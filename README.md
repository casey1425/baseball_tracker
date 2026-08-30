# ⚾ KBO 실시간 중계 & 경기 기록 대시보드 (KBO Live Tracker)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![HTTPX](https://img.shields.io/badge/HTTPX-Fast_HTTP_Client-1E88E5?style=flat)](https://www.python-httpx.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

KBO 한국프로야구 리그의 **실시간 경기 진행 상황 및 과거 경기 기록**을 수집하여 시각화해 주는 인터랙티브 웹 대시보드입니다.  
라인스코어 점수판, 주자 다이아몬드, B-S-O 카운트보드, 실시간 자동 새로고침(Auto-Polling), 타석별 투구 상세 로그 및 팀별 선수 세부 기록실(Boxscore)을 직관적인 UI로 제공합니다.

---

## 📌 주요 기능 (Key Features)

### 1. 📅 날짜별 경기 일정 & 결과 탐색
- **퀵 네비게이션**: `◀ 이전 날`, `오늘`, `다음 날 ▶` 버튼 및 캘린더 피커를 통해 시즌 전체 경기 탐색
- 경기별 최종 점수, 진행 이닝, 경기장 및 선발/승리/패전 투수 정보 실시간 표시
- KBO 10개 구단 기본 홈구장 자동 매핑 및 우천 취소/경기 전 상태별 맞춤형 안내 UI 지원

### 2. ⚡ 실시간 자동 새로고침 (Live Polling)
- `streamlit-autorefresh` 기반의 백그라운드 자동 갱신 토글 지원
- 3초~30초 범위의 갱신 주기 슬라이더 조절 및 실시간 갱신 카운터 표시

### 3. 📊 이닝별 라인스코어보드 (Linescore)
- 1회부터 9회 및 연장전(10~12회)까지 회차별 득점표 자동 확장
- **R(득점), H(안타), E(실책), B(사사구)** 종합 경기 통계 테이블 렌더링

### 4. 🏟️ 주자 다이아몬드 & B-S-O 볼카운트 상황판
- SVG 기반 1루, 2루, 3루 베이스 점유 상태 실시간 황금색 점등 시각화
- Ball(초록), Strike(주황), Out(빨강) 카운트 인디케이터 실시간 렌더링

### 5. 📋 타석별 투구 및 타격 상세 중계
- 타석별 아코디언 인터페이스로 깔끔한 타임라인 제공
- 1구, 2구별 **구종(투심, 슬라이더, 체인지업 등)**, 볼카운트, 텍스트 중계 이벤트 분기 파싱
- 홈런/적시타(🔥), 아웃/삼진(⚾), 사사구(🚶) 등 이벤트 유형별 컬러 배지 강조

### 6. 📊 양 팀 선수별 상세 기록실 (Boxscore)
- `[실시간 중계 피드]`와 `[선수별 기록실]` 탭 분리
- **타자 기록표**: 타순, 포지션, 선수명, 타석, 타수, 득점, 안타, 타점, 홈런, 사사구, 삼진, 시즌 타율
- **투수 기록표**: 등판 순번, 선수명, 소화 이닝, 투구수, 피안타, 피홈런, 실점, 자책점, 사사구, 탈삼진, 시즌 ERA

---

## 🛠️ 기술 스택 (Tech Stack)

| 분류 | 기술 |
|---|---|
| **Language** | Python 3.10+ |
| **Frontend / Dashboard** | Streamlit, HTML5/CSS3 (SVG), `streamlit-autorefresh` |
| **Networking** | HTTPX (HTTP/2 지원 비동기/동기 HTTP 클라이언트) |
| **Data Processing** | Pandas |

---

## 📁 프로젝트 구조 (Directory Structure)

```text
baseball_tracker/
├── app.py              # Streamlit 메인 대시보드 웹 애플리케이션
├── check_api.py        # API 엔드포인트 및 패킷 점검용 유틸리티
├── requirements.txt    # 의존성 라이브러리 목록
├── .gitignore          # Git 제외 파일 목록 (.venv, 캐시 등)
└── README.md           # 프로젝트 문서
