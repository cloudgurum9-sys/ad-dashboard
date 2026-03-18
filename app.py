민준님, 탁월한 선택입니다!

회계/재무팀은 수많은 숫자를 다루지만, 최종 보고는 언제나 "비전문가인 경영진이나 타 부서도 한눈에 이해할 수 있게" 해야 합니다.  **레이더 차트(Radar Chart)**는 기업의 강점과 약점을 마치 '게임 캐릭터 능력치'처럼 직관적으로 보여주기 때문에, 민준님의 **'데이터 시각화 및 의사소통 역량'**을 극적으로 어필할 수 있는 최고의 도구입니다.

이미 대시보드에 모든 데이터가 준비되어 있으니, Plotly의 Scatterpolar 기능을 활용해 레이더 차트를 멋지게 띄워보겠습니다.

1️⃣ app.py 전체 코드 (육각형 기업 분석: 레이더 차트 탑재)
기존 코드에 **기업별 재무 캐릭터 육각형(방사형그래프)**을 그리는 함수와 시각화 섹션을 추가했습니다. 전체를 복사해서 덮어쓰기 하세요!

Python
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import os
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fpdf import FPDF

# --- 1. 산업별 통합 데이터베이스 (데이터는 이전과 동일) ---
INDUSTRY_DATA = {
    "광고업": {
        "companies": {"제일기획": "030000.KS", "이노션": "214320.KS", "나스미디어": "089600.KQ", "에코마케팅": "230360.KQ", "인크로스": "216050.KQ"},
        "finance": {
            "기업명": ["제일기획", "이노션", "나스미디어", "에코마케팅", "인크로스"],
            "매출액(억)": [42000, 18000, 1500, 3500, 600],
            "영업이익(억)": [3100, 1500, 300, 600, 150],
            "영업현금흐름(억)": [3500, 1600, 280, 650, 160],
            "부채비율(%)": [110, 80, 45, 35, 25],
            "순이익률(%)": [6.5, 5.8, 12.0, 14.5, 11.0],
            "총자산회전율(배)": [1.11, 1.0, 0.73, 0.94, 1.02],
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
            "순이익률(%)": [12.5, 15.0, 38.0, 42.0],
            "총자산회전율(배)": [0.52, 0.65, 0.27, 0.76],
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
            "순이익률(%)": [2.1, 35.0, 4.0, 1.5, -4.5],
            "총자산회전율(배)": [0.82, 0.55, 0.83, 0.59, 0.60],
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
            "순이익률(%)": [7.5, 4.2, 3.5],
            "총자산회전율(배)": [0.95, 1.15, 0.97],
            "ROE(%)": [12.5, 15.2, 8.5]
        }
    }
}

# --- 2. 기본 설정 및 리포트 함수 ---
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
if os.path.exists(font_path):
    font_prop = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font_prop.get_name())

def create_pdf_report(industry, df, font_path):
    pdf = FPDF()
    pdf.add_page()
    if os.path.exists(font_path):
        pdf.add_font("NanumGothic", "", font_path)
        pdf.set_font("NanumGothic", "", 16)
    else:
        pdf.set_font("Helvetica", "", 16)
        
    pdf.cell(0, 10, f"[{industry}] Financial Health & DuPont Analysis", ln=True, align='C')
    pdf.ln(10)
    
    if os.path.exists(font_path):
        pdf.set_font("NanumGothic", "", 11)
    
    for index, row in df.iterrows():
        pdf.cell(0, 8, f"▶ {row['기업명']}", ln=True)
        pdf.cell(0, 8, f"   - 이익 및 현금: 매출 {row['매출액(억)']}억 | 현금창출력 {row['현금창출력(%)']}%", ln=True)
        pdf.cell(0, 8, f"   - 듀퐁 분석(ROE {row['ROE(%)']}%): 순이익률 {row['순이익률(%)']}% | 자산회전율 {row['총자산회전율(배)']}배 | 재무레버리지 {row['재무레버리지(배)']}배", ln=True)
        pdf.ln(5)
    return bytes(pdf.output())

# --- 3. 대시보드 UI ---
st.set_page_config(page_title="고급 재무 분석 대시보드", layout="wide")
st.title("📊 산업별 고급 재무분석 (현금흐름 & 듀퐁 분석 & 육각형 기업)")
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
    
    # 지표 자동 계산
    df_finance['현금창출력(%)'] = (df_finance['영업현금흐름(억)'] / df_finance['영업이익(억)'] * 100).round(1)
    df_finance['재무레버리지(배)'] = (1 + (df_finance['부채비율(%)'] / 100)).round(2)

    # [PDF 다운로드]
    pdf_bytes = create_pdf_report(selected_industry, df_finance.sort_values(by='ROE(%)', ascending=False), font_path)
    st.download_button("📄 분석 리포트 다운로드 (PDF)", data=pdf_bytes, file_name=f"{selected_industry}_듀퐁분석.pdf", mime="application/pdf")

    # [A] 심층 재무 테이블
    st.subheader(f"📑 {selected_industry} 핵심 지표")
    cols = ['기업명', '매출액(억)', '영업이익(억)', '현금창출력(%)', '부채비율(%)', 'ROE(%)']
    st.table(df_finance[cols].sort_values(by='ROE(%)', ascending=False))

    # [B] 레이더 차트 (육각형 기업 분석) 시각화 섹션 추가
    st.markdown("---")
    st.subheader("🕸️ 육각형 기업 분석 (Radar Chart): 다면적 역량 평가")
    st.write("선택한 기업들의 **수익성, 활동성, 안정성, 현금창출력, 성장성**을 거미줄 그래프로 한눈에 비교합니다.")
    
    # 레이더 차트용 데이터 정제 (스케일링 - 0~100 사이로 변환)
    categories = ['수익성(순이익률)', '활동성(자산회전율x100)', '안정성(100-부채비율/2)', '현금창출력(%)', 'ROE(%)']
    
    fig_radar = go.Figure()
    
    for name in selected_names:
        row = df_finance[df_finance['기업명'] == name].iloc[0]
        # 스케일링 로직: 시각화를 위해 대략적인 범위를 0~100으로 맞춤
        values = [
            row['순이익률(%)'] * 2.5,        # 예: 순이익률 40% -> 100점
            row['총자산회전율(배)'] * 80,    # 예: 자산회전율 1.25배 -> 100점
            (200 - row['부채비율(%)']) / 2,   # 예: 부채비율 0% -> 100점, 200% -> 0점
            row['현금창출력(%)'] / 1.5,     # 예: 현금창출력 150% -> 100점
            row['ROE(%)'] * 2               # 예: ROE 50% -> 100점
        ]
        
        # 그래프를 닫기 위해 첫 번째 값을 마지막에 추가
        values.append(values[0])
        categories_closed = categories + [categories[0]]
        
        fig_radar.add_trace(go.Scatterpolar(
            r=values,
            theta=categories_closed,
            fill='toself',
            name=name
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100]) # 레이더 차트의 범위 설정
        ),
        legend=dict(orientation="h", y=1.1),
        template='plotly_white'
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    # [C] 듀퐁 분석 시각화 (하이라이트!)
    st.markdown("---")
    st.subheader("🔬 듀퐁 분석 (DuPont Analysis): ROE 분해")
    st.write("ROE가 높은 원인이 **수익성(마진)** 때문인지, **활동성(자산회전)** 때문인지, **레버리지(부채)** 때문인지 분석합니다.")
    
    fig_dupont = go.Figure()
    fig_dupont.add_trace(go.Bar(x=df_finance['기업명'], y=df_finance['순이익률(%)'], name='수익성 (순이익률 %)', marker_color='#1f77b4'))
    fig_dupont.add_trace(go.Bar(x=df_finance['기업명'], y=df_finance['총자산회전율(배)']*10, name='활동성 (회전율x10)', marker_color='#ff7f0e'))
    fig_dupont.add_trace(go.Bar(x=df_finance['기업명'], y=df_finance['재무레버리지(배)'], name='재무구조 (레버리지 배)', marker_color='#2ca02c'))
    
    fig_dupont.update_layout(barmode='group', template='plotly_white', legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_dupont, use_container_width=True)

    # [D] 주가 차트 생략 없이 깔끔하게 배치
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📈 주가 흐름 (1년)")
        selected_tickers = [company_dict[name] for name in selected_names]
        stock_data = yf.download(selected_tickers, period="1y")['Close']
        if not stock_data.empty:
            plot_df = stock_data.rename(columns={v: k for k, v in company_dict.items()})
            fig_stock = px.line(plot_df)
            fig_stock.update_layout(showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_stock, use_container_width=True)
            
    with col2:
        st.subheader("📊 이익의 질 (이익 vs 현금)")
        fig_cf = px.bar(df_finance, x='기업명', y=['영업이익(억)', '영업현금흐름(억)'], barmode='group')
        fig_cf.update_layout(legend=dict(orientation="h", y=1.1), margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_cf, use_container_width=True)

st.markdown("---")
st.caption("✅ **Update 2026-03-18**: 레이더 차트(육각형 기업 분석) 시각화 탑재 완료")
