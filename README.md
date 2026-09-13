# ⚾ KBO 실시간 중계 & 경기 기록 대시보드 (KBO Live Tracker)

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?style=flat&logo=next.js&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/python/)
[![HTTPX](https://img.shields.io/badge/HTTPX-Fast_HTTP_Client-1E88E5?style=flat)](https://www.python-httpx.org/)
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

KBO 한국프로야구 리그의 **실시간 경기 진행 상황 및 과거 경기 기록**을 수집하여 시각화해 주는 인터랙티브 웹 대시보드입니다.  
라인스코어 점수판, SVG 기반 주자 다이아몬드와 B-S-O 카운트보드, 실시간 하이라이트 타임라인 피드, 선수별 박스스코어, 그리고 Plotly 기반의 실시간 승리 확률(Win Expectancy) 및 승부처(WPA) 분석 차트를 제공합니다.

---

## 📌 주요 기능 (Key Features)

### 1. 📅 날짜별 경기 일정 & 실시간 자동 갱신
- **KST 기준 오늘 날짜 자동 기본값 진입** 및 `◀ 이전`, `오늘`, `다음 ▶` 날짜 네비게이션 피커 지원
- Next.js 대시보드는 날짜 표시를 누르면 달력이 열리고, 별도의 `오늘` 버튼으로 현재 날짜에 즉시 복귀
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
- 선수명·중계 문장 검색, 이닝 선택, 홈런·안타·삼진·사사구·아웃·교체 결과 유형 필터 지원
- 홈팀 / 원정팀 탭 분리를 통한 양 팀 타자(타순, 타수, 안타, 홈런, 타점, 시즌타율 등) 및 투수(이닝, 투구수, 피안타, 자책, 탈삼진, 시즌ERA 등) 세부 기록실 렌더링

### 6. 📝 경기 종료 요약
- 종료 경기의 최종 결과, 리드 교체 횟수, 최대 점수 차와 타자 MVP 후보를 자동 요약
- WPA 변동폭을 기준으로 승부를 가른 장면과 주요 승부처 TOP 5 제공

### 7. 🏆 팀 순위와 최근 흐름
- KBO 실시간 순위, 승·무·패, 승률, 최근 10경기, 연승·연패와 시즌 득실차 제공
- 1위 및 5위와의 게임 차, 응원팀 강조, 응원팀의 다음 경기 정보 표시

### 8. 🖥️ Next.js 실시간 통합 대시보드
- 날짜별 전체 경기 카드와 응원팀 우선 선택, 선택 경기 라인스코어를 반응형 화면으로 제공
- 경기 현황·상세 중계·경기 분석·선수 기록·경기 요약을 독립된 탭으로 구성해 필요한 정보에 바로 접근
- 10초 자동 갱신, 갱신 시각과 연결 오류 상태 표시, 실시간 갱신 ON/OFF 지원
- SVG 승리 확률 차트, 주요 장면 카테고리 필터와 시즌 팀 순위를 한 화면에 통합
- 승리 확률 그래프의 모든 구간에서 이닝·점수·타석 결과·WPA를 보여주는 마우스/터치 툴팁 지원
- 상세 중계 탭에서 선수·중계 내용 검색, 이닝과 결과 유형 필터, 투구별 구종·구속·B/S/O 확인 지원
- 선수 기록 탭에서 양 팀 타자·투수 박스스코어를 전환해 확인하고, 종료 경기에는 자동 요약 탭 제공
- 종료 경기 다시보기에서 이전·다음 타석 이동, 자동 재생, 속도 조절, 승리 확률 동기화와 주요 장면 바로가기 지원
- `/games/{gameId}?date=YYYY-MM-DD&tab=...` 고유 URL로 선택 경기와 탭을 새로고침 후에도 복원하고 링크 복사 지원
- 응원팀을 브라우저에 저장하고 다음 접속에서도 유지
- 외부 이미지 차단을 피하는 허용 도메인 기반 엠블럼 프록시와 이미지 실패 대체 UI 제공
- 현재 투수·타자, 주자 다이아몬드, B/S/O 카운트, 최근 5개 투구와 마지막 타석 결과를 실시간 상황판으로 제공

---

## 🛠️ 기술 스택 (Tech Stack)

| 분류 | 기술 |
|---|---|
| **Language** | Python 3.10+, TypeScript 5 |
| **Frontend / Dashboard** | Next.js 16, React 19, Streamlit, HTML5/CSS3 (SVG) |
| **Backend API** | FastAPI, Pydantic, Uvicorn |
| **Data Visualization** | Plotly (인터랙티브 승리 확률 곡선 및 승부처 마커) |
| **Networking & Concurrency** | HTTPX (HTTP Client), `concurrent.futures.ThreadPoolExecutor` |
| **Data Processing** | Pandas |

---

## 📁 프로젝트 구조 (Directory Structure)

```text
baseball_tracker/
├── app.py              # Streamlit 메인 대시보드 웹 애플리케이션
├── frontend/           # Next.js + TypeScript 실시간 대시보드
│   ├── app/            # App Router 페이지와 전역 스타일
│   ├── components/     # 경기 현황과 승리 확률 UI
│   ├── lib/            # FastAPI 클라이언트
│   ├── types/          # API 응답 타입
│   └── package-lock.json # npm 의존성 잠금 파일
├── services/api/       # FastAPI 백엔드와 네이버 스포츠 비동기 클라이언트
├── game_detail_data.py # 상세 중계와 선수 기록 API 응답 정규화
├── game_summary.py     # 경기 종료 요약 계산
├── highlight_events.py # 하이라이트 이벤트 추출
├── live_situation.py   # 현재 타석·주자·카운트·최근 투구 정규화
├── standings.py        # 팀 순위 데이터 변환
├── win_probability.py  # 승리 확률 데이터 변환
├── check_api.py        # API 엔드포인트 및 패킷 점검용 유틸리티
├── requirements.txt    # Streamlit 및 FastAPI 실행 의존성
├── render.yaml         # FastAPI와 Next.js 공개 배포 Blueprint
├── .gitignore          # Git 제외 파일 목록 (.venv, 캐시 등)
└── README.md           # 프로젝트 문서
```

---

## 🚀 실행 방법

필수 환경:

- Python 3.10 이상
- Node.js 20.9 이상 및 npm

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Streamlit 대시보드:

```bash
streamlit run app.py
```

FastAPI 백엔드:

```bash
uvicorn services.api.app.main:app --reload --port 8000
```

Next.js 실시간 대시보드(새 터미널):

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

- 대시보드: `http://localhost:3000`
- API 주소를 변경하려면 `frontend/.env.local`의 `NEXT_PUBLIC_API_BASE_URL`을 수정합니다.

- API 문서: `http://localhost:8000/docs`
- OpenAPI 스키마: `http://localhost:8000/openapi.json`
- 프런트엔드 허용 출처: `KBO_CORS_ORIGINS` 환경 변수로 설정(기본값 `http://localhost:3000` 포함)

## 🌐 Render 공개 배포

저장소 루트의 `render.yaml`은 FastAPI와 Next.js를 각각 Render Web Service로 생성합니다. 프런트엔드는 `/api/kbo/*` 프록시를 통해 Render 내부망의 FastAPI를 호출하므로 공개 API 주소나 CORS 값을 따로 연결할 필요가 없습니다.

1. [Render Blueprint 생성 화면](https://dashboard.render.com/blueprints)에서 **New Blueprint Instance**를 선택합니다.
2. GitHub의 `baseball_tracker` 저장소를 연결하고 `render.yaml`을 승인합니다.
3. 두 서비스의 첫 배포가 완료되면 `baseball-tracker-web` 서비스에 표시된 `onrender.com` 주소로 접속합니다.

Render 무료 Web Service는 일정 시간 요청이 없으면 중지되므로 첫 접속 시 다시 시작되는 시간이 걸릴 수 있습니다. 이후 `main` 브랜치에 푸시한 변경은 두 서비스에 자동으로 배포됩니다.

### 주요 API

| Method | Endpoint | 설명 |
|---|---|---|
| GET | `/api/v1/health` | 서버 상태 확인 |
| GET | `/api/v1/games?date=YYYY-MM-DD` | 날짜별 경기 목록 |
| GET | `/api/v1/games/{game_id}` | 경기 상세 정보 |
| GET | `/api/v1/games/{game_id}/relay` | 최신 또는 특정 이닝 중계 |
| GET | `/api/v1/games/{game_id}/highlights` | 주요 하이라이트 |
| GET | `/api/v1/games/{game_id}/win-probability` | 승리 확률과 WPA |
| GET | `/api/v1/games/{game_id}/dashboard` | 경기 현황·상세 중계·분석·선수 기록·종료 요약 통합 응답 |
| GET | `/api/v1/games/{game_id}/summary` | 종료 경기 요약 |
| GET | `/api/v1/standings` | 시즌 순위와 최근 흐름 |
| GET | `/api/v1/teams/{team_name}/next-game` | 팀의 다음 경기 |
