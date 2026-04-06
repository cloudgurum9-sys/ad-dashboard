import streamlit as st
import pandas as pd
import plotly.express as px
import os
import OpenDartReader

# ==========================================
# 💡 하얀 테마(Light) 설정 자동 생성 (다크모드 텍스트 증발 방지)
# ==========================================
if not os.path.exists(".streamlit"):
    os.makedirs(".streamlit")

with open(".streamlit/config.toml", "w", encoding="utf-8") as f:
    f.write('[theme]\nbase="light"\n')
# ==========================================

# 1. 페이지 기본 설정
st.set_page_config(page_title="한라엔컴 재무 대시보드", layout="wide")

# 2. 사이드바 (필터)
st.sidebar.header("분석 필터")
industry_selection = st.sidebar.selectbox("산업군 선택", ["레미콘/건설자재", "제조업 일반"])
company_selection = st.sidebar.selectbox("기업 선택", ["한라엔컴", "동종업계 경쟁사"])

# 3. 메인 타이틀
st.title("📊 한라엔컴 재무결산 및 비용통제 대시보드")
st.markdown("---")

# ==========================================
# 섹션 1. 결산 분석 (24-25년 실제 감사보고서 데이터 매핑)
# ==========================================
st.header("1. 결산 분석: 영업활동현금흐름(OCF) 및 매출채권 리스크 트래킹")

st.markdown("""
* **재무회계 실무 적용:** 최근 건설 경기 침체로 인해 B2B 건설사 대상 **매출채권** 대금 회수 지연(**대손** 리스크)이 커지고 있습니다. 
손익계산서상의 당기순이익에 **연연하지 않고**, 회사의 **실질적인** 현금창출능력(OCF)을 교차 검증하여 **흑자부도** 리스크를 꼼꼼히 모니터링합니다.
""")

@st.cache_data
def get_halla_financials_from_dart(api_key):
    """
    OpenDartReader를 이용해 한라엔컴의 재무제표를 긁어오거나,
    비상장사로 API 조회가 불가능할 경우 최신 감사보고서 실데이터를 매핑합니다.
    """
    try:
        if api_key == "be9b8d7fcf7374d13eba8194d37bea70ca047e0f":
            raise ValueError("API 키 미입력")
            
        dart = OpenDartReader(api_key)
        
        # 한라엔컴 2024년, 2025년 최신 재무제표 추출
        fs_24 = dart.finstate('한라엔컴', 2024)
        fs_25 = dart.finstate('한라엔컴', 2025)
        
        # 당기순이익 및 영업활동현금흐름 추출 후 억원 단위 변환
        ni_24 = int(fs_24.loc[fs_24['account_nm'].str.contains('당기순이익'), 'thstrm_amount'].values[0].replace(',', '')) / 100000000
        ni_25 = int(fs_25.loc[fs_25['account_nm'].str.contains('당기순이익'), 'thstrm_amount'].values[0].replace(',', '')) / 100000000
        ocf_24 = int(fs_24.loc[fs_24['account_nm'].str.contains('영업활동현금흐름'), 'thstrm_amount'].values[0].replace(',', '')) / 100000000
        ocf_25 = int(fs_25.loc[fs_25['account_nm'].str.contains('영업활동현금흐름'), 'thstrm_amount'].values[0].replace(',', '')) / 100000000
        
        return pd.DataFrame({
            "연도": ["2024", "2025"],
            "당기순이익": [round(ni_24), round(ni_25)],
            "영업활동현금흐름(OCF)": [round(ocf_24), round(ocf_25)]
        })
    except Exception as e:
        # 🚨 [실데이터 수동 매핑] 
        # 한라엔컴은 비상장사로 API 자동 추출이 불가하므로 2026.03.31 연결감사보고서 실데이터 반영
        return pd.DataFrame({
            "연도": ["2024", "2025"],
            "당기순이익": [147, 83], 
            "영업활동현금흐름(OCF)": [144, 153] 
        })

# 🔑 DART API 키 입력
MY_DART_API_KEY = "be9b8d7fcf7374d13eba8194d37bea70ca047e0f"

# 데이터 불러오기 및 지표 계산
chart_data = get_halla_financials_from_dart(MY_DART_API_KEY)
ni_2024 = int(chart_data.loc[chart_data["연도"]=="2024", "당기순이익"].values[0])
ni_2025 = int(chart_data.loc[chart_data["연도"]=="2025", "당기순이익"].values[0])
ocf_2024 = int(chart_data.loc[chart_data["연도"]=="2024", "영업활동현금흐름(OCF)"].values[0])
ocf_2025 = int(chart_data.loc[chart_data["연도"]=="2025", "영업활동현금흐름(OCF)"].values[0])

col1, col2 = st.columns([1, 2])
with col1:
    st.metric(label="2025년 당기순이익", value=f"{ni_2025}억", delta=f"{ni_2025 - ni_2024}억 (전년 대비)")
    st.metric(label="2025년 영업활동현금흐름(OCF)", value=f"{ocf_2025}억", delta=f"{ocf_2025 - ocf_2024}억 (전년 대비)", delta_color="inverse")
with col2:
    fig_bar = px.bar(chart_data, x="연도", y=["당기순이익", "영업활동현금흐름(OCF)"], 
                     barmode="group", title="당기순이익 vs 영업활동현금흐름(OCF) 괴리율 (실데이터)")
    fig_bar.update_layout(legend_title_text='구분', xaxis_title="", yaxis_title="금액 (억원)")
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ==========================================
# 섹션 2. 비용 통제 
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

report_numeric = generate_halla_expenses()

report_display = report_numeric.copy()
report_display['청구금액(원)'] = report_display['청구금액'].apply(lambda x: f"{x:,}")
report_display = report_display.drop(columns=['청구금액'])
report_display.index = [''] * len(report_display)

fig_pie = px.pie(report_numeric, values='청구금액', names='발생현장(부서)', hole=0.3,
                 title="🚨 부서별 이상치 결제 금액 비중")
fig_pie.update_traces(textposition='inside', textinfo='percent+label')

col_pie, col_table = st.columns([1, 1.5])

with col_pie:
    st.plotly_chart(fig_pie, use_container_width=True)
    
with col_table:
    st.markdown("**[전표 집중 검토 대상 (고액 300만 원 이상 및 주말 결제 건)]**")
    st.table(report_display)
