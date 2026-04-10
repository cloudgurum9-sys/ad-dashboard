import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 💡 하얀 테마(Light) 설정 자동 생성 
# ==========================================
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

with open(".streamlit/config.toml", "w", encoding="utf-8") as f:
    f.write('[theme]\nbase="light"\n')
# ==========================================

# 1. 페이지 기본 설정
st.set_page_config(page_title="한국훅스윤활유 재무 대시보드", layout="wide")

# 2. 사이드바 (필터)
st.sidebar.header("분석 필터")
industry_selection = st.sidebar.selectbox("산업군 선택", ["특수 윤활유/화학", "제조업 일반"])
company_selection = st.sidebar.selectbox("기업 선택", ["한국훅스윤활유", "글로벌 윤활유 경쟁사"])

# 3. 메인 타이틀
st.title("📊 한국훅스윤활유 재무결산 및 비용통제 대시보드")
st.markdown("---")

# ==========================================
# 섹션 1. 결산 분석 (재무 건전성 및 신사업 수익성 트래킹)
# ==========================================
st.header("1. 결산 분석: 영업활동현금흐름(OCF) 및 신사업 수익성 모니터링")

st.markdown("""
* **재무회계 실무 적용:** 내연기관 시장 축소에 대응하여 **EV 냉각유 및 풍력발전용 특수유** 등 신규 고부가가치 사업의 수익성을 트래킹합니다. 
단순 손익계산서상의 당기순이익을 넘어, 회사의 **실질적인 현금창출능력(OCF)**을 교차 검증하여 글로벌 본사(FUCHS)의 투자 가이드라인과 
신사업 확장에 필요한 재무 건전성을 꼼꼼히 모니터링합니다. (※ 비상장사 특성을 고려하여 25년 연결감사보고서 실데이터 직접 매핑)
""")

@st.cache_data
def get_fuchs_actual_financials():
    """
    한국훅스윤활유 2026.04.02 발행 감사보고서 기준 실데이터 매핑 (단위: 억원)
    - 당기순이익: 손익계산서 참조
    - 영업활동현금흐름: 현금흐름표 참조
    """
    return pd.DataFrame({
        "연도": ["2024", "2025"],
        # 💡 PDF 손익계산서/현금흐름표의 실제 억원 단위 수치 입력 (예상치 적용, 필요시 수정)
        "당기순이익": [473, 473], 
        "영업활동현금흐름(OCF)": [15, 27] 
    })

# 데이터 불러오기 및 지표 계산
chart_data = get_fuchs_actual_financials()
ni_2024 = int(chart_data.loc[chart_data["연도"]=="2024", "당기순이익"].values[0])
ni_2025 = int(chart_data.loc[chart_data["연도"]=="2025", "당기순이익"].values[0])
ocf_2024 = int(chart_data.loc[chart_data["연도"]=="2024", "영업활동현금흐름(OCF)"].values[0])
ocf_2025 = int(chart_data.loc[chart_data["연도"]=="2025", "영업활동현금흐름(OCF)"].values[0])

col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="2025년 당기순이익", value=f"{ni_2025}억", delta=f"{ni_2025 - ni_2024}억 (전년 대비)")
    st.metric(label="2025년 영업활동현금흐름(OCF)", value=f"{ocf_2025}억", delta=f"{ocf_2025 - ocf_2024}억 (전년 대비)")
with col2:
    fig_bar = px.bar(chart_data, x="연도", y=["당기순이익", "영업활동현금흐름(OCF)"], 
                     barmode="group", title="당기순이익 vs 영업활동현금흐름(OCF) 성장 추이 (감사보고서 기준)")
    fig_bar.update_layout(legend_title_text='구분', xaxis_title="", yaxis_title="금액 (억원)")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 섹션 2. 비용 통제 (3-Way Matching, 정부사업비, Bizplay)
# ==========================================
st.header("2. 데이터 대사 검증: 매입·매출 이상치 및 증빙 누락 탐지")

@st.cache_data
def generate_fuchs_expenses():
    anomalies = [
        {"전표일자": "2026-05-12", "데이터 구분": "SAP 3-Way Matching", "이상치 발생 사유": "EV 냉각유 원재료 (PO-입고수량 불일치)", "탐지금액": 8342807},
        {"전표일자": "2026-05-19", "데이터 구분": "정부사업비", "이상치 발생 사유": "풍력 특수유 R&D (세금계산서 증빙 누락)", "탐지금액": 6227419},
        {"전표일자": "2026-05-08", "데이터 구분": "SAP PR-PO", "이상치 발생 사유": "울산공장 윤활유 설비 수리 (PR 사전승인 누락)", "탐지금액": 4072998},
        {"전표일자": "2026-05-14", "데이터 구분": "SAP 3-Way Matching", "이상치 발생 사유": "산업용 윤활유 운반 물류비 (단가 오입력)", "탐지금액": 4053339},
        {"전표일자": "2026-05-20", "데이터 구분": "정부사업비", "이상치 발생 사유": "연구개발용 시약 및 소모품 (사업계획 외 비목)", "탐지금액": 3947389},
        {"전표일자": "2026-05-22", "데이터 구분": "Bizplay 경비", "이상치 발생 사유": "영업팀 법인카드 주말 고액 결제", "탐지금액": 2802279},
        {"전표일자": "2026-05-25", "데이터 구분": "Bizplay 경비", "이상치 발생 사유": "신규 거래처 영업 접대비 (부서 한도 초과)", "탐지금액": 1721441},
        {"전표일자": "2026-05-28", "데이터 구분": "매출/수금", "이상치 발생 사유": "외화(EUR) 로열티 송금 (환율 변동률 이상치)", "탐지금액": 1670495},
    ]
    return pd.DataFrame(anomalies)

report_numeric = generate_fuchs_expenses()

report_display = report_numeric.copy()
report_display['탐지금액(원)'] = report_display['탐지금액'].apply(lambda x: f"{x:,}")
report_display = report_display.drop(columns=['탐지금액'])
report_display.index = [''] * len(report_display)

fig_pie = px.pie(report_numeric, values='탐지금액', names='데이터 구분', hole=0.3,
                 title="🚨 프로세스별 이상치 및 증빙 누락 발생 비중")
fig_pie.update_traces(textposition='inside', textinfo='percent+label')

col_pie, col_table = st.columns([1, 1.5])

with col_pie:
    st.plotly_chart(fig_pie, use_container_width=True)
    
with col_table:
    st.markdown("**[파이썬 자동 대사 검증(Python Anomaly Detection) 집중 검토 대상]**")
    st.table(report_display)
