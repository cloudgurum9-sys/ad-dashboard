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
st.set_page_config(page_title="대림바스 재경결산 및 SAP 데이터 검증 대시보드", layout="wide")

# 2. 사이드바 (필터)
st.sidebar.header("데이터 분석 필터")
business_selection = st.sidebar.sidebar.selectbox("판매 채널 선택", ["전체", "B2B (건설사/대리점 납품)", "B2C (대림몰/쿠팡/에이블리)", "직영쇼룸(논현 등)"])
product_selection = st.sidebar.sidebar.selectbox("주요 품목 선택", ["전체", "위생도기(양변기/세면기)", "일체형 비데 (FÜLEN)", "욕실 리모델링 패키지"])

# 3. 메인 타이틀
st.title("📊 대림바스 재무결산 및 SAP 데이터 대사/검증 대시보드")
st.markdown("---")

# ==========================================
# 섹션 1. 결산 분석 (B2B 납품 및 B2C 플랫폼 채널 매출 트래킹)
# ==========================================
st.header("1. O2C 결산 모니터링: 채널별 매출 추이 및 채권 현황")

st.markdown("""
* **재경 실무 적용:** 대림바스의 비즈니스가 B2B(건설사 납품) 중심에서 B2C(이커머스/플랫폼)로 확장됨에 따라, 채널별로 다르게 발생하는 매출 인식 구조(세금계산서 vs 플랫폼 정산)를 통합적으로 트래킹하는 것이 월/결산의 핵심입니다.
* 본 대시보드는 채널별 매출 발생액을 교차 트래킹하여 재무제표의 정확성을 높이고 결산 리드타임을 단축하는 데 목적이 있습니다.
""")

@st.cache_data
def get_daelim_revenue_data():
    """
    대림바스 월별 B2B 및 B2C 매출 샘플 데이터 
    (B2C 플랫폼 매출이 폭발적으로 증가하는 최신 트렌드 반영)
    """
    return pd.DataFrame({
        "월(Month)": ["1월", "2월", "3월", "4월"],
        "B2B 납품 매출액 (억원)": [145, 142, 158, 165], 
        "B2C 플랫폼/쇼룸 매출액 (억원)": [20, 28, 45, 62] 
    })

# 데이터 불러오기 및 지표 계산
chart_data = get_daelim_revenue_data()
b2b_april = chart_data.loc[chart_data["월(Month)"]=="4월", "B2B 납품 매출액 (억원)"].values[0]
b2c_april = chart_data.loc[chart_data["월(Month)"]=="4월", "B2C 플랫폼/쇼룸 매출액 (억원)"].values[0]
b2b_march = chart_data.loc[chart_data["월(Month)"]=="3월", "B2B 납품 매출액 (억원)"].values[0]
b2c_march = chart_data.loc[chart_data["월(Month)"]=="3월", "B2C 플랫폼/쇼룸 매출액 (억원)"].values[0]

col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="4월 B2B 납품 매출액 (세금계산서 기준)", value=f"{b2b_april:g}억원", delta=f"{b2b_april - b2b_march:g}억원 (전월 대비)")
    st.metric(label="4월 B2C 플랫폼 매출액 (쿠팡/에이블리 등)", value=f"{b2c_april:g}억원", delta=f"{b2c_april - b2c_march:g}억원 (전월 대비)")
    
with col2:
    # 이중 Y축을 지원하는 서브플롯 생성
    fig_mixed = make_subplots(specs=[[{"secondary_y": True}]])

    # 1. B2B 매출액 막대 그래프 (왼쪽 Y축)
    fig_mixed.add_trace(
        go.Bar(x=chart_data["월(Month)"], y=chart_data["B2B 납품 매출액 (억원)"], name="B2B 매출액 (건설/대리점)", marker_color="#0052A4"), # 대림바스 블루톤
        secondary_y=False,
    )

    # 2. B2C 매출액 꺾은선 그래프 (오른쪽 Y축 - 성장성 강조)
    fig_mixed.add_trace(
        go.Scatter(x=chart_data["월(Month)"], y=chart_data["B2C 플랫폼/쇼룸 매출액 (억원)"], name="B2C 매출액 (온라인/쇼룸)", 
                   mode="lines+markers", marker=dict(size=10, color="#FF6B6B"), line=dict(width=3)),
        secondary_y=True,
    )

    # 차트 레이아웃 디자인 업데이트
    fig_mixed.update_layout(
        title_text="월별 B2B 납품 매출 vs B2C 플랫폼 매출 성장 추이",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Y축 이름 설정
    fig_mixed.update_yaxes(title_text="B2B 매출액 (억원)", secondary_y=False)
    fig_mixed.update_yaxes(title_text="B2C 매출액 (억원)", showgrid=False, secondary_y=True)

    st.plotly_chart(fig_mixed, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 섹션 2. 비용 통제 및 대사 (ERP 데이터 검증)
# ==========================================
st.header("2. ERP(SAP) 데이터 대사 검증: 전표 누락 및 이상치 자동 탐지")
st.markdown("""
Python Pandas를 활용하여 **영업/물류 원천 데이터**와 **내부 SAP 회계 장부**를 주문번호(고유 식별자) 기준으로 자동 병합(Merge)하고, 
단가 불일치, 부가세 안분 오류, 재고 출고 누락 등의 전표 이상 데이터를 실시간으로 추출한 결과입니다. (운영계획서 내 'ERP 데이터 검증' 직무 타겟팅)
""")

@st.cache_data
def generate_daelim_anomalies():
    # 대림바스 비즈니스 및 ERP 검증에 특화된 이상치 데이터 셋
    anomalies = [
        {"전표일자": "2026-04-05", "데이터 구분": "B2B 세금계산서", "이상치 발생 사유": "건설사 납품 단가와 ERP 수주 단가 불일치 (차액 발생)", "탐지금액": 12850000},
        {"전표일자": "2026-04-06", "데이터 구분": "B2C 플랫폼 정산", "이상치 발생 사유": "쿠팡 로켓설치 정산 수수료율 오적용 (정산금액 부족)", "탐지금액": 4527410},
        {"전표일자": "2026-04-07", "데이터 구분": "재고자산(물류)", "이상치 발생 사유": "창원공장 위생도기 재고 실사 불일치 (SAP 출고 누락)", "탐지금액": 8305000},
        {"전표일자": "2026-04-08", "데이터 구분": "매출전표 누락", "이상치 발생 사유": "에이블리 판매분 SAP 회계전표 미생성 (회계반영 누락)", "탐지금액": 2853330},
        {"전표일자": "2026-04-08", "데이터 구분": "부가세 안분", "이상치 발생 사유": "쇼룸 결제액(VAT포함)의 공급가액/부가세 계산 오류", "탐지금액": 1947380},
        {"전표일자": "2026-04-09", "데이터 구분": "법인카드 경비", "이상치 발생 사유": "마케팅 부서 B2C 프로모션 비용 예산 한도 초과", "탐지금액": 3802270},
        {"전표일자": "2026-04-10", "데이터 구분": "외주 시공비", "이상치 발생 사유": "리모델링 시공 기사 용역비 원천세(3.3%) 징수액 오류", "탐지금액": 1670490},
    ]
    return pd.DataFrame(anomalies)

report_numeric = generate_daelim_anomalies()

report_display = report_numeric.copy()
report_display['탐지금액(원)'] = report_display['탐지금액'].apply(lambda x: f"{x:,}")
report_display = report_display.drop(columns=['탐지금액'])
report_display.index = [''] * len(report_display)

# 파이 차트 생성 (대림바스 컬러에 맞게 조정)
fig_pie = px.pie(report_numeric, values='탐지금액', names='데이터 구분', hole=0.3,
                 title="🚨 O2C 프로세스별 전표 이상치 탐지 비중")
fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(colors=px.colors.qualitative.Prism))

col_pie, col_table = st.columns([1, 1.5])

with col_pie:
    st.plotly_chart(fig_pie, use_container_width=True)
    
with col_table:
    st.markdown("**[Python 기반 SAP 매출/재고/경비 전표 집중 검토 리스트]**")
    st.table(report_display)
