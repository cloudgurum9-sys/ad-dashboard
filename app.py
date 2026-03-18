import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import os
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# --- 1. 산업별 통합 데이터베이스 (영업현금흐름 OCF 추가) ---
# 실제 2024~2025 예상치 및 실적 경향 반영
INDUSTRY_DATA = {
    "광고업": {
        "companies": {"제일기획": "030000.KS", "이노션": "214320.KS", "나스미디어": "089600.KQ", "에코마케팅": "230360.KQ", "인크로스": "216050.KQ"},
        "finance": {
            "기업명": ["제일기획", "이노션", "나스미디어", "에코마케팅", "인크로스"],
            "매출액(억)": [42000, 18000, 1500, 3500, 600],
            "영업이익(억)": [3100, 1500, 300, 600, 150],
            "영업현금흐름(억)": [3500, 1600, 280, 650, 160], # OCF는 대개 영업이익보다 큼(감가상각비 등 영향)
            "부채비율(%)": [110, 80, 45, 35, 25],
            "ROE(%)": [15.2, 10.5, 12.8, 18.5, 14.1]
        }
    },
    "반도체": {
        "companies": {"삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "한미반도체": "042700.KS", "HPSP": "403870.KQ"},
        "finance": {
            "기업명": ["삼성전자", "SK하이닉스", "한미반도체", "HPSP"],
            "매출액(억)": [2580000, 440000, 5767, 2164],
            "영업이익(억)": [650000, 270000, 2514, 1182],
            "영업현금흐름(억)": [820000, 350000, 2800, 1300],
            "부채비율(%)": [25, 55, 15, 10],
            "ROE(%)": [8.2, 15.5, 12.0, 35.5]
        }
    },
    "게임": {
        "companies": {"컴투스": "078340.KQ", "크래프톤": "259960.KS", "넷마블": "251270.KS", "엔씨소프트": "036570.KS", "카카오게임즈": "293490.KQ"},
        "finance": {
            "기업명": ["컴투스", "크래프톤", "넷마블", "엔씨소프트", "카카오게임즈"],
            "매출액(억)": [7000, 27098, 26638, 15069, 7388],
            "영업이익(억)": [190, 11825, 3525, 161, -396],
            "영업현금흐름(억)": [450, 13500, 4200, 1200, 200],
            "부채비율(%)": [45, 15, 65, 35, 50],
            "ROE(%)": [2.5, 22.1, 5.5, 1.2, -5.2]
        }
    },
    "타이어": {
        "companies": {"한국타이어앤테크놀로지": "161390.KS", "금호타이어": "073240.KS", "넥센타이어": "002350.KS"},
        "finance": {
            "기업명": ["한국타이어앤테크놀로지", "금호타이어", "넥센타이어"],
            "매출액(억)": [212022, 41000, 27000],
            "영업이익(억)": [18425, 3800, 1800],
            "영업현금흐름(억)": [22000, 4500, 2400],
            "부채비율(%)": [75, 210, 150],
            "ROE(%)": [12.5, 15.2, 8.5]
        }
    }
}

# --- 2. 폰트 및 페이지 설정 ---
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())

st.set_page_config(page_title="전문 재무 분석 대시보드", layout="wide")
st.title("📂 전문 재무 건전성 및 현금흐름 분석 포털")
st.markdown("> **회계팀 관점의 리스크 관리 도구: 이익의 질(Quality of Earnings) 분석**")

# --- 3. 사이드바 ---
selected_industry = st.sidebar.selectbox("📂 업종 선택", list(INDUSTRY_DATA.keys()))
current_data = INDUSTRY_DATA[selected_industry]
company_dict = current_data["companies"]

selected_names = st.sidebar.multiselect(
    f"🔍 {selected_industry} 기업 선택",
    options=list(company_dict.keys()),
    default=list(company_dict.keys())
)

# --- 4. 메인 분석 화면 ---
if selected_names:
    df_finance = pd.DataFrame(current_data["finance"])
    df_finance = df_finance[df_finance['기업명'].isin(selected_names)]
    
    # [A] 지표 자동 계산
    df_finance['영업이익률(%)'] = (df_finance['영업이익(억)'] / df_finance['매출액(억)'] * 100).round(2)
    # 핵심 회계 지표: 영업이익 대비 현금흐름 비율 (100% 이상일수록 이익의 질이 좋음)
    df_finance['현금창출력(%)'] = (df_finance['영업현금흐름(억)'] / df_finance['영업이익(억)'] * 100).round(1)

    # [B] 재무 데이터 테이블
    st.subheader(f"📑 {selected_industry} 심층 재무 지표")
    cols = ['기업명', '매출액(억)', '영업이익(억)', '영업현금흐름(억)', '현금창출력(%)', '부채비율(%)', 'ROE(%)']
    st.table(df_finance[cols].sort_values(by='현금창출력(%)', ascending=False))

    # [C] 현금흐름 vs 영업이익 시각화 (Plotly)
    st.subheader("📊 영업이익 vs 실제 현금유입 비교")
    fig_cf = px.bar(df_finance, x='기업명', y=['영업이익(억)', '영업현금흐름(억)'], 
                    barmode='group', title="이익의 질 분석 (영업이익 vs OCF)")
    st.plotly_chart(fig_cf, use_container_width=True)

    # [D] 주가 차트 및 뉴스 (이전 코드와 동일하되 깔끔하게 정리)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 주가 트렌드")
        selected_tickers = [company_dict[name] for name in selected_names]
        data = yf.download(selected_tickers, period="1y")['Close']
        if not data.empty:
            inv_map = {v: k for k, v in company_dict.items()}
            st.line_chart(data.rename(columns=inv_map))
    
    with col2:
        st.subheader("📰 최신 주요 뉴스")
        # 간단 뉴스 링크 버튼 제공
        for name in selected_names[:3]: # 상위 3개만 요약
            st.link_button(f"🔍 {name} 실시간 뉴스 보기", f"https://search.naver.com/search.naver?where=news&query={name}")

st.markdown("---")
st.caption("✅ **Update 2026-03-18**: 영업현금흐름(OCF) 및 이익의 질 분석 모듈 탑재 완료")
