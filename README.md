# BotServer

Mattermost 슬래시 커맨드와 OpenAI Assistant API를 연동하는 챗봇 서버.  
사용자가 Mattermost에서 질문을 입력하면 OpenAI Assistant가 답변을 생성해 채널로 응답한다.

---

## 프로젝트 구조

```
botserver/
├── app.py              ← 메인 서버 (여기만 실행하면 됨)
├── insert.py           ← PostgreSQL 성능 테스트 데이터 벌크 입력 유틸
├── with.sql            ← ClickHouse 분석 쿼리
├── .env                ← 실제 API 키 (절대 커밋 금지)
├── .env.example        ← 환경 변수 템플릿
├── .gitignore
├── requirements.txt
├── botserver.log       ← 실행 시 자동 생성되는 로그 파일
└── archive/            ← 개발 과정 실험 파일 보관 (참고용)
    ├── chatres1.py     ← app.py의 전신 (비동기 + 인용 제거)
    ├── chat1234.py     ← 진행 카운트다운 버전
    ├── chatbot.py      ← OpenAI Assistant 기본 연동
    ├── bot.py          ← Mattermost 웹훅 기본 핸들러
    └── ...
```

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| **비동기 처리** | 요청 즉시 "생성 중" 메시지 반환 → 백그라운드에서 처리 후 최종 응답 전송 |
| **대화 맥락 유지** | 사용자 ID별 OpenAI Thread 재사용 → 이전 대화를 기억함 |
| **대화 초기화** | `/intermax reset` 또는 `/intermax 초기화` 입력 시 대화 기록 리셋 |
| **멀티 어시스턴트 라우팅** | 키워드에 따라 다른 Assistant ID로 자동 분기 |
| **타임아웃 처리** | 설정 시간(기본 120초) 초과 시 오류 응답 전송 |
| **실패 상태 처리** | `failed`, `cancelled`, `expired` 상태 감지 및 오류 메시지 반환 |
| **인용 제거** | OpenAI 응답의 `【4:1†source】` 형식 마커 자동 제거 |
| **토큰 인증** | Mattermost 웹훅 토큰 검증 |
| **구조화 로깅** | 콘솔 + `botserver.log` 파일에 동시 기록 |

---

## 메시지 흐름

```
Mattermost 사용자
      │ (슬래시 커맨드)
      ▼
app.py /intermax
      │
      ├─► 즉시 "생성 중..." 반환 (ephemeral)
      │
      └─► 백그라운드 Thread 시작
               │
               ├── 사용자 ID로 기존 스레드 조회 or 신규 생성
               │
               ├── 키워드로 어시스턴트 ID 결정
               │
               ├── OpenAI Thread에 메시지 추가 & Run 시작
               │
               ├── 5초 간격 폴링 (최대 120초)
               │
               ├── 완료 → 인용 마커 제거
               │
               └── Mattermost response_url로 최종 응답 POST
```

---

## 빠른 시작

### 1. 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 열어 실제 값으로 교체:

```env
OPENAI_API_KEY=sk-proj-...
ASSISTANT_ID=asst_...
MATTERMOST_TOKEN=your-token
```

### 3. 실행

```bash
python app.py
```

서버가 `0.0.0.0:5000`에서 시작된다.

---

## 환경 변수

| 변수 | 필수 | 기본값 | 설명 |
|------|------|--------|------|
| `OPENAI_API_KEY` | ✅ | - | OpenAI API 키 |
| `ASSISTANT_ID` | ✅ | - | 기본 OpenAI Assistant ID |
| `MATTERMOST_TOKEN` | - | (검증 안 함) | Mattermost 웹훅 토큰 |
| `PORT` | - | `5000` | 서버 포트 |
| `POLL_TIMEOUT` | - | `120` | 최대 응답 대기 시간(초) |
| `POLL_INTERVAL` | - | `5` | 상태 폴링 간격(초) |
| `ASSISTANT_ROUTES` | - | `{}` | 멀티 어시스턴트 라우팅 JSON |

### 멀티 어시스턴트 라우팅 설정 예시

```env
ASSISTANT_ROUTES={"장애":"asst_abc123","성능":"asst_def456","배포":"asst_ghi789"}
```

질문에 "장애"가 포함되면 `asst_abc123`, "성능"이 포함되면 `asst_def456`으로 라우팅.  
키워드 없으면 `ASSISTANT_ID`(기본값) 사용.

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/thread` | 새 OpenAI 스레드 생성, `thread_id` 반환 |
| `POST` | `/intermax` | Mattermost 슬래시 커맨드 수신 및 처리 |
| `GET` | `/apidocs` | Swagger UI (자동 생성) |

### `/intermax` 입력 파라미터

| 파라미터 | 설명 |
|----------|------|
| `token` | Mattermost 웹훅 인증 토큰 |
| `user_id` | 사용자 ID (대화 맥락 유지에 사용) |
| `text` | 사용자가 입력한 질문 |
| `response_url` | 최종 응답을 전송할 Mattermost URL |

### 특수 명령어

| 입력 | 동작 |
|------|------|
| `reset` / `/reset` / `초기화` | 현재 사용자의 대화 기록 초기화 |

---

## Mattermost 설정

### Slash Command 설정

| 항목 | 값 |
|------|-----|
| Command | `/intermax` |
| Request URL | `http://your-server:5000/intermax` |
| Request Method | `POST` |
| Response Username | `BotServer` |

### Outgoing Webhook 설정 (트리거 워드 방식)

| 항목 | 값 |
|------|-----|
| Callback URL | `http://your-server:5000/intermax` |
| Trigger Word | `$qwer` |
| Token | `.env`의 `MATTERMOST_TOKEN` 값과 동일하게 설정 |

---

## 로그 확인

실행 중 `botserver.log` 파일에 모든 이벤트가 기록된다.

```
2025-01-01 12:00:00 [INFO] BotServer 시작 (port=5000)
2025-01-01 12:00:05 [INFO] 요청 수신: user=user123 input='장애 원인이...'
2025-01-01 12:00:05 [INFO] 새 스레드 생성: user=user123 thread=thread_abc
2025-01-01 12:00:05 [INFO] 라우팅: '장애' → asst_abc123
2025-01-01 12:00:05 [INFO] run 시작: thread=thread_abc run=run_xyz asst=asst_abc123
2025-01-01 12:00:10 [INFO] run 상태: in_progress (5s 경과)
2025-01-01 12:00:15 [INFO] run 상태: completed (10s 경과)
2025-01-01 12:00:15 [INFO] 응답 전송: user=user123 len=342
```

---

## 데이터베이스 유틸

### insert.py — PostgreSQL 성능 테스트 데이터 생성

```bash
python insert.py
# 1,000만 건을 10만 건씩 나눠 PostgreSQL에 삽입
```

연결 정보는 파일 상단 `DB_PARAMS`에서 수정.

### with.sql — ClickHouse 분석 쿼리

애플리케이션 트랜잭션, Pod 정보, 성능 메트릭 분석용 쿼리 모음.

---

## 개발 이력

| 파일 | 설명 |
|------|------|
| `bot.py` | 트리거 워드 기반 단순 응답 (1세대) |
| `chatbot.py` | OpenAI Assistant 기본 연동 (2세대) |
| `chatres.py` | 비동기 처리 + response_url 추가 (3세대) |
| `chatres1.py` | 인용 텍스트 제거 추가 (4세대) |
| `chat1234.py` | 처리 중 카운트다운 메시지 실험 |
| `app.py` | 모든 기능 통합 + 보안/안정성 개선 **(현재 버전)** |

---

## 주의사항

- `.env` 파일은 절대 Git에 커밋하지 않는다 (`.gitignore`에 포함됨).
- `_user_threads` 딕셔너리는 프로세스 재시작 시 초기화된다. 대화 맥락을 영구 보존하려면 Redis 또는 DB로 교체 필요.
- 운영 환경에서는 `app.run()` 대신 `gunicorn`을 사용 권장: `gunicorn -w 4 app:app`
