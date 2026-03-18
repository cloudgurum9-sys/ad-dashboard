# [최종본] 광고업 재무 & 뉴스 분석 대시보드
import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests
from bs4 import BeautifulSoup

# 1. 뉴스 가져오기 함수
@st.cache_data(ttl=1800)
def get_recent_news(company_name):
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={company_name}&sort=1"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.text, "html.parser")
        news_items = soup.find_all("a", class_="news_tit")
        results = []
        for item in news_items[:5]:
            title = item.get("title") if item.get("title") else item.get_text()
            link = item.get("href")
            results.append({"title": title, "link": link})
        return results
    except:
        return []

# 2. 주가 데이터 로딩 함수
@st.cache_data(ttl=3600)
def get_stock_data(tickers):
    data = yf.download(tickers, period="1y")['Close']
    return data

# 한글 폰트 설정
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())
plt.rcParams['axes.unicode_minus'] = False

# 페이지 설정
st.set_page_config(page_title="광고업 재무 분석 대시보드", layout="wide")

st.title("🚀 광고업 주요 기업 재무 & 주가 분석")
st.markdown("---")

# 3. 사이드바 설정
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

if not selected_names:
    st.warning("분석할 기업을 최소 하나 이상 선택해 주세요!")
else:
    selected_tickers = [companies[name] for name in selected_names]

    with st.spinner('데이터를 분석 중입니다...'):
        try:
            # 수익성 지표
            st.subheader("📊 기업별 수익성 지표 (2025 예상)")
            analysis_data = {
                "기업명": ["제일기획", "이노션", "나스미디어", "에코마케팅", "인크로스"],
                "매출액(억)": [42000, 18000, 1500, 3500, 600],
                "영업이익(억)": [3100, 1500, 300, 600, 150]
            }
            df_finance = pd.DataFrame(analysis_data)
            df_finance = df_finance[df_finance['기업명'].isin(selected_names)]
            df_finance['영업이익률(%)'] = (df_finance['영업이익(억)'] / df_finance['매출액(억)'] * 100).round(2)
            st.table(df_finance.sort_values(by='영업이익률(%)', ascending=False))

            # 주가 차트
            st.subheader("📈 최근 1년 주가 흐름 비교")
            stock_df = get_stock_data(selected_tickers)
            st.line_chart(stock_df)

            # 실시간 뉴스
            st.markdown("---")
            st.subheader("📰 선택 기업 최신 뉴스 요약")
            tabs = st.tabs(selected_names)
            for i, tab in enumerate(tabs):
                with tab:
                    c_name = selected_names[i]
                    news_list = get_recent_news(c_name)
                    if news_list:
                        for news in news_list:
                            st.write(f"🔗 [{news['title']}]({news['link']})")
                    else:
                        st.info(f"'{c_name}' 뉴스를 가져오는 중입니다...")

        except Exception as e:
            st.error(f"⚠️ 시스템 오류: {e}")

st.markdown("---")
st.caption("✅ Update 2026-03-18: 최종 기능 통합 완료")
