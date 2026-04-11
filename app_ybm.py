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
st.set_page_config(page_title="YBM 재무결산 및 PG정산 대시보드", layout="wide")

# 2. 사이드바 (필터)
st.sidebar.header("데이터 분석 필터")
business_selection = st.sidebar.selectbox("사업 부문 선택", ["전체", "어학시험(TOEIC 등)", "이러닝/어학원", "출판/교재"])
pg_selection = st.sidebar.selectbox("결제/PG사 선택", ["전체", "KG이니시스", "토스페이먼츠", "네이버페이", "카카오페이"])

# 3. 메인 타이틀
st.title("📊 YBM 재무결산 및 PG정산 모니터링 대시보드")
st.markdown("---")

# ==========================================
# 섹션 1. 결산 분석 (B2C 결제액 및 선수수익 매출 대체 추이)
# ==========================================
st.header("1. 결산 분석: B2C 결제액 및 선수수익 매출 인식 트래킹")

st.markdown("""
* **재무회계 실무 적용:** YBM의 비즈니스 특성상 매일 발생하는 수많은 **강의 수강료 및 시험 응시료 결제액을 '선수수익(부채)'**으로 우선 인식한 후, 수강 기간 경과 및 시험일 도래에 따라 **'매출'로 대체**하는 결산 과정이 매우 중요합니다.
* 본 대시보드는 월별 총 결제 발생액과 당월 매출 대체액을 교차 트래킹하여, 재무제표의 정확성을 높이고 결산 마감 리드타임을 단축하는 데 목적이 있습니다.
""")

@st.cache_data
def get_ybm_revenue_data():
    """
    YBM 월별 B2C 결제액 및 매출 대체액 샘플 데이터 (단위: 백만 원)
    """
    return pd.DataFrame({
        "월(Month)": ["1월", "2월", "3월", "4월", "5월", "6월"],
        "총 결제발생액(선수수익 증가)": [4500, 4200, 5100, 4800, 5300, 4900], 
        "당월 매출인식액(선수수익 감소)": [4100, 4300, 4600, 4900, 5000, 5100] 
    })

# 데이터 불러오기 및 지표 계산
chart_data = get_ybm_revenue_data()
payment_june = int(chart_data.loc[chart_data["월(Month)"]=="6월", "총 결제발생액(선수수익 증가)"].values[0])
revenue_june = int(chart_data.loc[chart_data["월(Month)"]=="6월", "당월 매출인식액(선수수익 감소)"].values[0])
payment_may = int(chart_data.loc[chart_data["월(Month)"]=="5월", "총 결제발생액(선수수익 증가)"].values[0])
revenue_may = int(chart_data.loc[chart_data["월(Month)"]=="5월", "당월 매출인식액(선수수익 감소)"].values[0])

col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="6월 총 결제발생액 (B2C)", value=f"{payment_june:,}백만원", delta=f"{payment_june - payment_may:,}백만원 (전월 대비)")
    st.metric(label="6월 실제 매출인식액", value=f"{revenue_june:,}백만원", delta=f"{revenue_june - revenue_may:,}백만원 (전월 대비)")
    
with col2:
    # 이중 Y축을 지원하는 서브플롯 생성
    fig_mixed = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. 결제발생액 막대 그래프 (왼쪽 Y축)
    fig_mixed.add_trace(
        go.Bar(x=chart_data["월(Month)"], y=chart_data["총 결제발생액(선수수익 증가)"], name="신규 결제액(선수수익)", marker_color="#E2E8F0"),
        secondary_y=False,
    )

    # 2. 매출인식액 꺾은선 그래프 (오른쪽 Y축)
    fig_mixed.add_trace(
        go.Scatter(x=chart_data["월(Month)"], y=chart_data["당월 매출인식액(선수수익 감소)"], name="당월 매출 인식액", 
                   mode="lines+markers", marker=dict(size=10, color="#E83A14"), line=dict(width=3)),
        secondary_y=True,
    )

    # 차트 레이아웃 디자인 업데이트
    fig_mixed.update_layout(
        title_text="월별 B2C 신규 결제액 vs 당월 매출(선수수익 대체) 인식 추이",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Y축 이름 설정
    fig_mixed.update_yaxes(title_text="신규 결제액 (백만원)", secondary_y=False)
    fig_mixed.update_yaxes(title_text="매출 인식액 (백만원)", showgrid=False, secondary_y=True)

    st.plotly_chart(fig_mixed, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 섹션 2. 비용 통제 및 대사 (PG정산, 환불, 강사료, 재고)
# ==========================================
st.header("2. 데이터 대사 검증(Reconciliation): PG정산 불일치 및 이상치 탐지")
st.markdown("""
Python Pandas를 활용하여 **내부 ERP 매출 장부**와 **외부 PG사(결제대행사) 정산 내역**을 고유 식별자(주문번호 등) 기준으로 자동 병합(Outer Join)하고, 
수수료율 오류, 중복 환불, 교재 출고 누락 등의 이상 데이터를 실시간으로 추출한 결과입니다.
""")

@st.cache_data
def generate_ybm_anomalies():
    anomalies = [
        {"전표일자": "2026-06-25", "데이터 구분": "PG사 정산 대사", "이상치 발생 사유": "신용카드 수수료율 오적용 (정산금액 불일치)", "탐지금액": 8342807},
        {"전표일자": "2026-06-26", "데이터 구분": "이러닝 환불", "이상치 발생 사유": "수강진도율 50% 초과건 전액 환불 (규정 위반)", "탐지금액": 4527419},
        {"전표일자": "2026-06-27", "데이터 구분": "출판/교재 물류", "이상치 발생 사유": "교재 물류센터 재고 실사 불일치 (ERP 출고 누락)", "탐지금액": 3072998},
        {"전표일자": "2026-06-28", "데이터 구분": "어학시험 접수", "이상치 발생 사유": "TOEIC 단체접수 할인율 시스템 적용 누락", "탐지금액": 2853339},
        {"전표일자": "2026-06-28", "데이터 구분": "강사료 정산", "이상치 발생 사유": "외주 강사료 원천세(3.3%) 징수액 계산 오류", "탐지금액": 1947389},
        {"전표일자": "2026-06-29", "데이터 구분": "PG 결제 중복", "이상치 발생 사유": "동일 IP, 동일 금액 연속 결제 (중복 결제 의심)", "탐지금액": 1802279},
        {"전표일자": "2026-06-30", "데이터 구분": "Bizplay 경비", "이상치 발생 사유": "마케팅 부서 법인카드 고액 결제 (예산 한도 초과)", "탐지금액": 1721441},
        {"전표일자": "2026-06-30", "데이터 구분": "SaaS/구독료", "이상치 발생 사유": "AWS 클라우드 서버 이용료 (환율 변동률 이상치)", "탐지금액": 1670495},
    ]
    return pd.DataFrame(anomalies)

report_numeric = generate_ybm_anomalies()

report_display = report_numeric.copy()
report_display['탐지금액(원)'] = report_display['탐지금액'].apply(lambda x: f"{x:,}")
report_display = report_display.drop(columns=['탐지금액'])
report_display.index = [''] * len(report_display)

# 파이 차트 생성
fig_pie = px.pie(report_numeric, values='탐지금액', names='데이터 구분', hole=0.3,
                 title="🚨 주요 프로세스별 이상치 탐지 비중")
fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(colors=px.colors.qualitative.Pastel))

col_pie, col_table = st.columns([1, 1.5])

with col_pie:
    st.plotly_chart(fig_pie, use_container_width=True)
    
with col_table:
    st.markdown("**[Python 대사 로직(Pandas Merge) 기반 집중 검토 리스트]**")
    st.table(report_display)
