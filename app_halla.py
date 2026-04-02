import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(page_title="한라엔컴 재무결산 및 비용통제 대시보드", page_icon="🏗️", layout="wide")

# 2. 가상 재무 데이터 생성 (듀퐁 분석용 자산/자본 데이터 삭제, OCF 집중)
@st.cache_data
def load_financial_data():
    data = {
        '연도': ['2024', '2025', '2024', '2025', '2024', '2025'],
        '산업군': ['레미콘/건설자재', '레미콘/건설자재', '레미콘/건설자재', '레미콘/건설자재', '시멘트 제조', '시멘트 제조'],
        '기업명': ['한라엔컴', '한라엔컴', '유진기업(레미콘)', '유진기업(레미콘)', '삼표시멘트', '삼표시멘트'],
        '매출액': [3500, 3700, 8000, 8200, 7500, 7800], # 단위: 억원
        '당기순이익': [250, 180, 400, 320, 350, 290], # 건설업황 악화로 이익 감소
        '영업활동현금흐름(OCF)': [200, 80, 300, 150, 400, 250] # 매출채권 회수 지연으로 현금흐름 악화 반영
    }
    return pd.DataFrame(data)

df = load_financial_data()

# 3. 사이드바 설정
st.sidebar.header("🔍 분석 필터")

industry_list = df['산업군'].unique().tolist()
selected_industry = st.sidebar.selectbox("🏗️ 산업군 선택", industry_list, index=0)

filtered_companies = df[df['산업군'] == selected_industry]['기업명'].unique()
selected_company = st.sidebar.selectbox("🏢 기업 선택", filtered_companies)

company_data = df[df['기업명'] == selected_company].sort_values('연도').reset_index(drop=True)

# 4. 메인 대시보드 화면
st.title(f"🏗️ {selected_company} 재무결산 및 비용통제 대시보드")
st.markdown("---")

if len(company_data) >= 2:
    current = company_data.iloc[-1]
    previous = company_data.iloc[-2]

    # =====================================================================
    # [포트폴리오 Page 4 용] Section 1: 실질 현금창출력(OCF) 및 매출채권 리스크
    # =====================================================================
    st.subheader("1. 결산 분석: 영업활동현금흐름(OCF) 및 매출채권 리스크 트래킹")
    st.info("💡 **재무회계 실무 적용:** 최근 건설 경기 침체로 인해 B2B 건설사 대상 **매출채권 대금 회수 지연(대손 리스크)**이 커지고 있습니다. 손익계산서상의 당기순이익(흑자)에 안주하지 않고, 회사의 실질적인 **현금창출능력(OCF)**을 교차 검증하여 흑자부도 리스크를 꼼꼼히 모니터링합니다.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("당기 매출액", f"{current['매출액']:,} 억", f"{current['매출액'] - previous['매출액']:,} 억")
    col2.metric("당기순이익", f"{current['당기순이익']:,} 억", f"{current['당기순이익'] - previous['당기순이익']:,} 억")
    col3.metric("영업활동현금흐름(OCF)", f"{current['영업활동현금흐름(OCF)']:,} 억", f"{current['영업활동현금흐름(OCF)'] - previous['영업활동현금흐름(OCF)']:,} 억")

    fig_ocf = go.Figure()
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['당기순이익'], name='당기순이익(장부상 이익)', marker_color='#A9A9A9'))
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['영업활동현금흐름(OCF)'], name='영업활동현금흐름(실제 현금)', marker_color='#1f77b4'))
    fig_ocf.update_layout(barmode='group', title="당기순이익 vs 영업활동현금흐름(OCF) 괴리율 분석", height=400)
    
    st.plotly_chart(fig_ocf, width='stretch')

else:
    st.warning("데이터가 부족하여 비교 분석을 수행할 수 없습니다.")


# =====================================================================
# [포트폴리오 Page 5 용] Section 2: 전국 공장 비용 통제 및 이상치 탐지
# =====================================================================
st.markdown("---")
st.subheader("2. 전국 현장(공장) 비용 증빙 통제 및 이상치 탐지 자동화")
st.info("💡 **전표 처리 실무 적용:** 한라엔컴의 전국 15개 이상 레미콘 공장에서 매월 올라오는 방대한 비용 증빙 중, **사내 규정 위반 의심 건(주말 결제, 심야 긴급수리, 300만 원 이상 고액 청구 등)**을 Python으로 자동 필터링합니다. 이를 통해 현장과의 마찰은 줄이고 본사 차원의 결산 정확도와 통제력을 높입니다.")

# 가상 현장 비용 데이터 생성 (레미콘 산업 맞춤형 계정 및 부서)
np.random.seed(42) 

card_data = pd.DataFrame({
    '전표일자': pd.date_range(start='2025-03-01', periods=50, freq='D').strftime('%Y-%m-%d'),
    '발생현장(부서)': np.random.choice(['용인공장_생산팀', '광주공장_물류팀', '천안공장_설비보전팀', '본사_재무회계팀', '본사_영업본부'], 50),
    '사용처(계정과목)': np.random.choice(['믹서트럭 지입/용역비', '시멘트/골재 하역비', '건설현장_주말특근식대', '유류비(경유)', '공장 플랜트_긴급수리비', '현장 안전용품(안전모 등)', '거래처 영업_접대비'], 50),
    # 레미콘 산업 단가 반영 (금액 스케일 업)
    '청구금액(원)': np.random.randint(200000, 4500000, 50)
})

col4, col5 = st.columns([1, 1.2])

with col4:
    st.markdown("#### 📊 현장/부서별 비용 발생 현황")
    # 현장별 사용금액 도넛 차트
    dept_expense = card_data.groupby('발생현장(부서)')['청구금액(원)'].sum().reset_index()
    fig_pie = go.Figure(data=[go.Pie(labels=dept_expense['발생현장(부서)'], values=dept_expense['청구금액(원)'], hole=.4)])
    fig_pie.update_layout(height=380, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, width='stretch')

with col5:
    st.markdown("#### 🚨 전표 집중 검토 대상 (자동 이상치 탐지 결과)")
    # 필터링 조건 명시
    st.markdown("**🔍 필터링 조건:** 건당 **300만 원 이상 고액 청구** OR **주말/긴급** 관련 결제 건")
    
    # 이상치 필터링 로직 (Pandas)
    anomaly_df = card_data[
        (card_data['청구금액(원)'] >= 3000000) | 
        (card_data['사용처(계정과목)'].str.contains('주말|긴급'))
    ].sort_values('청구금액(원)', ascending=False).reset_index(drop=True)
    
    # 금액 포맷팅 (천단위 콤마)
    anomaly_df['청구금액(원)'] = anomaly_df['청구금액(원)'].apply(lambda x: f"{x:,.0f}")
    
    st.dataframe(anomaly_df, height=320, width='stretch')
