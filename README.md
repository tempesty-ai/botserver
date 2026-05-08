# BotServer - Mattermost와 LLM Assistant 챗봇

> Mattermost slash command를 LLM Assistant와 연결하는 샘플 연동 서버입니다.
> 단순한 챗봇 응답 흐름뿐 아니라, 잘못된 답변을 QA 관점에서 어떻게 다룰 것인지까지 함께 다룹니다.

## 데이터 안내

이 저장소의 slash command 이름, 라우팅 키워드, 데이터베이스 연결 예시, SQL 예시, 로그는 모두 샘플 값입니다. 현재 또는 과거 회사/고객사의 환경에서 복사한 값이 아닙니다.

가상화된 예시는 다음과 같습니다.

- `/sample-bot` 같은 slash command 이름
- `topic_a`, `topic_b` 같은 라우팅 키워드
- 데이터베이스 호스트, 테이블, 쿼리 예시
- Assistant 라우팅 예시

## 문제

QA와 운영 채널에서는 같은 질문이 반복되는 경우가 많습니다.

- 이 환경의 빌드 번호가 무엇인가?
- 지난주 장애 원인은 무엇이었는가?
- 성능 테스트 절차 문서는 어디에 있는가?

이 프로젝트는 반복되는 수동 답변을 줄이면서도, 응답 흐름을 명시적이고 테스트 가능하게 유지하는 것을 목표로 합니다.

## 접근 방식

| 결정 | 이유 |
| --- | --- |
| Mattermost slash command와 outgoing webhook | 익숙한 협업 인터페이스를 사용하기 위해 |
| OpenAI Assistant API | thread 기반 대화 맥락을 유지하기 위해 |
| 키워드 기반 Assistant 라우팅 | 주제별 Assistant를 분리하기 위해 |
| 백그라운드 처리 | LLM 응답 대기 중 채팅 UX가 멈추지 않도록 하기 위해 |
| `.env` 설정 | API 키와 토큰을 소스 코드에서 분리하기 위해 |

## 주요 기능

| 기능 | 설명 |
| --- | --- |
| 비동기 응답 흐름 | 먼저 처리 중 메시지를 반환하고, 최종 답변은 나중에 게시 |
| 사용자 thread 재사용 | Mattermost 사용자 ID 기준으로 OpenAI thread 재사용 |
| 대화 초기화 | `reset` 명령으로 사용자 로컬 thread 매핑 초기화 |
| 다중 Assistant 라우팅 | 키워드에 따라 Assistant ID로 메시지 라우팅 |
| Timeout 처리 | 설정된 시간 초과 시 통제된 오류 메시지 반환 |
| Citation 정리 | Assistant citation marker를 최종 텍스트에서 제거 |
| 토큰 검증 | Mattermost webhook token을 선택적으로 검증 |
| 구조화 로그 | 콘솔과 `botserver.log`에 로그 기록 |

## 메시지 흐름

```text
Mattermost user
  -> POST /sample-bot
  -> immediate ephemeral response
  -> background thread processing
  -> OpenAI Assistant run polling
  -> citation cleanup
  -> response_url final POST
```

## 아키텍처 단계

아래 다이어그램은 초기 Mattermost slash command 흐름부터 외부 connector 기반 Assistant 흐름까지의 확장 과정을 요약합니다.

### 1단계 - Mattermost 연동

![Mattermost, API 서버, Assistant API 메시지 흐름](img/phase1_mm_flow.png)

### 2단계 - Assistant 내부 로직

![Assistant API instruction, function calling, vector store 개선 흐름](img/phase2_internal_logic.png)

### 3단계 - Connector 확장

![로컬 및 외부 connector가 Assistant 응답 파이프라인으로 연결되는 흐름](img/phase3_connector_flow.png)

## 빠른 시작

```bash
pip install -r requirements.txt
cp .env.example .env
python app.py
```

기본적으로 서버는 `0.0.0.0:5000`에서 시작합니다.

## 환경 변수

| 변수 | 필수 | 기본값 | 설명 |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | 예 | - | OpenAI API 키 |
| `ASSISTANT_ID` | 예 | - | 기본 Assistant ID |
| `MATTERMOST_TOKEN` | 아니오 | Empty | Mattermost webhook token |
| `PORT` | 아니오 | `5000` | 서버 포트 |
| `POLL_TIMEOUT` | 아니오 | `120` | 최대 대기 시간(초) |
| `POLL_INTERVAL` | 아니오 | `5` | polling 간격(초) |
| `ASSISTANT_ROUTES` | 아니오 | `{}` | JSON 형태의 키워드별 Assistant ID 매핑 |

라우팅 설정 예시:

```text
ASSISTANT_ROUTES={"topic_a":"asst_aaa","topic_b":"asst_bbb"}
```

## API 엔드포인트

| Method | Path | 설명 |
| --- | --- | --- |
| `GET` | `/health` | Health check |
| `GET` | `/thread` | 새 OpenAI thread 생성 |
| `POST` | `/sample-bot` | Mattermost slash command 요청 수신 |
| `GET` | `/apidocs` | Swagger UI |

## 데이터베이스 유틸리티 참고

`insert.py`는 학습용 PostgreSQL 성능 테스트 데이터 생성기입니다. 남아 있는 연결 값은 사용 전에 로컬 dummy 값으로 교체해야 합니다.

## QA 의미와 한계

이 저장소는 운영용 지원 챗봇이 아니라 연동 패턴을 보여주는 프로젝트입니다. 답변 정확도를 자체적으로 평가하지는 않습니다. 다음 QA 질문인 "챗봇의 잘못된 답변을 어떻게 감지하고 측정할 것인가?"는 형제 프로젝트 `aiops-sentinel`에서 LLM 출력 평가로 다룹니다.

## 로드맵

- Redis 또는 데이터베이스에 대화 맥락 저장
- `aiops-sentinel`과 연결해 응답 품질 평가 추가
- 응답 시간과 실패율 모니터링 추가
