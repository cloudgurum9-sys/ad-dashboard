import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import os
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fpdf import FPDF  # PDF 생성을 위한 라이브러리 추가

# --- 1. 산업별 통합 데이터베이스 ---
INDUSTRY_DATA = {
    "광고업": {
        "companies": {"제일기획": "030000.KS", "이노션": "214320.KS", "나스미디어": "089600.KQ", "에코마케팅": "230360.KQ", "인크로스": "216050.KQ"},
        "finance": {
            "기업명": ["제일기획", "이노션", "나스미디어", "에코마케팅", "인크로스"],
            "매출액(억)": [42000, 18000, 1500, 3500, 600],
            "영업이익(억)": [3100, 1500, 300, 600, 150],
            "영업현금흐름(억)": [3500, 1600, 280, 650, 160],
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

# --- 2. 기본 폰트 설정 ---
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())

# --- 3. PDF 리포트 생성 함수 ---
def create_pdf_report(industry, df, font_path):
    pdf = FPDF()
    pdf.add_page()
    
    # 한글 폰트 적용 (에러 방지용 Fallback 포함)
    if os.path.exists(font_path):
        pdf.add_font("NanumGothic", "", font_path)
        pdf.set_font("NanumGothic", "", 16)
    else:
        pdf.set_font("Helvetica", "", 16)
        
    # 제목 작성
    pdf.cell(0, 10, f"[{industry}] Financial Health & Cash Flow Report", ln=True, align='C')
    pdf.ln(10)
    
    # 본문 폰트 크기 변경
    if os.path.exists(font_path):
        pdf.set_font("NanumGothic", "", 11)
    
    # 데이터 순회하며 PDF에 작성
    for index, row in df.iterrows():
        pdf.cell(0, 8, f"▶ 기업명: {row['기업명']}", ln=True)
        pdf.cell(0, 8, f"   - 매출액: {row['매출액(억)']}억 | 영업이익: {row['영업이익(억)']}억 | 현금흐름(OCF): {row['영업현금흐름(억)']}억", ln=True)
        pdf.cell(0, 8, f"   - 현금창출력: {row['현금창출력(%)']}% | 부채비율: {row['부채비율(%)']}% | ROE: {row['ROE(%)']}%", ln=True)
        pdf.ln(5) # 간격 띄우기
        
    # PDF를 byte 형태로 반환
    return bytes(pdf.output())

# --- 4. 대시보드 UI ---
st.set_page_config(page_title="전문 재무 분석 대시보드", layout="wide")
st.title("📊 산업별 재무분석 및 이익의 질(Quality of Earnings)")
st.markdown("---")

selected_industry = st.sidebar.selectbox("📂 분석 업종 선택", list(INDUSTRY_DATA.keys()))
current_data = INDUSTRY_DATA[selected_industry]
company_dict = current_data["companies"]

selected_names = st.sidebar.multiselect(
    f"🔍 {selected_industry} 기업 선택",
    options=list(company_dict.keys()),
    default=list(company_dict.keys())
)

if selected_names:
    df_finance = pd.DataFrame(current_data["finance"])
    df_finance = df_finance[df_finance['기업명'].isin(selected_names)]
    df_finance['영업이익률(%)'] = (df_finance['영업이익(억)'] / df_finance['매출액(억)'] * 100).round(2)
    df_finance['현금창출력(%)'] = (df_finance['영업현금흐름(억)'] / df_finance['영업이익(억)'] * 100).round(1)

    # [다운로드 버튼 영역 추가]
    st.subheader(f"📑 {selected_industry} 심층 재무 분석")
    
    # PDF 생성 및 다운로드 버튼
    pdf_bytes = create_pdf_report(selected_industry, df_finance.sort_values(by='현금창출력(%)', ascending=False), font_path)
    st.download_button(
        label="📄 PDF 리포트 다운로드",
        data=pdf_bytes,
        file_name=f"{selected_industry}_재무분석_리포트.pdf",
        mime="application/pdf"
    )

    # 테이블 출력
    cols = ['기업명', '매출액(억)', '영업이익(억)', '영업현금흐름(억)', '현금창출력(%)', '부채비율(%)', 'ROE(%)']
    st.table(df_finance[cols].sort_values(by='현금창출력(%)', ascending=False))

    # 차트 출력
    st.subheader("📊 이익의 질 분석 (영업이익 vs 실제현금흐름)")
    fig_cf = px.bar(df_finance, x='기업명', y=['영업이익(억)', '영업현금흐름(억)'], barmode='group', template='plotly_white')
    st.plotly_chart(fig_cf, use_container_width=True)

    st.subheader("📈 최근 1년 주가 트렌드 비교")
    selected_tickers = [company_dict[name] for name in selected_names]
    stock_data = yf.download(selected_tickers, period="1y")['Close']
    if not stock_data.empty:
        inv_map = {v: k for k, v in company_dict.items()}
        plot_df = stock_data.rename(columns=inv_map)
        fig_stock = px.line(plot_df, labels={"value": "주가 (원)", "Date": "날짜", "variable": "기업명"})
        fig_stock.update_layout(hovermode="x unified")
        st.plotly_chart(fig_stock, use_container_width=True)

st.markdown("---")
st.caption("✅ **Update 2026-03-18**: 현금흐름 분석 및 PDF 자동 리포팅 모듈 탑재")
