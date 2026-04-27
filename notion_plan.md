# BotServer 개발 로드맵

---

## 1단계 — MM 연동 구조 ✅ 완료

> Mattermost 슬래시 커맨드로 메시지를 전송하고, Assistant API가 읽을 수 있도록 변환하여 답변을 요청하는 기본 연동 구조

```
MatterMost  ──────────────►  API 서버  ──────────────►  Assistant API
     ▲                           │                            │
     └───────────────────────────┘◄───────────────────────────┘
     답변을 MM이 읽을 수 있도록 변환         Assistant API 통해 답변 받아 전송
```

### 처리 흐름

1. **MatterMost → API 서버** — 슬래시 커맨드로 text 형식 메시지 전송
2. **API 서버 사전 작업**
   - Assistant API KEY, Assistant ID 값으로 thread 생성
   - 생성된 thread에서 답변을 받을 수 있도록 데이터 변환
   - 변환한 데이터를 Assistant API에 전송 및 완료 대기
3. **Assistant API 답변 생성** — Vector Store, Instruction, Function Calling 기반 답변 생성
4. **API 서버 → MatterMost** — 답변을 MM 형식으로 변환 후 전송
5. **MatterMost 답변 표시** — 요청한 채널에 답변 표시

### 구현 파일

| 파일 | 역할 |
|------|------|
| `app.py` | 메인 Flask 서버, `/intermax` 엔드포인트 |
| `.env` | API 키, 토큰 관리 |
| `requirements.txt` | 의존성 |

---

## 2단계 — 내부로직 개선 및 고도화 ✅ 완료

> 기존 Mattermost 연동 흐름은 유지하면서, Assistant API 내부 품질을 높이는 단계

```
MatterMost  ──────────────►  API 서버  ──────────────►  Assistant API
                                │                       ┌──────────────────────┐
                                │     requires_action   │ Function Calling     │
                                │◄──────────────────────│ (search_documents,   │
                                │──────────────────────►│  call_webhook, ...)  │
                                                        └──────────────────────┘
```

### 개선 항목

1. **기존 메터모스트 메세지를 통한 로직은 유지**
2. **Assistant API 내부로직 고도화**
   - **Instruction 고도화** — OpenAI Playground에서 더 정밀한 Instruction 설정
   - **Function Calling 고도화 (TOOLS)** — 키워드별 답변 정확성 강화
   - **Vector Store 데이터 전처리 및 업로드** — 용량 최소화, 읽기 좋은 형식으로 정제

### 구현 파일

| 파일 | 역할 |
|------|------|
| `tools/definitions.py` | OpenAI function tool 스키마 정의 (`search_documents`, `call_webhook`) |
| `tools/executor.py` | `requires_action` 수신 시 tool call 실행 |
| `app.py` (업데이트) | `requires_action` 상태 처리 루프 추가 |

### 활성화 방법

```env
# .env
TOOLS_ENABLED=true
TOOL_WEBHOOKS={"performance":"http://내부서버/api/perf","alert":"http://내부서버/api/alert"}
```

---

## 3단계 — 로컬 및 외부 API와의 연동 ✅ 완료

> API 서버가 외부 데이터 소스와 연동하여, 질문과 관련된 파일을 실시간으로 Vector Store에 주입하는 구조

```
┌─────────────┐
│    LOCAL    │
│   exemDocs  │──┐
│  googleDocs │  ├──►  API 서버  ──────────────►  Assistant API
│   clickUp   │──┘    (파일 업로드 후 첨부)
│    etc.     │
└─────────────┘
```

### 처리 흐름

1. **MatterMost 슬래시 커맨드** → API 서버 요청
2. **API 서버 사전 작업**
   - 활성화된 커넥터(Local / exemDocs / GoogleDocs / ClickUp)에서 키워드로 파일 검색
   - 검색된 파일을 OpenAI에 업로드 (`purpose="assistants"`)
   - 해당 파일을 메시지의 첨부파일로 추가 (`file_search` 툴 지정)
3. **Assistant API 답변 생성**
   - 기존 Vector Store 파일 + 새로 첨부된 파일을 함께 참조하여 답변 생성
4. **응답 전달 및 임시 파일 정리** — 업로드한 파일 자동 삭제
5. **MatterMost 답변 표시**

### 구현 파일

| 파일 | 역할 |
|------|------|
| `connectors/base.py` | `BaseConnector` 추상 클래스, `Document` 데이터 클래스 |
| `connectors/local.py` | 로컬 파일 시스템 검색 |
| `connectors/exem_docs.py` | exemDocs 내부 문서 시스템 (HTTP API) |
| `connectors/google_docs.py` | Google Drive 서비스 계정 연동 |
| `connectors/clickup.py` | ClickUp 태스크/문서 검색 |
| `connectors/__init__.py` | `search_all()` — 모든 커넥터 통합 검색 |
| `app.py` (업데이트) | 커넥터 검색 → 파일 업로드 → 메시지 첨부 → 정리 |

### 커넥터별 활성화 방법

```env
# .env

# Local 파일
LOCAL_SEARCH_PATHS=/home/user/docs,/mnt/shared/manuals

# exemDocs
EXEM_DOCS_URL=http://exem-docs-server/
EXEM_DOCS_API_KEY=your-key

# Google Drive (서비스 계정 JSON 파일 필요)
GOOGLE_CREDENTIALS_FILE=google_credentials.json
GOOGLE_DRIVE_FOLDER_ID=1abc2def3ghi

# ClickUp
CLICKUP_API_TOKEN=pk_...
CLICKUP_WORKSPACE_ID=12345678
```

---

## 전체 구조 요약

```
botserver/
├── app.py                  ← 메인 서버 (1+2+3단계 통합)
├── connectors/             ← 3단계: 외부 데이터 소스 커넥터
│   ├── __init__.py         ←   search_all() 통합 인터페이스
│   ├── base.py             ←   BaseConnector, Document
│   ├── local.py            ←   로컬 파일
│   ├── exem_docs.py        ←   exemDocs
│   ├── google_docs.py      ←   Google Drive
│   └── clickup.py          ←   ClickUp
├── tools/                  ← 2단계: Function Calling
│   ├── __init__.py
│   ├── definitions.py      ←   tool 스키마 (search_documents, call_webhook)
│   └── executor.py         ←   tool call 실행기
├── .env                    ← API 키 (커밋 금지)
├── .env.example            ← 설정 템플릿
├── requirements.txt
└── archive/                ← 이전 실험 버전들
```

## 단계별 상태

| 단계 | 핵심 작업 | 상태 |
|------|-----------|------|
| 1단계 | Mattermost ↔ API 서버 ↔ Assistant 기본 연동 | ✅ 완료 |
| 2단계 | Function Calling + Instruction / Vector Store 고도화 | ✅ 완료 |
| 3단계 | Local / exemDocs / GoogleDocs / ClickUp 커넥터 연동 | ✅ 완료 |
