import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px # <-- Plotly 추가
import requests
from bs4 import BeautifulSoup
import os

# --- 1. 데이터 베이스 확장 (부채비율, ROE 지표 추가) ---
INDUSTRY_DATA = {
    "광고업": {
        "companies": {"제일기획": "030000.KS", "이노션": "214320.KS", "나스미디어": "089600.KQ", "에코마케팅": "230360.KQ", "인크로스": "216050.KQ"},
        "finance": {
            "기업명": ["제일기획", "이노션", "나스미디어", "에코마케팅", "인크로스"],
            "매출액(억)": [42000, 18000, 1500, 3500, 600],
            "영업이익(억)": [3100, 1500, 300, 600, 150],
            "부채비율(%)": [110, 80, 45, 35, 25], # 예시 수치
            "ROE(%)": [15.2, 10.5, 12.8, 18.5, 14.1]
        }
    },
    "반도체": {
        "companies": {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", "HPSP": "403870.KQ"},
        "finance": {
            "기업명": ["삼성전자", "SK하이닉스", "한미반도체", "HPSP"],
            "매출액(억)": [2580000, 440000, 1590, 1700],
            "영업이익(억)": [65000, 27000, 350, 950],
            "부채비율(%)": [25, 55, 15, 10],
            "ROE(%)": [8.2, 5.5, 12.0, 35.5]
        }
    },
    "게임": {
        "companies": {"컴투스": "078340.KQ", "크래프톤": "259960.KS", "넷마블": "251270.KS", "엔씨소프트": "036570.KS", "카카오게임즈": "293490.KQ"},
        "finance": {
            "기업명": ["컴투스", "크래프톤", "넷마블", "엔씨소프트", "카카오게임즈"],
            "매출액(억)": [6938, 27098, 26638, 15781, 7388],
            "영업이익(억)": [24, 11825, 2156, -1092, 65],
            "부채비율(%)": [45, 15, 65, 35, 50],
            "ROE(%)": [2.5, 22.1, 5.5, -3.2, 1.8]
        }
    },
    "타이어": {
        "companies": {"한국타이어앤테크놀로지": "161390.KS", "금호타이어": "073240.KS", "넥센타이어": "002350.KS"},
        "finance": {
            "기업명": ["한국타이어앤테크놀로지", "금호타이어", "넥센타이어"],
            "매출액(억)": [212022, 41000, 27000],
            "영업이익(억)": [18425, 3800, 1800],
            "부채비율(%)": [75, 210, 150],
            "ROE(%)": [12.5, 15.2, 8.5]
        }
    }
}

# --- 2. 핵심 함수 ---
@st.cache_data(ttl=1800)
def get_company_news_final(company_name):
    results = []
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={company_name}&sort=1"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            for item in soup.select(".news_tit")[:5]:
                results.append({"title": item.get_text(), "link": item.get("href")})
    except: pass
    return results

@st.cache_data(ttl=3600)
def get_stock_data(tickers):
    try:
        data = yf.download(tickers, period="1y")['Close']
        return data
    except: return pd.DataFrame()

# 폰트 및 페이지 설정
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
plt.rcParams['axes.unicode_minus'] = False
st.set_page_config(page_title="재무 건전성 분석 포털", layout="wide")

st.title("📊 산업별 재무 건전성 & 수익성 대시보드")
st.write("회계팀 관점에서의 다각도 기업 분석 도구입니다.")
st.markdown("---")

# --- 3. 사이드바 인터페이스 ---
st.sidebar.header("⚙️ 분석 설정")
selected_industry = st.sidebar.selectbox("1단계: 산업군 선택", list(INDUSTRY_DATA.keys()))
current_data = INDUSTRY_DATA[selected_industry]
company_dict = current_data["companies"]

selected_names = st.sidebar.multiselect(
    f"2단계: {selected_industry} 기업 선택",
    options=list(company_dict.keys()),
    default=list(company_dict.keys())
)

# --- 4. 대시보드 출력 ---
if not selected_names:
    st.info("비교할 기업을 선택해 주세요.")
else:
    selected_tickers = [company_dict[name] for name in selected_names]
    
    # [A] 재무 지표 비교 (부채비율, ROE 포함)
    st.subheader(f"📑 {selected_industry} 핵심 재무 지표 비교")
    df_finance = pd.DataFrame(current_data["finance"])
    df_finance = df_finance[df_finance['기업명'].isin(selected_names)]
    
    # 영업이익률 추가 계산
    df_finance['영업이익률(%)'] = (df_finance['영업이익(억)'] / df_finance['매출액(억)'] * 100).round(2)
    
    # 컬럼 순서 재배치 (보기 좋게)
    cols = ['기업명', '매출액(억)', '영업이익(억)', '영업이익률(%)', '부채비율(%)', 'ROE(%)']
    st.table(df_finance[cols].sort_values(by='ROE(%)', ascending=False))

    # [B] 주가 차트 (Plotly로 업그레이드!)
    st.subheader(f"📈 {selected_industry} 주가 트렌드 (1년)")
    stock_df = get_stock_data(selected_tickers)
    
    if not stock_df.empty:
        # 데이터 정제: yfinance 데이터는 컬럼이 티커(030000.KS)로 되어있어서 기업명으로 바꿔줍니다.
        # 티커와 기업명 매핑용 사전 생성
        inv_company_dict = {v: k for k, v in company_dict.items()}
        
        # 컬럼명을 티커에서 한글 기업명으로 변경
        plot_df = stock_df.rename(columns=inv_company_dict)
        
        # Plotly를 이용한 인터랙티브 라인 차트
        fig = px.line(plot_df, 
                      labels={"value": "주가 (원)", "date": "날짜", "variable": "기업명"},
                      template="plotly_white") # 깔끔한 흰색 배경
        
        # 그래프 디자인 살짝 가미
        fig.update_layout(
            hovermode="x unified", # 마우스 갖다대면 모든 기업 수치 한꺼번에 노출
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), # 범례를 상단에 배치
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    # [C] 실시간 뉴스 탭
    st.markdown("---")
    st.subheader(f"📰 {selected_industry} 최신 주요 이슈")
    tabs = st.tabs(selected_names)
    for i, name in enumerate(selected_names):
        with tabs[i]:
            news_list = get_company_news_final(name)
            if news_list:
                for news in news_list:
                    st.write(f"🔗 [{news['title']}]({news['link']})")
            else:
                st.info(f"'{name}' 뉴스를 가져오는 중입니다.")
                st.link_button(f"🔍 네이버 뉴스 직접 보기", f"https://search.naver.com/search.naver?where=news&query={name}")

st.markdown("---")
st.caption("✅ **Update 2026-03-18**: 회계팀 취업용 재무 건전성 분석 모듈 추가 완료")
