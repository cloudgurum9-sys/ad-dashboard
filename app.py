import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import requests  # 뉴스 호출용
from bs4 import BeautifulSoup  # 뉴스 파싱용

# 1. 뉴스 가져오기 함수 (캐싱 적용: 30분마다 업데이트)
@st.cache_data(ttl=1800)
def get_recent_news(company_name):
    try:
        url = f"https://search.naver.com/search.naver?where=news&query={company_name}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        news_items = soup.select(".news_tit")[:5] # 최신 뉴스 5개만
        results = []
        for item in news_items:
            results.append({"title": item.get("title"), "link": item.get("href")})
        return results
    except:
        return []

# ... (기존 폰트 설정 및 페이지 설정 코드 동일) ...

# --- 데이터 출력 부분 (주가 차트 아래에 추가하세요) ---

if selected_names:
    # (기존 주가 차트 코드 아래에 이어서 작성)
    
    st.markdown("---")
    st.subheader("📰 선택 기업 최신 뉴스 요약")
    
    # 선택된 기업별로 탭을 나눠서 뉴스를 보여줍니다.
    if len(selected_names) > 0:
        tabs = st.tabs(selected_names)
        for i, tab in enumerate(tabs):
            with tab:
                company = selected_names[i]
                news_list = get_recent_news(company)
                if news_list:
                    for news in news_list:
                        st.write(f"🔗 [{news['title']}]({news['link']})")
                else:
                    st.write("최근 뉴스를 불러올 수 없습니다.")
