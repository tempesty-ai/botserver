# `botserver` — Mattermost × OpenAI Assistant QA 챗봇

> Mattermost 슬래시 커맨드와 OpenAI Assistant API를 연결하는 챗봇 서버.
> 핵심은 "챗봇을 띄우는 것"이 아니라, **"QA가 같은 질문을 반복해서 받는 인터럽트 비용을 어떻게 줄이느냐"** 입니다.

---

## 한 줄 가치

> **"QA가 같은 장애·성능·배포 질문을 매일 몇 번이나 받고 있는가?"** 라는 문제에 답하는 저장소.
> 비동기·라우팅·타임아웃·로깅·인증·리셋까지 갖춰 **PoC가 아니라 그대로 사내에 배치 가능한** 수준으로 설계했습니다.

---

## 발견한 크리티컬 리스크

| # | 리스크 | 의미 |
| --- | --- | --- |
| R1 | **QA 응답 지연 / 인터럽트 비용** | QA가 같은 장애/성능/배포 관련 질문을 반복적으로 받으면 다른 작업이 끊김. 멘탈 컨텍스트 스위칭 비용 누적 |
| R2 | **컨텍스트 단절** | 챗봇이 매번 새로 시작하면 "아까 말한 그 장애"를 다시 설명해야 함. 후속 질문 정확도 저하 |
| R3 | **잘못된 어시스턴트 라우팅** | 질문 유형(장애/성능/배포)별로 다른 지식 베이스가 필요한데 단일 모델로만 답하면 도메인 정확도 저하 |
| R4 | **외부 API 타임아웃** | OpenAI Run이 오래 걸리면 Mattermost 3초 타임아웃으로 슬래시 커맨드 자체가 끊김 → 사용자 신뢰 상실 |

---

## 테스트 설계 (= 서버 자체의 안정성 설계)

이 챗봇 서버는 **운영 검증 포인트 자체가 곧 설계 포인트**입니다.

| 기능 | 설계 의도 | 어떤 리스크에 답하는가 |
| --- | --- | --- |
| **비동기 처리** (즉시 "생성 중" 반환 → 백그라운드 처리) | Mattermost 3초 타임아웃 회피 | R4 |
| **사용자 ID별 OpenAI Thread 재사용** | 대화 맥락 유지 → 후속 질문 정확도 ↑ | R2 |
| **키워드 기반 멀티 어시스턴트 라우팅** (장애 / 성능 / 배포) | 도메인별 정확도 ↑ | R3 |
| **폴링 타임아웃** (기본 120초) + **실패 상태 감지** (`failed`, `cancelled`, `expired`) | 응답 누락 방지 | R4 |
| **인용 마커 자동 제거** (`【4:1†source】`) | 출력 가독성 | 사용자 경험 |
| **`/intermax reset` 명령** | 컨텍스트가 꼬였을 때 즉시 복구 | R2 (안전장치) |
| **토큰 인증 + 구조화 로깅** | 보안 + 운영 디버깅 가능성 | 운영 신뢰 |
| **`insert.py`** (1,000만 건 PG 적재 유틸) + **`with.sql`** (ClickHouse 분석 쿼리) | 챗봇 답변 품질을 뒷받침할 **데이터 환경**까지 자체 구비 | 답변 품질 |

### 메시지 흐름

```
Mattermost 사용자
      │ (슬래시 커맨드)
      ▼
app.py /intermax
      │
      ├─► 즉시 "생성 중..." 반환 (ephemeral)  ← 3초 타임아웃 회피
      │
      └─► 백그라운드 Thread 시작
               │
               ├── 사용자 ID로 기존 스레드 조회 or 신규 생성  ← 컨텍스트 유지
               │
               ├── 키워드로 어시스턴트 ID 결정  ← 도메인 라우팅
               │
               ├── OpenAI Thread에 메시지 추가 & Run 시작
               │
               ├── 5초 간격 폴링 (최대 120초)  ← 타임아웃 가드
               │
               ├── 완료 → 인용 마커 제거
               │
               └── Mattermost response_url로 최종 응답 POST
```

### 멀티 어시스턴트 라우팅 예시

```
ASSISTANT_ROUTES={"장애":"asst_abc123","성능":"asst_def456","배포":"asst_ghi789"}
```

질문에 "장애" 포함 → `asst_abc123`, "성능" 포함 → `asst_def456`. 키워드 없으면 기본값.

---

## 자동화의 비즈니스 임팩트

| 임팩트 | 어떻게 발생하는가 |
| --- | --- |
| **QA 인터럽트 비용 감소** | 반복 질문을 챗봇이 1차로 받음 → 멘탈 컨텍스트 스위칭 비용 감소 |
| **도메인별 답변 일관성** | 키워드 라우팅으로 장애/성능/배포 답변 품질이 일관됨 |
| **운영 가능한 챗봇** | 비동기·타임아웃·로깅·인증·리셋까지 갖춤 → PoC가 아니라 즉시 사내 배치 가능 |
| **데이터 검증 환경 동봉** | `insert.py`(1,000만 건) + `with.sql`로 챗봇이 답할 데이터까지 자체 구축 가능 |

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

## 빠른 시작

### 1. 설치

```
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```
cp .env.example .env
```

`.env` 파일을 열어 실제 값으로 교체:

```
OPENAI_API_KEY=sk-proj-...
ASSISTANT_ID=asst_...
MATTERMOST_TOKEN=your-token
```

### 3. 실행

```
python app.py
```

서버가 `0.0.0.0:5000`에서 시작된다.

---

## 환경 변수

| 변수 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | ✅ | - | OpenAI API 키 |
| `ASSISTANT_ID` | ✅ | - | 기본 OpenAI Assistant ID |
| `MATTERMOST_TOKEN` | - | (검증 안 함) | Mattermost 웹훅 토큰 |
| `PORT` | - | `5000` | 서버 포트 |
| `POLL_TIMEOUT` | - | `120` | 최대 응답 대기 시간(초) |
| `POLL_INTERVAL` | - | `5` | 상태 폴링 간격(초) |
| `ASSISTANT_ROUTES` | - | `{}` | 멀티 어시스턴트 라우팅 JSON |

---

## API 엔드포인트

| 메서드 | 경로 | 설명 |
| --- | --- | --- |
| `GET` | `/health` | 서버 상태 확인 |
| `GET` | `/thread` | 새 OpenAI 스레드 생성, `thread_id` 반환 |
| `POST` | `/intermax` | Mattermost 슬래시 커맨드 수신 및 처리 |
| `GET` | `/apidocs` | Swagger UI (자동 생성) |

### 특수 명령어

| 입력 | 동작 |
| --- | --- |
| `reset` / `/reset` / `초기화` | 현재 사용자의 대화 기록 초기화 |

---

## Mattermost 설정

### Slash Command

| 항목 | 값 |
| --- | --- |
| Command | `/intermax` |
| Request URL | `http://your-server:5000/intermax` |
| Request Method | `POST` |
| Response Username | `BotServer` |

### Outgoing Webhook (트리거 워드 방식)

| 항목 | 값 |
| --- | --- |
| Callback URL | `http://your-server:5000/intermax` |
| Trigger Word | `$qwer` |
| Token | `.env`의 `MATTERMOST_TOKEN` 값과 동일 |

---

## 데이터베이스 유틸

### `insert.py` — PostgreSQL 성능 테스트 데이터 생성

```
python insert.py
# 1,000만 건을 10만 건씩 나눠 PostgreSQL에 삽입
```

연결 정보는 파일 상단 `DB_PARAMS`에서 수정.

### `with.sql` — ClickHouse 분석 쿼리

애플리케이션 트랜잭션, Pod 정보, 성능 메트릭 분석용 쿼리 모음.

---

## 개발 이력

| 파일 | 설명 |
| --- | --- |
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
- 운영 환경에서는 `app.run()` 대신 `gunicorn` 사용 권장: `gunicorn -w 4 app:app`
