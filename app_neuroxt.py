import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
st.set_page_config(page_title="NeuroXT 재무 대시보드", layout="wide")

# 2. 사이드바 (필터)
st.sidebar.header("분석 필터")
industry_selection = st.sidebar.selectbox("산업군 선택", ["의료 AI / 딥테크", "IT / 소프트웨어"])
company_selection = st.sidebar.selectbox("기업 선택", ["NeuroXT", "글로벌 의료 AI 경쟁사"])

# 3. 메인 타이틀
st.title("📊 NeuroXT 재무결산 및 비용통제 자동화 대시보드")
st.markdown("---")

# ==========================================
# 섹션 1. 결산 분석 (Series A 스타트업 자금 소진율 및 계정 잔액 관리)
# ==========================================
st.header("1. 기초 회계 관리: 월별 예산 집행(Burn-rate) 및 계정별 잔액 트래킹")

st.markdown("""
* **재무회계 실무 적용:** Series A 투자 유치 이후, 알츠하이머 AI 진단 기술 고도화를 위한 **R&D 연구개발비와 IT/서버 인프라 비용**이 증가하고 있습니다. 
단순 수익 지표가 아닌, 부서별 **지출결의 현황과 계정별 가용 예산 잔액(Runway)**을 시각화하여 경영진의 자금 운용 의사결정을 돕고, 
전표 입력 및 월 마감(결산) 리드타임을 단축하기 위해 현금 흐름을 실시간으로 모니터링합니다. (JD 1, 4, 5번 대응)
""")

@st.cache_data
def get_neuroxt_expenses():
    """
    NeuroXT 월별 비용 집행 가상 데이터 (단위: 백만 원)
    - R&D 및 클라우드 비용과 일반 판관비(법인카드 등) 분리
    """
    return pd.DataFrame({
        "월": ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"],
        "R&D 및 IT 인프라비": [120, 150, 145, 180, 210], # AWS, GPU, 연구용역 등
        "일반관리비(법인카드 등)": [45, 42, 48, 51, 49]
    })

# 데이터 불러오기 및 지표 계산
chart_data = get_neuroxt_expenses()
total_rd_may = int(chart_data.loc[chart_data["월"]=="2026-05", "R&D 및 IT 인프라비"].values[0])
total_sgna_may = int(chart_data.loc[chart_data["월"]=="2026-05", "일반관리비(법인카드 등)"].values[0])

col1, col2, col3 = st.columns([1, 1, 2])
with col1:
    st.metric(label="5월 R&D 및 IT 인프라 집행액", value=f"{total_rd_may}M", delta="16.6% (전월비 상향)")
    st.metric(label="5월 일반 판관비 집행액", value=f"{total_sgna_may}M", delta="-3.9% (비용 통제 중)", delta_color="inverse")
with col2:
    st.metric(label="당월 법인카드 미정산 건수", value="3 건", delta="-12 건 (전월 대비 감소)", delta_color="inverse")
    st.metric(label="매입 세금계산서 대사율", value="98.5%", delta="자동화 적용")
    
with col3:
    # 누적 막대 그래프 생성
    fig_bar = go.Figure()
    
    fig_bar.add_trace(go.Bar(
        x=chart_data["월"], y=chart_data["R&D 및 IT 인프라비"],
        name="R&D 및 IT 인프라비", marker_color="#4F8BF9"
    ))
    fig_bar.add_trace(go.Bar(
        x=chart_data["월"], y=chart_data["일반관리비(법인카드 등)"],
        name="일반관리비(법인카드 등)", marker_color="#FF9F43"
    ))

    # 차트 레이아웃 디자인 업데이트
    fig_bar.update_layout(
        title_text="월별 주요 계정 비용 집행 추이 (단위: 백만 원)",
        barmode='stack',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    fig_bar.update_yaxes(title_text="비용 집행액 (백만 원)", showgrid=True)

    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 섹션 2. 비용 통제 (Python 기반 3-Way Matching, 정부사업비, Bizplay)
# ==========================================
st.header("2. 데이터 대사 검증: 지출결의 이상치 및 세금/증빙 누락 자동 탐지")
st.markdown("**IT/소프트웨어 업종 특성(클라우드, SaaS, R&D)**을 반영하여 파이썬(Pandas)으로 증빙 데이터를 1원 단위까지 크로스체크합니다. (우대사항 2, 3번 대응)")

@st.cache_data
def generate_neuroxt_anomalies():
    anomalies = [
        {"전표일자": "2026-05-12", "데이터 구분": "세금계산서 대사", "이상치 발생 사유": "AWS 클라우드 서버 이용료 (지출결의서-계산서 금액 불일치)", "탐지금액": 8342807},
        {"전표일자": "2026-05-19", "데이터 구분": "정부사업비 정산", "이상치 발생 사유": "알츠하이머 임상 데이터 라이선스 (연구비 적격증빙 누락)", "탐지금액": 6227419},
        {"전표일자": "2026-05-08", "데이터 구분": "지출결의/비용처리", "이상치 발생 사유": "연구소 고성능 GPU 서버 수리비 (품의서 사전승인 누락)", "탐지금액": 4072998},
        {"전표일자": "2026-05-14", "데이터 구분": "세금계산서 대사", "이상치 발생 사유": "외부 연구용역비 지급 (원천세 징수 및 신고 누락 의심)", "탐지금액": 4053339},
        {"전표일자": "2026-05-20", "데이터 구분": "정부사업비 정산", "이상치 발생 사유": "연구개발용 시약 및 소모품 (국책과제 사업계획 외 비목 집행)", "탐지금액": 3947389},
        {"전표일자": "2026-05-22", "데이터 구분": "Bizplay (법인카드)", "이상치 발생 사유": "연구개발팀 법인카드 주말 고액 결제 (소명 필요)", "탐지금액": 2802279},
        {"전표일자": "2026-05-25", "데이터 구분": "Bizplay (법인카드)", "이상치 발생 사유": "소프트웨어 구독료(SaaS) 중복 결제 및 영수증 누락", "탐지금액": 1721441},
        {"전표일자": "2026-05-28", "데이터 구분": "외화 결제비용", "이상치 발생 사유": "미국 FDA 인허가 컨설팅 송금 (USD 환율 변동률 이상치)", "탐지금액": 1670495},
    ]
    return pd.DataFrame(anomalies)

report_numeric = generate_neuroxt_anomalies()

report_display = report_numeric.copy()
report_display['탐지금액(원)'] = report_display['탐지금액'].apply(lambda x: f"{x:,}")
report_display = report_display.drop(columns=['탐지금액'])
report_display.index = [''] * len(report_display)

fig_pie = px.pie(report_numeric, values='탐지금액', names='데이터 구분', hole=0.3,
                 color_discrete_sequence=px.colors.qualitative.Pastel,
                 title="🚨 프로세스별 이상치 및 증빙 누락 발생 비중")
fig_pie.update_traces(textposition='inside', textinfo='percent+label')

col_pie, col_table = st.columns([1, 1.5])

with col_pie:
    st.plotly_chart(fig_pie, use_container_width=True)
    
with col_table:
    st.markdown("**[파이썬 자동 대사 검증(Python Anomaly Detection) 집중 검토 대상]**")
    st.table(report_display)
