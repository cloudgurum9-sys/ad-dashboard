import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# 1. 캐싱 설정: 데이터를 한 번 불러오면 1시간(3600초) 동안 저장해서 속도를 높입니다.
@st.cache_data(ttl=3600)
def get_stock_data(tickers):
    data = yf.download(tickers, period="1y")['Close']
    return data

# 한글 폰트 설정 (어제 설정한 나눔고딕 활용)
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(page_title="광고업 재무 분석 대시보드", layout="wide")

st.title("🚀 광고업 주요 기업 재무 & 주가 분석")
st.markdown("---")

# 2. 사이드바 필터 추가: 사용자가 직접 기업을 선택하게 만듭니다.
st.sidebar.header("🔍 분석 설정")
companies = {
    "제일기획": "030000.KS",
    "이노션": "214320.KS",
    "나스미디어": "089600.KQ",
    "에코마케팅": "230360.KQ",
    "인크로스": "216050.KQ"
}

selected_names = st.sidebar.multiselect(
    "비교할 기업을 선택하세요",
    options=list(companies.keys()),
    default=list(companies.keys())
)

# 선택된 기업이 없을 때의 예외 처리
if not selected_names:
    st.warning("분석할 기업을 최소 하나 이상 선택해 주세요!")
else:
    selected_tickers = [companies[name] for name in selected_names]

    # 데이터 로드 (캐싱 적용됨)
    with st.spinner('데이터를 불러오는 중입니다...'):
        try:
            stock_df = get_stock_data(selected_tickers)
            
            # 3. 수익성 지표 계산 (예시 데이터)
            # 실제로는 DART API를 써야 하지만, 우선 구조를 보여드리기 위해 
            # 2025년 가상 영업이익률 데이터를 표로 보여줍니다.
            st.subheader("📊 기업별 수익성 지표 (2025 예상)")
            
            # 수익성 지표 계산식: (영업이익 / 매출) * 100
            analysis_data = {
                "기업명": ["제일기획", "이노션", "나스미디어", "에코마케팅", "인크로스"],
                "매출액(억)": [42000, 18000, 1500, 3500, 600],
                "영업이익(억)": [3100, 1500, 300, 600, 150]
            }
            df_finance = pd.DataFrame(analysis_data)
            df_finance = df_finance[df_finance['기업명'].isin(selected_names)]
            
            # 영업이익률 계산 루틴
            df_finance['영업이익률(%)'] = (df_finance['영업이익(억)'] / df_finance['매출액(억)'] * 100).round(2)
            
            # 대시보드에 표 출력
            st.table(df_finance.sort_values(by='영업이익률(%)', ascending=False))

            # 주가 차트 출력
            st.subheader("📈 최근 1년 주가 흐름 비교")
            st.line_chart(stock_df)

        except Exception as e:
            st.error(f"⚠️ 현재 외부 데이터 서버가 불안정합니다. 잠시 후 다시 시도해 주세요. (에러: {e})")

# 하단 업데이트 기록 (버전 관리)
st.markdown("---")
st.caption("✅ Update 2026-03-18: 캐싱 시스템 도입 및 기업별 영업이익률 분석 기능 추가")
