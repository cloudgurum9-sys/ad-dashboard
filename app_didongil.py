import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 기본 설정 (제조업 느낌의 아이콘으로 변경)
st.set_page_config(page_title="디아이동일 재무 분석 대시보드", page_icon="🏭", layout="wide")

# 2. 가상 재무 데이터 생성 (디아이동일 및 2차전지 알루미늄박 경쟁사 맞춤형)
@st.cache_data
def load_data():
    data = {
        '연도': ['2024', '2025', '2024', '2025', '2024', '2025'],
        '산업군': ['2차전지 알루미늄박', '2차전지 알루미늄박', '2차전지 소재', '2차전지 소재', '종합 포장재/소재', '종합 포장재/소재'],
        '기업명': ['디아이동일(알루미늄 사업부)', '디아이동일(알루미늄 사업부)', '삼아알미늄', '삼아알미늄', '동원시스템즈', '동원시스템즈'],
        '매출액': [8000, 9500, 3000, 3800, 12000, 13500], # 단위: 억원
        '당기순이익': [450, 680, 200, 310, 800, 950],
        '총자산': [12000, 16000, 4500, 6000, 15000, 18000], # 공장 증설(CAPEX)로 인한 자산 증가 반영
        '자기자본': [6000, 7500, 2000, 2800, 7000, 8500],
        '영업활동현금흐름(OCF)': [500, 850, 150, 400, 1100, 1400]
    }
    return pd.DataFrame(data)

df = load_data()

# 3. 사이드바 설정
st.sidebar.header("🔍 분석 필터")

industry_list = df['산업군'].unique().tolist()
selected_industry = st.sidebar.selectbox("🏭 산업군 선택", industry_list, index=0)

filtered_companies = df[df['산업군'] == selected_industry]['기업명'].unique()
selected_company = st.sidebar.selectbox("🏢 기업 선택", filtered_companies)

company_data = df[df['기업명'] == selected_company].sort_values('연도').reset_index(drop=True)

# 4. 메인 대시보드 화면
st.title(f"🏭 {selected_company} 경영관리 및 재무 분석 대시보드")
st.markdown("---")

if len(company_data) >= 2:
    current = company_data.iloc[-1]
    previous = company_data.iloc[-2]

    # --- Section 1: 실질 현금창출력 (OCF) 추적 ---
    st.subheader("1. 재무 분석: 영업활동현금흐름(OCF) 및 수익성 추적")
    st.info("💡 **실무적 해석:** 2차전지 알루미늄박 수요 증가에 따른 외형 성장과 더불어, 대규모 설비투자(CAPEX)가 지속되는 환경 속에서 기업의 실질적인 현금창출능력(OCF)이 원활하게 방어되고 있는지 모니터링합니다.")
    
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
        st.info("💡 **결산 분석 코멘트:** 공장 라인 증설 등으로 인한 총자산 증가가 실제 생산/매출(총자산회전율)과 수익성(NPM) 개선으로 이어져 ROE를 견인하고 있는지 분해하여 분석합니다.")

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
st.subheader("3. 현장/사업부별 비용 모니터링 및 이상치 자동 탐지 (제조원가 통제)")
st.info("💡 **올라운더 실무 적용:** 매월 발생하는 방대한 현장 설비 유지보수 및 비용 증빙 내역 중, 사내 규정 위반 의심 건(주말/심야 긴급 결제, 고액 분할 결제 등)을 Python으로 자동 필터링하여 결산 리드타임을 획기적으로 단축합니다.")

# 가상 현장 법인카드 데이터 생성 (제조업 부서명 및 사용처로 변경)
np.random.seed(42) 

card_data = pd.DataFrame({
    '결제일자': pd.date_range(start='2025-03-01', periods=50, freq='D').strftime('%Y-%m-%d'),
    '부서명': np.random.choice(['생산관리팀', '품질보증팀', '설비기술팀', '원자재구매팀', '영업본부'], 50),
    '사용처': np.random.choice(['설비 유지보수(외주)', '소모품(안전장비/공구)', '야근/특근식대', '물류/운송비(긴급배차)', '주말/심야_긴급수리', '고가_원부자재_샘플', '거래처 접대비'], 50),
    # 제조업 특성상 결제 단가를 높임
    '결제금액': np.random.randint(50000, 2500000, 50)
})

col6, col7 = st.columns([1, 1])

with col6:
    st.markdown("#### 📊 공장/부서별 비용 집행 현황")
    # 부서별 사용금액 도넛 차트
    dept_expense = card_data.groupby('부서명')['결제금액'].sum().reset_index()
    fig_pie = go.Figure(data=[go.Pie(labels=dept_expense['부서명'], values=dept_expense['결제금액'], hole=.4)])
    fig_pie.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, width='stretch')

with col7:
    st.markdown("#### 🚨 비용 증빙 집중 검토 대상 (자동 이상치 탐지)")
    # 제조업에 맞게 필터링 조건 금액 상향
    st.markdown("**필터링 조건:** 건당 **100만 원 이상 고액 결제** OR **주말/심야 휴일 결제** 건")
    
    # 이상치 필터링 로직
    anomaly_df = card_data[
        (card_data['결제금액'] >= 1000000) | 
        (card_data['사용처'].str.contains('주말|심야'))
    ].sort_values('결제금액', ascending=False).reset_index(drop=True)
    
    # 금액 포맷팅 (천단위 콤마 추가)
    anomaly_df['결제금액'] = anomaly_df['결제금액'].apply(lambda x: f"{x:,.0f} 원")
    
    st.dataframe(anomaly_df, height=300, width='stretch')
