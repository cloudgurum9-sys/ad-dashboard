import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(page_title="경영관리/재무 분석 대시보드", page_icon="📊", layout="wide")

# 2. 가상 재무 데이터 생성 (마르헨제이 맞춤형)
@st.cache_data
def load_data():
    data = {
        '연도': ['2024', '2025', '2024', '2025', '2024', '2025'],
        '산업군': ['패션/이커머스', '패션/이커머스', '애슬레저/의류', '애슬레저/의류', '패션 플랫폼', '패션 플랫폼'],
        '기업명': ['알비이엔씨(마르헨제이)', '알비이엔씨(마르헨제이)', '브랜드엑스코퍼레이션', '브랜드엑스코퍼레이션', '무신사', '무신사'],
        '매출액': [350, 520, 2100, 2300, 7000, 9900],
        '당기순이익': [25, 45, 120, 150, -100, 300],
        '총자산': [180, 250, 1500, 1700, 12000, 15000],
        '자기자본': [80, 125, 800, 950, 6000, 6500],
        '영업활동현금흐름(OCF)': [30, 60, 140, 180, 500, 800]
    }
    return pd.DataFrame(data)

df = load_data()

# 3. 사이드바 설정
st.sidebar.header("🔍 분석 필터")

industry_list = df['산업군'].unique().tolist()
selected_industry = st.sidebar.selectbox("🏢 산업군 선택", industry_list, index=0)

filtered_companies = df[df['산업군'] == selected_industry]['기업명'].unique()
selected_company = st.sidebar.selectbox("🏢 기업 선택", filtered_companies)

company_data = df[df['기업명'] == selected_company].sort_values('연도').reset_index(drop=True)

# 4. 메인 대시보드 화면
st.title(f"📊 {selected_company} 경영관리 및 재무 분석 대시보드")
st.markdown("---")

if len(company_data) >= 2:
    current = company_data.iloc[-1]
    previous = company_data.iloc[-2]

    # --- Section 1: 실질 현금창출력 (OCF) 추적 ---
    st.subheader("1. 재무 분석: 영업활동현금흐름(OCF) 및 수익성 추적")
    st.info("💡 **실무적 해석:** 당기순이익과 OCF의 괴리율을 추적하여, 외형 성장(매출) 이면에 기업의 실질적인 현금창출능력과 운전자본 부담이 얼마나 견고한지 평가합니다.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("당기 매출액", f"{current['매출액']:,} 억", f"{current['매출액'] - previous['매출액']:,} 억")
    col2.metric("당기순이익", f"{current['당기순이익']:,} 억", f"{current['당기순이익'] - previous['당기순이익']:,} 억")
    col3.metric("영업활동현금흐름(OCF)", f"{current['영업활동현금흐름(OCF)']:,} 억", f"{current['영업활동현금흐름(OCF)'] - previous['영업활동현금흐름(OCF)']:,} 억")

    fig_ocf = go.Figure()
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['당기순이익'], name='당기순이익', marker_color='#A9A9A9'))
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['영업활동현금흐름(OCF)'], name='영업활동현금흐름(OCF)', marker_color='#1f77b4'))
    fig_ocf.update_layout(barmode='group', title="당기순이익 vs 영업활동현금흐름(OCF) 질적 분석", height=400)
    
    st.plotly_chart(fig_ocf, width='stretch')

    # --- Section 2: 듀퐁 분석 (DuPont Analysis) ---
    st.markdown("---")
    st.subheader("2. 재무 분석: 듀퐁 분석 (자기자본이익률 ROE 변동 원인 시각화)")
    
    def calc_dupont(row):
        npm = row['당기순이익'] / row['매출액'] if row['매출액'] else 0
        ato = row['매출액'] / row['총자산'] if row['총자산'] else 0
        em = row['총자산'] / row['자기자본'] if row['자기자본'] else 0
        roe = npm * ato * em
        return npm, ato, em, roe

    prev_npm, prev_ato, prev_em, prev_roe = calc_dupont(previous)
    curr_npm, curr_ato, curr_em, curr_roe = calc_dupont(current)

    dupont_df = pd.DataFrame({
        '지표 (Indicator)': ['매출액순이익률(NPM)', '총자산회전율(ATO)', '재무레버리지(EM)', '자기자본이익률(ROE)'],
        '전기 (2024)': [f"{prev_npm:.2%}", f"{prev_ato:.2f}x", f"{prev_em:.2f}x", f"{prev_roe:.2%}"],
        '당기 (2025)': [f"{curr_npm:.2%}", f"{curr_ato:.2f}x", f"{curr_em:.2f}x", f"{curr_roe:.2%}"],
        '증감 (Variance)': [
            f"{(curr_npm - prev_npm) * 100:.2f}%p", 
            f"{(curr_ato - prev_ato):.2f}x", 
            f"{(curr_em - prev_em):.2f}x", 
            f"{(curr_roe - prev_roe) * 100:.2f}%p"
        ]
    })
    
    col4, col5 = st.columns([1, 1.5])
    with col4:
        st.dataframe(dupont_df, hide_index=True, width='stretch')
        st.info("💡 **결산 분석 코멘트:** 전기 대비 ROE의 변동 원인을 수익성(NPM), 활동성(ATO), 안정성(EM) 측면에서 분해하여 보여줍니다.")

    with col5:
        fig_dupont = go.Figure(data=[
            go.Bar(name='전기 (2024)', x=['매출액순이익률', '총자산회전율', '재무레버리지'], y=[prev_npm, prev_ato, prev_em], marker_color='#A9A9A9'),
            go.Bar(name='당기 (2025)', x=['매출액순이익률', '총자산회전율', '재무레버리지'], y=[curr_npm, curr_ato, curr_em], marker_color='#1f77b4')
        ])
        fig_dupont.update_layout(title="듀퐁 핵심 지표 전기 대비 변동(Variance) 비교", barmode='group', height=350)
        
        st.plotly_chart(fig_dupont, width='stretch')

else:
    st.warning("데이터가 부족하여 비교 분석을 수행할 수 없습니다.")

# --- Section 3: 경영관리 실무 (법인카드 및 비용 통제) ---
st.markdown("---")
st.subheader("3. 경영관리 실무: 부서별 법인카드 모니터링 및 이상치 탐지")
st.info("💡 **올라운더 실무 적용:** 매월 발생하는 수백 건의 법인카드 내역 중, 사내 규정 위반 의심 건(주말/심야 결제, 고액 결제)을 파이썬으로 자동 필터링하여 비용 검증 및 정산 업무의 리드타임을 획기적으로 단축합니다.")

# 가상 법인카드 데이터 생성
np.random.seed(42) 

card_data = pd.DataFrame({
    '결제일자': pd.date_range(start='2025-03-01', periods=50, freq='D').strftime('%Y-%m-%d'),
    '부서명': np.random.choice(['마케팅팀', '디자인팀', '경영지원팀', '글로벌영업팀', '물류팀'], 50),
    '사용처': np.random.choice(['네이버/메타 광고', '비품(쿠팡)', '스타벅스', '야근식대(배달의민족)', '항공권(해외출장)', '주말/심야_택시', '고가_소프트웨어_구독'], 50),
    '결제금액': np.random.randint(10000, 1500000, 50)
})

col6, col7 = st.columns([1, 1])

with col6:
    st.markdown("#### 📊 부서별 비용 집행 비율")
    # 부서별 사용금액 도넛 차트
    dept_expense = card_data.groupby('부서명')['결제금액'].sum().reset_index()
    fig_pie = go.Figure(data=[go.Pie(labels=dept_expense['부서명'], values=dept_expense['결제금액'], hole=.4)])
    fig_pie.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, width='stretch')

with col7:
    st.markdown("#### 🚨 비용 증빙 집중 검토 대상 (이상치 탐지)")
    st.markdown("**필터링 조건:** 건당 50만 원 이상 고액 결제 **OR** 주말/심야 휴일 결제 건")
    
    # 이상치 필터링 로직
    anomaly_df = card_data[
        (card_data['결제금액'] >= 500000) | 
        (card_data['사용처'].str.contains('주말|심야'))
    ].sort_values('결제금액', ascending=False).reset_index(drop=True)
    
    # 금액 포맷팅 (보기 편하게 천단위 콤마 추가)
    anomaly_df['결제금액'] = anomaly_df['결제금액'].apply(lambda x: f"{x:,.0f} 원")
    
    st.dataframe(anomaly_df, height=300, width='stretch')
