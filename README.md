# ⚾ KBO 실시간 중계 & 경기 기록 대시보드 (KBO Live Tracker)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/python/)
[![HTTPX](https://img.shields.io/badge/HTTPX-Fast_HTTP_Client-1E88E5?style=flat)](https://www.python-httpx.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

KBO 한국프로야구 리그의 **실시간 경기 진행 상황 및 과거 경기 기록**을 수집하여 시각화해 주는 인터랙티브 웹 대시보드입니다.  
라인스코어 점수판, SVG 기반 주자 다이아몬드와 B-S-O 카운트보드, 실시간 하이라이트 타임라인 피드, 선수별 박스스코어, 그리고 Plotly 기반의 실시간 승리 확률(Win Expectancy) 및 승부처(WPA) 분석 차트를 제공합니다.

---

## 📌 주요 기능 (Key Features)

### 1. 📅 날짜별 경기 일정 & 실시간 자동 갱신
- **KST 기준 오늘 날짜 자동 기본값 진입** 및 `◀ 이전`, `오늘`, `다음 ▶` 날짜 네비게이션 피커 지원
- KBO 10개 구단 기본 홈구장 자동 매핑 및 우천 취소/경기 전 상태별 맞춤형 안내 UI 지원
- `streamlit-autorefresh` 기반의 백그라운드 자동 폴링 토글 및 갱신 주기(3초~30초) 조절 지원

### 2. 📊 라인스코어보드 (Linescore) & 실시간 상황판
- 1회부터 9회 및 연장전까지 회차별 점수판 자동 확장 및 **R(득점), H(안타), E(실책), B(사사구)** 종합 경기 통계 렌더링
- SVG 기반 1·2·3루 베이스 점유 상태(황금색 점등) 및 Ball(초록)·Strike(주황)·Out(빨강) 카운트 인디케이터 실시간 시각화

### 3. ⏱️ 주요 장면 & 득점 하이라이트 피드 (Highlight Timeline)
- 경기 중 발생한 **홈런, 득점/적시타, 안타/장타, 선수 교체, 승부처/삼진** 이벤트를 실시간으로 추출하여 타임라인 카드로 시각화
- 이벤트 카테고리 필터 칩을 통해 원하는 주요 장면만 선별 조회 가능

### 4. 📈 실시간 승리 확률(Win Expectancy) & WPA 승부처 그래프
- `ThreadPoolExecutor`를 통한 1회부터 경기 종료까지의 전 이닝 타석별 승리 확률 및 WPA(승리기여도) 데이터 고속 병렬 수집
- **전체 경기 vs 특정 이닝(1회, 2회 ... 연장)** 선택 필터를 지원하는 Plotly 인터랙티브 라인 차트 제공
- 홈런 및 결정적 클러치 상황(WPA 변동폭 10% 이상)에 황금 마커(⭐) 표시 및 하단 주요 승부처 요약 피드 연동

### 5. 📋 타석별 상세 투구 중계 & 선수별 박스스코어 (Boxscore)
- 타석별 아코디언 인터페이스로 1구, 2구별 구종(직구, 슬라이더, 포크 등), 구속, 볼카운트 상세 중계 제공
- 홈팀 / 원정팀 탭 분리를 통한 양 팀 타자(타순, 타수, 안타, 홈런, 타점, 시즌타율 등) 및 투수(이닝, 투구수, 피안타, 자책, 탈삼진, 시즌ERA 등) 세부 기록실 렌더링

---

## 🛠️ 기술 스택 (Tech Stack)

| 분류 | 기술 |
|---|---|
| **Language** | Python 3.10+ |
| **Frontend / Dashboard** | Streamlit, HTML5/CSS3 (SVG), `streamlit-autorefresh` |
| **Data Visualization** | Plotly (인터랙티브 승리 확률 곡선 및 승부처 마커) |
| **Networking & Concurrency** | HTTPX (HTTP Client), `concurrent.futures.ThreadPoolExecutor` |
| **Data Processing** | Pandas |

---

## 📁 프로젝트 구조 (Directory Structure)

```text
baseball_tracker/
├── app.py              # Streamlit 메인 대시보드 웹 애플리케이션
├── check_api.py        # API 엔드포인트 및 패킷 점검용 유틸리티
├── requirements.txt    # 의존성 라이브러리 목록 (Streamlit, Plotly, HTTPX, Pandas 등)
├── .gitignore          # Git 제외 파일 목록 (.venv, 캐시 등)
└── README.md           # 프로젝트 문서
