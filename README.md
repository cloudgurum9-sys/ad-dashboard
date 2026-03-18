# 📊 광고업 주요 상장사 재무 분석 대시보드 (v2.0)

이 프로젝트는 파이썬과 Streamlit을 활용해 대한민국 대표 광고 기업들의 **실시간 주가와 수익성 지표**를 시각화한 대시보드입니다.

## 🛠 주요 기술 스택
- **Language**: Python 3.x
- **Framework**: Streamlit (Cloud Deployment)
- **Data**: yfinance (실시간 주가), DART API 기반 재무 데이터 분석
- **Design**: Custom Dark Theme & Responsive Sidebar Filter

## 🚀 주요 기능
1. **Interactive Filter**: 사이드바를 통해 분석하고 싶은 기업만 실시간으로 선택 및 비교 가능.
2. **Profitability Analysis**: 매출액 대비 영업이익률($$영업이익/매출 \times 100$$) 자동 계산 및 랭킹 정렬.
3. **Data Caching**: `@st.cache_data`를 적용하여 API 호출 속도를 대폭 개선.
4. **Professional UI**: 다크 테마를 적용하여 데이터 가독성 극대화.

## 📈 분석 대상
제일기획, 이노션, 나스미디어, 에코마케팅, 인크로스

---
*본 프로젝트는 데이터 분석 및 회계 실무 역량을 증명하기 위해 제작되었습니다.*
