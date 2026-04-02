import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 기본 설정 (건설자재/레미콘 느낌의 아이콘으로 변경)
st.set_page_config(page_title="한라엔컴 재무 분석 대시보드", page_icon="🏗️", layout="wide")

# 2. 가상 재무 데이터 생성 (한라엔컴 및 주요 레미콘/시멘트 경쟁사 맞춤형 세팅)
# 매출액 등은 실제 한라엔컴 규모(~3,500억)와 유사하게 스케일링
@st.cache_data
def load_data():
    data = {
        '연도': ['2024', '2025', '2024', '2025', '2024', '2025'],
        '산업군': ['레미콘/건설자재', '레미콘/건설자재', '레미콘/건설자재', '레미콘/건설자재', '시멘트 제조', '시멘트 제조'],
        '기업명': ['한라엔컴', '한라엔컴', '유진기업(레미콘)', '유진기업(레미콘)', '삼표시멘트', '삼표시멘트'],
        '매출액': [3500, 3700, 8000, 8200, 7500, 7800], # 단위: 억원
        '당기순이익': [250, 180, 400, 320, 350, 290], # 건설업황 악화로 이익 감소 추세 반영
        '총자산': [2800, 3100, 11000, 11500, 10000, 10200], # 골재 회사 볼트온 인수로 자산 증가
        '자기자본': [1300, 1450, 4500, 4700, 5000, 5200],
        '영업활동현금흐름(OCF)': [200, 80, 300, 150, 400, 250] # 매출채권 회수 지연으로 현금흐름 악화 반영
    }
    return pd.DataFrame(data)

df = load_data()

# 3. 사이드바 설정
st.sidebar.header("🔍 분석 필터")

industry_list = df['산업군'].unique().tolist()
selected_industry = st.sidebar.selectbox("🏗️ 산업군 선택", industry_list, index=0)

filtered_companies = df[df['산업군'] == selected_industry]['기업명'].unique()
selected_company = st.sidebar.selectbox("🏢 기업 선택", filtered_companies)

company_data = df[df['기업명'] == selected_company].sort_values('연도').reset_index(drop=True)

# 4. 메인 대시보드 화면
st.title(f"🏗️ {selected_company} 경영관리 및 재무 분석 대시보드")
st.markdown("---")

if len(company_data) >= 2:
    current = company_data.iloc[-1]
    previous = company_data.iloc[-2]

    # --- Section 1: 실질 현금창출력 (OCF) 추적 ---
    st.subheader("1. 재무 분석: 영업활동현금흐름(OCF) 및 매출채권 리스크 추적")
    st.info("💡 **실무적 해석:** 최근 건설 경기 침체로 인해 B2B 건설사 대상 **매출채권 대금 회수 지연** 리스크가 커지고 있습니다. 서류상 당기순이익(흑자) 이면에, 회사의 실질적인 **현금창출능력(OCF)이 악화되고 있지 않은지(흑자부도 리스크)** 집중 모니터링합니다.")
    
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
        st.info("💡 **결산 분석 코멘트:** 레미콘 산업은 대규모 공장 플랜트가 필요한 장치산업입니다. 골재 회사 인수 등으로 증가한 총자산이 실제 레미콘 출하 매출(총자산회전율)로 이어져 ROE를 방어하고 있는지 분해하여 분석합니다.")

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
st.subheader("3. 전국 공장별 현장 비용 모니터링 및 이상치 탐지 (제조원가/물류비 통제)")
st.info("💡 **실무 적용:** 전국 15개 이상 레미콘 공장에서 매월 발생하는 방대한 시멘트/골재 매입 내역 및 믹서트럭 물류비 증빙 중, **단가 오입력 의심 건이나 이상 결제(주말 현장 결제, 고액 수리비 등)**를 Python으로 자동 필터링하여 현장과의 마찰을 줄이고 결산의 정확도를 높입니다.")

# 가상 현장 법인카드/비용 데이터 생성 (레미콘 산업 부서명 및 사용처로 완전 변경)
np.random.seed(42) 

card_data = pd.DataFrame({
    '전표일자': pd.date_range(start='2025-03-01', periods=50, freq='D').strftime('%Y-%m-%d'),
    '부서(현장)명': np.random.choice(['본사_구매팀', '용인공장_생산팀', '광주공장_물류팀', '천안공장_설비보전팀', '본사_영업본부'], 50),
    '사용처/계정': np.random.choice(['믹서트럭 지입/용역비', '시멘트/골재 하역비', '건설현장_주말특근식대', '유류비(경유)', '공장 배차실_긴급수리비', '현장 안전용품(안전모/조끼)', '건설사 영업_접대비'], 50),
    # 레미콘 산업 물류/원자재 특성상 단가를 크게 상향
    '청구금액': np.random.randint(200000, 4500000, 50)
})

col6, col7 = st.columns([1, 1])

with col6:
    st.markdown("#### 📊 현장/부서별 비용 집행 현황")
    # 부서별 사용금액 도넛 차트
    dept_expense = card_data.groupby('부서(현장)명')['청구금액'].sum().reset_index()
    fig_pie = go.Figure(data=[go.Pie(labels=dept_expense['부서(현장)명'], values=dept_expense['청구금액'], hole=.4)])
    fig_pie.update_layout(height=350, margin=dict(t=30, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, width='stretch')

with col7:
    st.markdown("#### 🚨 비용 증빙 집중 검토 대상 (자동 이상치 탐지)")
    # 필터링 조건
    st.markdown("**필터링 조건:** 건당 **300만 원 이상 고액 청구** OR **주말/긴급 수리** 관련 건")
    
    # 이상치 필터링 로직
    anomaly_df = card_data[
        (card_data['청구금액'] >= 3000000) | 
        (card_data['사용처/계정'].str.contains('주말|긴급'))
    ].sort_values('청구금액', ascending=False).reset_index(drop=True)
    
    # 금액 포맷팅 (천단위 콤마 추가)
    anomaly_df['청구금액'] = anomaly_df['청구금액'].apply(lambda x: f"{x:,.0f} 원")
    
    st.dataframe(anomaly_df, height=300, width='stretch')
