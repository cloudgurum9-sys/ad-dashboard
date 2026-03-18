아니요, 민준님! 단순하게 맨 뒤에 붙여넣으면 코드가 엉켜서 또 에러가 날 수 있어요.

현재 구조를 **'업종 선택형'**으로 완전히 바꾸려면, 기존의 광고업 데이터를 지우고 그 자리에 **'데이터 사전(Dictionary)'**을 넣은 뒤, 사용자가 선택한 업종의 데이터를 꺼내 쓰도록 코드를 살짝 재배치해야 합니다.

민준님이 그대로 복사해서 쓸 수 있게 **[업종 확장형 최종 코드]**를 다시 짜왔습니다. 반도체 업종까지 예시로 넣어두었으니, 이제 이 코드로 app.py를 싹 교체해 보세요!

🚀 [확장형] 대한민국 주요 산업 분석 포털 (app.py)
Python
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests
from bs4 import BeautifulSoup

# --- 1. 데이터 베이스 확장 (업종 추가하고 싶을 때 여기만 수정하세요!) ---
INDUSTRY_DATA = {
    "광고업": {
        "companies": {"제일기획": "030000.KS", "이노션": "214320.KS", "나스미디어": "089600.KQ", "에코마케팅": "230360.KQ", "인크로스": "216050.KQ"},
        "finance": {
            "기업명": ["제일기획", "이노션", "나스미디어", "에코마케팅", "인크로스"],
            "매출액(억)": [42000, 18000, 1500, 3500, 600],
            "영업이익(억)": [3100, 1500, 300, 600, 150]
        }
    },
    "반도체": {
        "companies": {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", "HPSP": "403870.KQ"},
        "finance": {
            "기업명": ["삼성전자", "SK하이닉스", "한미반도체", "HPSP"],
            "매출액(억)": [2580000, 440000, 1590, 1700],
            "영업이익(억)": [65000, 27000, 350, 950]
        }
    }
}

# --- 2. 핵심 함수들 ---
@st.cache_data(ttl=1800)
def get_company_news_final(company_name):
    results = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"}
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={company_name}&sort=1"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            news_items = soup.select(".news_tit")
            for item in news_items[:5]:
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
st.set_page_config(page_title="산업별 재무 분석 포털", layout="wide")

st.title("📊 대한민국 주요 산업 분석 대시보드")
st.markdown("---")

# --- 3. 사이드바 (업종 선택 로직) ---
st.sidebar.header("📂 업종 및 기업 선택")

# [업종 선택 박스]
selected_industry = st.sidebar.selectbox("1. 분석 업종 선택", list(INDUSTRY_DATA.keys()))

# 선택된 업종의 데이터만 필터링
current_industry = INDUSTRY_DATA[selected_industry]
company_dict = current_industry["companies"]

# [기업 선택 멀티셀렉트]
selected_names = st.sidebar.multiselect(
    f"2. {selected_industry} 기업 선택",
    options=list(company_dict.keys()),
    default=list(company_dict.keys())
)

# --- 4. 메인 화면 대시보드 출력 ---
if not selected_names:
    st.warning("분석할 기업을 선택해 주세요!")
else:
    selected_tickers = [company_dict[name] for name in selected_names]
    
    # [A] 수익성 지표 출력
    st.subheader(f"💰 {selected_industry} 수익성 지표 (2025 예상)")
    finance_raw = current_industry["finance"]
    df_finance = pd.DataFrame(finance_raw)
    
    # 선택된 기업만 필터링 후 영업이익률 계산
    df_finance = df_finance[df_finance['기업명'].isin(selected_names)]
    df_finance['영업이익률(%)'] = (df_finance['영업이익(억)'] / df_finance['매출액(억)'] * 100).round(2)
    st.table(df_finance.sort_values(by='영업이익률(%)', ascending=False))

    # [B] 주가 차트
    st.subheader(f"📈 {selected_industry} 최근 1년 주가 흐름")
    with st.spinner('차트를 불러오는 중...'):
        stock_df = get_stock_data(selected_tickers)
        if not stock_df.empty:
            st.line_chart(stock_df)

    # [C] 실시간 뉴스
    st.markdown("---")
    st.subheader(f"📰 {selected_industry} 최신 이슈")
    tabs = st.tabs(selected_names)
    for i, name in enumerate(selected_names):
        with tabs[i]:
            news_list = get_company_news_final(name)
            if news_list:
                for news in news_list:
                    st.write(f"🔗 [{news['title']}]({news['link']})")
            else:
                st.write(f"⚠️ '{name}' 뉴스를 불러오지 못했습니다.")
                naver_link = f"https://search.naver.com/search.naver?where=news&query={name}"
                st.link_button(f"👉 네이버에서 '{name}' 뉴스 직접 보기", naver_link)

st.markdown("---")
st.caption(f"✅ Update: {selected_industry} 데이터 분석 모듈 가동 중 | 2026-03-18")
