import streamlit as st
import pandas as pd
import plotly.express as px  # 예쁜 차트를 만들기 위한 라이브러리 추가

# 1. 페이지 기본 설정
st.set_page_config(page_title="한라엔컴 재무 대시보드", layout="wide")

# ==========================================
# 💡 [핵심 추가] CSS 주입을 통한 배경/폰트 색상 강제 고정
# ==========================================
st.markdown("""
<style>
    /* 메인 화면 배경색 (연한 회색) */
    .stApp {
        background-color: #F4F6F9;
    }
    /* 사이드바 배경색 (메인보다 살짝 어두운 회색) */
    [data-testid="stSidebar"] {
        background-color: #E9ECEF;
    }
    /* 모든 텍스트 색상을 검은색으로 강제 적용 (다크모드 무력화) */
    .stApp, .stApp p, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6, .stApp span, .stApp div, .stApp label, .stApp li {
        color: #111111 !important;
    }
    /* 표(DataFrame) 내부 텍스트 색상 */
    th, td {
        color: #111111 !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. 사이드바 (필터)
st.sidebar.header("분석 필터")
industry_selection = st.sidebar.selectbox("산업군 선택", ["레미콘/건설자재", "제조업 일반"])
company_selection = st.sidebar.selectbox("기업 선택", ["한라엔컴", "동종업계 경쟁사"])

# 3. 메인 타이틀
st.title("📊 한라엔컴 재무결산 및 비용통제 대시보드")
st.markdown("---")

# ==========================================
# 섹션 1. 결산 분석 (누운 막대그래프 세우기)
# ==========================================
st.header("1. 결산 분석: 영업활동현금흐름(OCF) 및 매출채권 리스크 트래킹")

st.markdown("""
* **재무회계 실무 적용:** 최근 건설 경기 침체로 인해 B2B 건설사 대상 **매출채권** 대금 회수 지연(**대손** 리스크)이 커지고 있습니다. 
손익계산서상의 당기순이익에 **연연하지 않고**, 회사의 **실질적인** 현금창출능력(OCF)을 교차 검증하여 **흑자부도** 리스크를 꼼꼼히 모니터링합니다.
""")

col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="당기순이익", value="200억", delta="20억 (전년 대비)")
    st.metric(label="영업활동현금흐름(OCF)", value="80억", delta="-20억 (전년 대비)", delta_color="inverse")
with col2:
    # 데이터 세팅
    chart_data = pd.DataFrame({
        "연도": ["2024", "2025"],
        "당기순이익": [180, 200],
        "영업활동현금흐름(OCF)": [100, 80]
    })
    
    # 💡 누운 그래프를 세로로 반듯하게 세우는 Plotly 막대그래프
    fig_bar = px.bar(chart_data, x="연도", y=["당기순이익", "영업활동현금흐름(OCF)"], 
                     barmode="group", title="당기순이익 vs 영업활동현금흐름(OCF) 괴리율 분석")
    
    # 💡 [추가] 차트 배경을 투명하게 만들고 폰트를 검은색으로 설정 (회색 배경과 위화감 없애기)
    fig_bar.update_layout(
        legend_title_text='구분', 
        xaxis_title="", 
        yaxis_title="금액 (억원)",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#111111')
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True) # 여백 추가

# ==========================================
# 섹션 2. 비용 통제 (사라진 원형 그래프 부활!)
# ==========================================
st.header("2. 전국 현장(공장) 비용 증빙 통제 및 이상치 탐지")

@st.cache_data
def generate_halla_expenses():
    anomalies = [
        {"전표일자": "2025-03-21", "발생현장(부서)": "천안공장_설비보전팀", "사용처(계정과목)": "배치플랜트 메인모터 긴급수리", "청구금액": 4342807},
        {"전표일자": "2025-04-19", "발생현장(부서)": "본사_재무회계팀", "사용처(계정과목)": "외부 회계감사/자문 수수료", "청구금액": 4227419},
        {"전표일자": "2025-04-08", "발생현장(부서)": "천안공장_설비보전팀", "사용처(계정과목)": "컨베이어 벨트 긴급 교체 부품비", "청구금액": 4072998},
        {"전표일자": "2025-03-14", "발생현장(부서)": "광주공장_물류팀", "사용처(계정과목)": "시멘트/골재 야간 하역 용역비", "청구금액": 4053339},
        {"전표일자": "2025-03-20", "발생현장(부서)": "용인공장_생산팀", "사용처(계정과목)": "동절기 현장 안전용품(안전모/화) 대량구입", "청구금액": 3947389},
        {"전표일자": "2025-03-22", "발생현장(부서)": "본사_영업본부", "사용처(계정과목)": "B2B 건설사 임원 주말 접대비", "청구금액": 3802279},
        {"전표일자": "2025-03-18", "발생현장(부서)": "본사_영업본부", "사용처(계정과목)": "신규 수주 VIP 거래처 접대비", "청구금액": 3721441},
        {"전표일자": "2025-04-12", "발생현장(부서)": "본사_재무회계팀", "사용처(계정과목)": "결산용 ERP 모듈 라이선스 갱신", "청구금액": 3670495},
    ]
    return pd.DataFrame(anomalies)

# 숫자형 데이터 원본 (그래프용)
report_numeric = generate_halla_expenses()

# 문자형 데이터 (표 출력용 - 천 단위 콤마)
report_display = report_numeric.copy()
report_display['청구금액(원)'] = report_display['청구금액'].apply(lambda x: f"{x:,}")
report_display = report_display.drop(columns=['청구금액'])

# 💡 사라졌던 원형 그래프(도넛 차트) 부활
fig_pie = px.pie(report_numeric, values='청구금액', names='발생현장(부서)', hole=0.3,
                 title="🚨 부서별 이상치 결제 금액 비중")
fig_pie.update_traces(textposition='inside', textinfo='percent+label')

# 💡 [추가] 파이 차트 배경 투명화 및 폰트 색상 강제
fig_pie.update_layout(
    paper_bgcolor='rgba(0,0,0,0)', 
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#111111')
)

# 화면을 반으로 나누어 왼쪽엔 원형 그래프, 오른쪽엔 표 배치
col_pie, col_table = st.columns([1, 1.5])

with col_pie:
    st.plotly_chart(fig_pie, use_container_width=True)
    
with col_table:
    st.markdown("**[전표 집중 검토 대상 (고액 300만 원 이상 및 주말 결제 건)]**")
    st.dataframe(report_display, use_container_width=True, hide_index=True)
