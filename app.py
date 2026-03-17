import OpenDartReader
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import streamlit as st # 🚀 웹사이트를 만들어줄 마법 도구!

# 🎨 윈도우 한글 폰트 설정
plt.rc('font', family='NanumGothic') 
plt.rcParams['axes.unicode_minus'] = False 

# ==========================================
# 🌐 웹 페이지 기본 디자인 세팅
# ==========================================
st.set_page_config(page_title="광고업 재무 대시보드", page_icon="📈", layout="wide")
st.title("📈 대한민국 광고업 Top 5 재무 & 주가 대시보드")
st.markdown("**포트폴리오용:** 파이썬(DART API + yfinance)으로 자동 수집된 실시간 데이터입니다.")

# 1. API 키 입력 (민준님의 키로 변경!)
api_key = 'be9b8d7fcf7374d13eba8194d37bea70ca047e0f'

# 로딩 중일 때 멋진 빙글빙글 효과를 줍니다!
with st.spinner('데이터를 실시간으로 수집하고 있습니다. 잠시만 기다려주세요...'):
    dart = OpenDartReader(api_key)
    
    companies = {
        '제일기획': {'dart': '030000', 'yahoo': '030000.KS'},
        '이노션': {'dart': '214320', 'yahoo': '214320.KS'},
        '에코마케팅': {'dart': '230360', 'yahoo': '230360.KQ'},
        '나스미디어': {'dart': '089600', 'yahoo': '089600.KQ'},
        '인크로스': {'dart': '216050', 'yahoo': '216050.KQ'}
    }

    analysis_results = []
    profits_for_chart = {}

    for name, codes in companies.items():
        try:
            # DART 데이터
            data = dart.finstate(codes['dart'], 2024, reprt_code='11011')
            profit = 0
            if data is not None:
                profit_data = data[(data['account_nm'] == '영업이익') & (data['fs_div'] == 'CFS')]
                if profit_data.empty:
                    profit_data = data[(data['account_nm'] == '영업이익') & (data['fs_div'] == 'OFS')]
                if not profit_data.empty:
                    profit = int(str(profit_data['thstrm_amount'].values[0]).replace(',', '')) // 100000000
            
            # Yahoo 데이터
            stock = yf.Ticker(codes['yahoo'])
            hist = stock.history(period="1d")
            current_price = int(hist['Close'].iloc[0]) if not hist.empty else 0
            
            analysis_results.append({
                '기업명': name,
                '2024년 영업이익(억원)': profit,
                '현재 주가(원)': current_price
            })
            profits_for_chart[name] = profit
            
        except Exception as e:
            st.error(f"{name} 데이터를 불러오는 데 실패했습니다.") # 에러도 웹 화면에 예쁘게 띄워줍니다.

    df = pd.DataFrame(analysis_results)
    df = df.sort_values(by='현재 주가(원)', ascending=False).reset_index(drop=True)

# ==========================================
# 📊 웹 화면에 결과물 띄우기!
# ==========================================
st.divider() # 구분선 긋기

col1, col2 = st.columns(2) # 화면을 반으로 나눠서 왼쪽, 오른쪽 배치!

with col1:
    st.subheader("📊 실적 및 주가 데이터")
    # 표의 숫자에 콤마 찍기
    df_display = df.copy()
    df_display['2024년 영업이익(억원)'] = df_display['2024년 영업이익(억원)'].apply(lambda x: f"{x:,}")
    df_display['현재 주가(원)'] = df_display['현재 주가(원)'].apply(lambda x: f"{x:,}")
    st.dataframe(df_display, use_container_width=True)

with col2:
    st.subheader("📉 영업이익 비교 그래프")
    fig, ax = plt.subplots(figsize=(8, 5))
    names = list(profits_for_chart.keys())    
    values = list(profits_for_chart.values()) 
    color_map = {'제일기획': '#003478', '이노션': '#FF6600', '에코마케팅': '#000000', '나스미디어': '#E71D36', '인크로스': '#2EC4B6'}
    colors = [color_map.get(name, '#CCCCCC') for name in names]

    bars = ax.bar(names, values, color=colors, width=0.6)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:,}억', ha='center', va='bottom', fontsize=11)

    # st.pyplot을 이용해 방금 그린 그래프를 웹에 쏩니다!
    st.pyplot(fig)
