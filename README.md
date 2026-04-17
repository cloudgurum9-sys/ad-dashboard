# 📊 YBM 재무결산 및 PG정산 자동화 대시보드

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)

## 💡 프로젝트 개요
본 프로젝트는 에듀테크 리딩 기업 **YBM의 비즈니스 특성(방대한 B2C 소액 결제, 선수수익 인식 구조)**을 반영하여 구축한 **재무결산 및 데이터 대사 모니터링 대시보드**입니다. 
단순한 데이터 시각화를 넘어, 실제 재무팀의 **결산 리드타임 단축**과 **수작업(엑셀) 대사 과정의 비효율 및 오류**를 해결하는 데 목적이 있습니다.

- **URL:** [대시보드 바로가기 링크 삽입] *(※ Streamlit Cloud 등에 배포한 링크가 있다면 추가하세요)*

---

## 🔑 핵심 기능 및 비즈니스 임팩트

### 1. B2C 결제액(선수수익) 및 당월 매출 대체 트래킹
YBM의 핵심 회계 이슈인 '선수수익(수강료/응시료 선결제)'이 실제 기간 경과에 따라 '당월 매출'로 인식되는 흐름을 교차 추적합니다.
- **주요 기능:** 월별 총 결제 발생액(부채 증가)과 당월 매출 인식액(부채 감소/매출 증가)을 이중 축 그래프(Bar & Line)로 시각화
- **기대 효과:** 부서 간 결제 데이터 불일치 방지 및 직관적인 회사의 현금 흐름 및 실제 수익(매출) 현황 파악

### 2. PG 정산 불일치 및 비용 대사 자동화 (이상치 탐지)
수백만 건의 내부 ERP 매출 장부와 외부 PG사(결제대행사) 정산 내역을 파이썬 Pandas를 활용해 병합(Merge)하고 검증합니다.
- **주요 기능:** 수수료율 오적용, 중복 환불, 강사료 원천세 오류, 교재 출고 누락 등 수작업으로 찾기 힘든 **차액 및 이상 데이터(Anomaly)**를 추출하여 집중 검토 리스트로 제공
- **기대 효과:** 매월 반복되는 PG 대사 실무의 야근 최소화, 수수료 누수 방지 및 결산 마감 프로세스 효율화

---

## 🛠 기술 스택 (Tech Stack)

- **Language:** Python 3.x
- **Web Framework:** Streamlit (웹 대시보드 UI 구현 및 라이트 테마 자동 설정)
- **Data Manipulation:** Pandas (데이터 전처리, 결측치 처리, ERP/PG 데이터 Merge)
- **Data Visualization:** Plotly Express / Graph_Objects (이중 Y축 차트, 파이 차트 등 동적 시각화)

---

## 🚀 설치 및 실행 방법 (How to Run)

1. **Repository 클론**
```bash
git clone [https://github.com/본인아이디/리포지토리이름.git](https://github.com/본인아이디/리포지토리이름.git)
