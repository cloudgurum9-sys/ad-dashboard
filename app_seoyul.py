import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(page_title="재무/현금흐름 분석 대시보드", page_icon="📊", layout="wide")

# 2. 가상 재무 데이터 생성
@st.cache_data
def load_data():
    data = {
        '연도': ['2024', '2025', '2024', '2025', '2024', '2025'],
        '산업군': ['광고업', '광고업', '게임업', '게임업', 'IT서비스', 'IT서비스'],
        '기업명': ['A광고사', 'A광고사', '컴투스', '컴투스', 'B서비스', 'B서비스'],
        '매출액': [5000, 5200, 7084, 8560, 10000, 9500],
        '당기순이익': [300, 350, -214, 452, 800, 600],
        '총자산': [8000, 8500, 15200, 14850, 20000, 19000],
        '자기자본': [5000, 5300, 11300, 11780, 12000, 11500],
        # K-IFRS 공식 명칭 완벽 적용
        '영업활동현금흐름(OCF)': [400, 450, 158, 620, 1200, 900]
    }
    return pd.DataFrame(data)

df = load_data()

# 3. 사이드바 설정 (컴투스 자동 선택 로직 제거, A광고사가 무조건 먼저 뜸)
st.sidebar.header("🔍 분석 필터")

industry_list = df['산업군'].unique().tolist()

# 기본값을 0번 인덱스('광고업')로 고정
selected_industry = st.sidebar.selectbox("🏢 산업군 선택", industry_list, index=0)

filtered_companies = df[df['산업군'] == selected_industry]['기업명'].unique()
selected_company = st.sidebar.selectbox("🏢 기업 선택", filtered_companies)

# 최종 선택된 기업 데이터
company_data = df[df['기업명'] == selected_company].sort_values('연도').reset_index(drop=True)

# 4. 메인 대시보드 화면
st.title(f"📊 {selected_company} 재무 및 현금흐름 분석 대시보드")
st.markdown("---")

if len(company_data) >= 2:
    # 당기(2025) 및 전기(2024) 데이터 추출
    current = company_data.iloc[-1]
    previous = company_data.iloc[-2]

    # --- Section 1: 실질 현금창출력 (OCF) 추적 ---
    st.subheader("1. 영업활동현금흐름(OCF) 및 당기순이익 추적")
    st.info("💡 **실무적 해석:** 당기순이익과 OCF의 괴리율을 추적하여 기업의 실질적인 현금창출능력을 평가합니다.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("당기 매출액", f"{current['매출액']:,} 억", f"{current['매출액'] - previous['매출액']:,} 억")
    col2.metric("당기순이익", f"{current['당기순이익']:,} 억", f"{current['당기순이익'] - previous['당기순이익']:,} 억")
    # 메트릭 라벨 변경 완료
    col3.metric("영업활동현금흐름(OCF)", f"{current['영업활동현금흐름(OCF)']:,} 억", f"{current['영업활동현금흐름(OCF)'] - previous['영업활동현금흐름(OCF)']:,} 억")

    # 시각화: 순이익 vs OCF 비교 바 차트 (제목 및 범례 변경 완료)
    fig_ocf = go.Figure()
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['당기순이익'], name='당기순이익', marker_color='#A9A9A9'))
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['영업활동현금흐름(OCF)'], name='영업활동현금흐름(OCF)', marker_color='#1f77b4'))
    fig_ocf.update_layout(barmode='group', title="당기순이익 vs 영업활동현금흐름(OCF) 질적 분석", height=400)
    st.plotly_chart(fig_ocf, use_container_width=True)

    # --- Section 2: 듀퐁 분석 (DuPont Analysis) 전기 대비 증감 분해 ---
    st.markdown("---")
    st.subheader("2. 듀퐁 분석 (자기자본이익률 ROE 변동 원인 시각화)")
    
    # 듀퐁 지표 계산
    def calc_dupont(row):
        npm = row['당기순이익'] / row['매출액'] if row['매출액'] else 0
        ato = row['매출액'] / row['총자산'] if row['총자산'] else 0
        em = row['총자산'] / row['자기자본'] if row['자기자본'] else 0
        roe = npm * ato * em
        return npm, ato, em, roe

    prev_npm, prev_ato, prev_em, prev_roe = calc_dupont(previous)
    curr_npm, curr_ato, curr_em, curr_roe = calc_dupont(current)

    # 듀퐁 분석 지표 비교 테이블 (%p 수정 반영)
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
        st.dataframe(dupont_df, hide_index=True, use_container_width=True)
        # 기말 잔액 주석 추가 완료
        st.info("💡 **결산 분석 코멘트:** 전기 대비 ROE의 변동 원인을 수익성(NPM), 활동성(ATO), 안정성(EM) 측면에서 분해하여 보여줍니다. (※ 본 분석의 자산 및 자본 지표는 기말 잔액 기준입니다.)")

    # 시각화: 듀퐁 핵심 지표 바 차트
    with col5:
        fig_dupont = go.Figure(data=[
            go.Bar(name='전기 (2024)', x=['매출액순이익률', '총자산회전율', '재무레버리지'], y=[prev_npm, prev_ato, prev_em], marker_color='#A9A9A9'),
            go.Bar(name='당기 (2025)', x=['매출액순이익률', '총자산회전율', '재무레버리지'], y=[curr_npm, curr_ato, curr_em], marker_color='#1f77b4')
        ])
        fig_dupont.update_layout(title="듀퐁 핵심 지표 전기 대비 변동(Variance) 비교", barmode='group', height=350)
        st.plotly_chart(fig_dupont, use_container_width=True)

else:
    st.warning("데이터가 부족하여 비교 분석을 수행할 수 없습니다.")
