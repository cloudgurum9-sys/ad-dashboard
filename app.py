import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. 페이지 기본 설정
st.set_page_config(page_title="글로벌 게임사 재무/현금흐름 분석 대시보드", page_icon="🎮", layout="wide")

# 2. 가상 재무 데이터 생성 (컴투스 및 게임 산업 타겟팅)
@st.cache_data
def load_data():
    data = {
        '연도': ['2024', '2025', '2024', '2025', '2024', '2025'],
        '산업군': ['게임업', '게임업', '광고업', '광고업', 'IT서비스', 'IT서비스'],
        '기업명': ['컴투스', '컴투스', 'A광고사', 'A광고사', 'B서비스', 'B서비스'],
        '매출액': [7084, 8560, 5000, 5200, 10000, 9500],
        '당기순이익': [-214, 452, 300, 350, 800, 600],
        '총자산': [15200, 14850, 8000, 8500, 20000, 19000],
        '자기자본': [11300, 11780, 5000, 5300, 12000, 11500],
        '영업현금흐름(OCF)': [158, 620, 400, 450, 1200, 900]
    }
    return pd.DataFrame(data)

df = load_data()

# 3. 사이드바 설정 (산업군 '게임업' 디폴트 고정 로직 적용)
st.sidebar.header("🔍 분석 필터")

# 실제 데이터에서 유니크한 산업군 리스트를 추출합니다.
industry_list = df['산업군'].unique().tolist()

# 핵심 포인트: 리스트 안에 '게임업'이 몇 번째 인덱스에 있는지 찾습니다.
if '게임업' in industry_list:
    default_index = industry_list.index('게임업')
else:
    # 만약 '게임업'이 없다면 그냥 맨 처음(0번) 것을 띄움 (에러 방지)
    default_index = 0

# selectbox의 index 속성에 찾은 번호를 넣어줍니다. 
selected_industry = st.sidebar.selectbox("🏢 산업군 선택", industry_list, index=default_index)

# 선택된 산업군에 맞는 기업만 필터링
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
    st.subheader("1. 영업현금흐름(OCF) 및 당기순이익 추적")
    st.info("💡 **실무적 해석:** 당기순이익과 OCF의 괴리율을 추적하여 기업의 실질적인 현금창출능력을 평가합니다.")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("당기 매출액", f"{current['매출액']:,} 억", f"{current['매출액'] - previous['매출액']:,} 억")
    col2.metric("당기순이익", f"{current['당기순이익']:,} 억", f"{current['당기순이익'] - previous['당기순이익']:,} 억")
    col3.metric("영업현금흐름(OCF)", f"{current['영업현금흐름(OCF)']:,} 억", f"{current['영업현금흐름(OCF)'] - previous['영업현금흐름(OCF)']:,} 억")

    # 시각화: 순이익 vs OCF 비교 바 차트
    fig_ocf = go.Figure()
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['당기순이익'], name='당기순이익', marker_color='#A9A9A9'))
    fig_ocf.add_trace(go.Bar(x=company_data['연도'], y=company_data['영업현금흐름(OCF)'], name='영업현금흐름(OCF)', marker_color='#1f77b4'))
    fig_ocf.update_layout(barmode='group', title="당기순이익 vs 영업현금흐름 질적 분석", height=400, template="streamlit")
    st.plotly_chart(fig_ocf, use_container_width=True)


    # --- Section 2: 듀퐁 분석 (DuPont Analysis) 전기 대비 증감 분해 ---
    st.markdown("---")
    st.subheader("2. 듀퐁 분석 (자기자본이익률 ROE 변동 원인 시각화)")
    
    # 듀퐁 지표 계산
    def calc_dupont(row):
        npm = row['당기순이익'] / row['매출액'] if row['매출액'] else 0 # 매출액순이익률 (수익성)
        ato = row['매출액'] / row['총자산'] if row['총자산'] else 0 # 총자산회전율 (활동성)
        em = row['총자산'] / row['자기자본'] if row['자기자본'] else 0 # 재무레버리지 (안정성)
        roe = npm * ato * em
        return npm, ato, em, roe

    prev_npm, prev_ato, prev_em, prev_roe = calc_dupont(previous)
    curr_npm, curr_ato, curr_em, curr_roe = calc_dupont(current)

    # 듀퐁 분석 지표 비교 테이블
    dupont_df = pd.DataFrame({
        '지표 (Indicator)': ['매출액순이익률(NPM)', '총자산회전율(ATO)', '재무레버리지(EM)', '자기자본이익률(ROE)'],
        '전기 (2024)': [f"{prev_npm:.2%}", f"{prev_ato:.2f}x", f"{prev_em:.2f}x", f"{prev_roe:.2%}"],
        '당기 (2025)': [f"{curr_npm:.2%}", f"{curr_ato:.2f}x", f"{curr_em:.2f}x", f"{curr_roe:.2%}"],
        '증감 (Variance)': [f"{(curr_npm - prev_npm):.2%}", f"{(curr_ato - prev_ato):.2f}x", f"{(curr_em - prev_em):.2f}x", f"{(curr_roe - prev_roe):.2%}"]
    })
    
    col4, col5 = st.columns([1, 1.5])
    with col4:
        st.dataframe(dupont_df, hide_index=True, use_container_width=True)
        st.info("💡 **결산 분석 코멘트:** 전기 대비 ROE의 변동 원인을 수익성(NPM), 활동성(ATO), 안정성(EM) 측면에서 분해하여 보여줍니다.")

    # 시각화: 듀퐁 핵심 지표 바 차트
    with col5:
        fig_dupont = go.Figure(data=[
            go.Bar(name='전기 (2024)', x=['매출액순이익률', '총자산회전율', '재무레버리지'], y=[prev_npm, prev_ato, prev_em], marker_color='#A9A9A9'),
            go.Bar(name='당기 (2025)', x=['매출액순이익률', '총자산회전율', '재무레버리지'], y=[curr_npm, curr_ato, curr_em], marker_color='#1f77b4')
        ])
        fig_dupont.update_layout(title="듀퐁 핵심 지표 전기 대비 변동(Variance) 비교", barmode='group', height=350, template="streamlit")
        st.plotly_chart(fig_dupont, use_container_width=True)

else:
    st.warning("데이터가 부족하여 비교 분석을 수행할 수 없습니다.")
