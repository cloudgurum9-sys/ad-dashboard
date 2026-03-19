민준님, 알겠습니다! 가장 강력하게 적용되도록 수정한 최신 CSS 코드를 포함하여 전체 파이썬 코드를 다시 싹 정리했습니다.

기존 코드를 모두 지우시고, 아래 코드를 그대로 복사해서 붙여넣기 해보세요!

💻 [최종 완성된 파이썬 전체 코드 (동적 텍스트 강제 적용 버전)]
Python
import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from fpdf import FPDF

# --- 1. 산업별 통합 데이터베이스 (데이터 동일) ---
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

# --- 3. 대시보드 UI (UI/UX 개선 버전) ---
st.set_page_config(page_title="고급 재무 분석 대시보드", layout="wide", initial_sidebar_state="expanded")

# 🌟 [추가된 CSS 코드] st.metric 글씨 잘림 방지 및 Expander 동적 텍스트 (강제 적용)
st.markdown("""
<style>
/* 1. 지표(Metric) 제목 및 값 줄바꿈 허용 */
[data-testid="stMetricLabel"] {
    white-space: normal !important;
    word-break: keep-all !important;
    overflow: visible !important;
}
[data-testid="stMetricValue"] {
    white-space: normal !important;
    word-break: keep-all !important;
    overflow: visible !important;
    font-size: 1.8rem !important;
}

/* 2. Expander(펼치기) 동적 텍스트 (강제 적용) */
/* 닫혀있을 때 */
[data-testid="stExpander"] details:not([open]) summary::after {
    content: " (클릭하여 펼치기)" !important;
    color: #888888 !important;
    font-size: 14px !important;
    margin-left: 10px !important;
    font-weight: normal !important;
}
/* 열려있을 때 */
[data-testid="stExpander"] details[open] summary::after {
    content: " (클릭하여 닫기)" !important;
    color: #ff4b4b !important; 
    font-size: 14px !important;
    margin-left: 10px !important;
    font-weight: normal !important;
}
</style>
""", unsafe_allow_html=True)

# 상단 헤더
st.title("📊 산업별 재무분석 및 이익의 질 평가")
st.markdown("현금흐름, 듀퐁 분석, 다면 평가를 통해 기업의 숨겨진 재무적 가치를 발굴합니다.")
st.markdown("---")

# 사이드바
st.sidebar.header("⚙️ 분석 조건 설정")
selected_industry = st.sidebar.selectbox("📂 분석 업종 선택", list(INDUSTRY_DATA.keys()))
current_data = INDUSTRY_DATA[selected_industry]
company_dict = current_data["companies"]

selected_names = st.sidebar.multiselect(
    f"🔍 {selected_industry} 기업 선택",
    options=list(company_dict.keys()),
    default=list(company_dict.keys())
)

if selected_names:
    # 데이터 처리
    df_finance = pd.DataFrame(current_data["finance"])
    df_finance = df_finance[df_finance['기업명'].isin(selected_names)]
    df_finance['현금창출력(%)'] = (df_finance['영업현금흐름(억)'] / df_finance['영업이익(억)'] * 100).round(1)
    df_finance['재무레버리지(배)'] = (1 + (df_finance['부채비율(%)'] / 100)).round(2)
    
    # 🌟 [신규 UI] 상단 KPI 요약 (Top Metrics)
    top_roe_company = df_finance.loc[df_finance['ROE(%)'].idxmax()]
    top_cf_company = df_finance.loc[df_finance['현금창출력(%)'].idxmax()]
    avg_debt = df_finance['부채비율(%)'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("분석 대상 기업 수", f"{len(selected_names)}개")
    col2.metric("🏆 최고 ROE 기업", f"{top_roe_company['기업명']}", f"{top_roe_company['ROE(%)']}%")
    col3.metric("💰 최고 현금창출 기업", f"{top_cf_company['기업명']}", f"{top_cf_company['현금창출력(%)']}%")
    col4.metric("⚖️ 그룹 평균 부채비율", f"{avg_debt:.1f}%", delta_color="inverse")
    
    st.markdown("<br>", unsafe_allow_html=True) # 여백

    # PDF 다운로드 (우측 정렬 느낌)
    pdf_bytes = create_pdf_report(selected_industry, df_finance.sort_values(by='ROE(%)', ascending=False), font_path)
    col_empty, col_btn = st.columns([4, 1])
    with col_btn:
        st.download_button("📄 PDF 리포트 다운로드", data=pdf_bytes, file_name=f"{selected_industry}_리포트.pdf", mime="application/pdf", use_container_width=True)

    # 🌟 [신규 UI] 탭(Tab)으로 깔끔하게 레이아웃 분할
    tab1, tab2, tab3 = st.tabs(["📑 심층 재무 & 듀퐁 분석", "🕸️ 기업 다면 평가 (레이더)", "📈 주가 및 이익의 질"])

    with tab1:
        # 데이터 테이블 (Expander로 숨김 기능 - 파이썬 텍스트 완전 제거 완료)
        with st.expander("📊 세부 재무 데이터 표 보기", expanded=False):
            cols = ['기업명', '매출액(억)', '영업이익(억)', '현금창출력(%)', '부채비율(%)', 'ROE(%)']
            st.dataframe(df_finance[cols].sort_values(by='ROE(%)', ascending=False), use_container_width=True, hide_index=True)
            
        st.subheader("🔬 듀퐁 분석 (DuPont Analysis): ROE 원인 분해")
        fig_dupont = go.Figure()
        fig_dupont.add_trace(go.Bar(x=df_finance['기업명'], y=df_finance['순이익률(%)'], name='수익성 (순이익률 %)', marker_color='#1f77b4'))
        fig_dupont.add_trace(go.Bar(x=df_finance['기업명'], y=df_finance['총자산회전율(배)']*10, name='활동성 (회전율x10)', marker_color='#ff7f0e'))
        fig_dupont.add_trace(go.Bar(x=df_finance['기업명'], y=df_finance['재무레버리지(배)'], name='재무구조 (레버리지 배)', marker_color='#2ca02c'))
        fig_dupont.update_layout(barmode='group', template='plotly_white', legend=dict(orientation="h", y=1.1), margin=dict(t=20))
        st.plotly_chart(fig_dupont, use_container_width=True)

    with tab2:
        st.subheader("🕸️ 육각형 기업 분석 (Radar Chart)")
        st.write("기업의 5가지 핵심 재무 역량을 상대 평가하여 강점과 약점을 파악합니다.")
        categories = ['수익성(순이익률)', '활동성(자산회전율x100)', '안정성(100-부채비율/2)', '현금창출력(%)', 'ROE(%)']
        fig_radar = go.Figure()
        for name in selected_names:
            row = df_finance[df_finance['기업명'] == name].iloc[0]
            values = [row['순이익률(%)'] * 2.5, row['총자산회전율(배)'] * 80, (200 - row['부채비율(%)']) / 2, row['현금창출력(%)'] / 1.5, row['ROE(%)'] * 2]
            values.append(values[0])
            categories_closed = categories + [categories[0]]
            fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories_closed, fill='toself', name=name))
        
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
            legend=dict(orientation="h", y=1.1),
            template='plotly_white', margin=dict(t=20, b=20)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with tab3:
        col1_t3, col2_t3 = st.columns(2)
        with col1_t3:
            st.subheader("📈 주가 흐름 (최근 1년)")
            selected_tickers = [company_dict[name] for name in selected_names]
            stock_data = yf.download(selected_tickers, period="1y")['Close']
            if not stock_data.empty:
                plot_df = stock_data.rename(columns={v: k for k, v in company_dict.items()})
                fig_stock = px.line(plot_df)
                fig_stock.update_layout(showlegend=False, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig_stock, use_container_width=True)
                
        with col2_t3:
            st.subheader("📊 이익의 질 (장부상 이익 vs 실제 현금)")
            fig_cf = px.bar(df_finance, x='기업명', y=['영업이익(억)', '영업현금흐름(억)'], barmode='group', color_discrete_sequence=['#83c9ff', '#182433'])
            fig_cf.update_layout(legend=dict(orientation="h", y=1.1), margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_cf, use_container_width=True)

st.markdown("---")
st.caption("✅ **최종 빌드 완료**: UI/UX 최적화 및 레이아웃 모듈화 탑재 (Metric 줄바꿈 및 강제 동적 텍스트 적용)")
