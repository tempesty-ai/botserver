import json
import logging
import os
import re
from threading import Thread
from time import sleep

import openai
import requests
from dotenv import load_dotenv
from flasgger import Swagger
from flask import Flask, jsonify, request

load_dotenv()

# ── 설정 ──────────────────────────────────────────────────────────────────────

OPENAI_API_KEY  = os.environ["OPENAI_API_KEY"]
DEFAULT_ASST_ID = os.environ["ASSISTANT_ID"]
MM_TOKEN        = os.environ.get("MATTERMOST_TOKEN", "")
PORT            = int(os.environ.get("PORT", 5000))
POLL_TIMEOUT    = int(os.environ.get("POLL_TIMEOUT", 120))
POLL_INTERVAL   = int(os.environ.get("POLL_INTERVAL", 5))
TOOLS_ENABLED   = os.environ.get("TOOLS_ENABLED", "false").lower() == "true"

_routes_raw = os.environ.get("ASSISTANT_ROUTES", "")
ASSISTANT_ROUTES: dict[str, str] = json.loads(_routes_raw) if _routes_raw else {}

openai.api_key = OPENAI_API_KEY

# ── 로깅 ──────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("botserver.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── 스레드 영속성 (사용자 ID → OpenAI thread_id) ─────────────────────────────

_user_threads: dict[str, str] = {}


def get_or_create_thread(user_id: str) -> str:
    if user_id not in _user_threads:
        thread = openai.beta.threads.create()
        _user_threads[user_id] = thread.id
        log.info("새 스레드 생성: user=%s thread=%s", user_id, thread.id)
    return _user_threads[user_id]


def reset_thread(user_id: str) -> str:
    thread = openai.beta.threads.create()
    _user_threads[user_id] = thread.id
    log.info("스레드 초기화: user=%s thread=%s", user_id, thread.id)
    return thread.id


# ── 어시스턴트 라우팅 ─────────────────────────────────────────────────────────

def resolve_assistant(text: str) -> str:
    lower = text.lower()
    for keyword, asst_id in ASSISTANT_ROUTES.items():
        if keyword.lower() in lower:
            log.info("어시스턴트 라우팅: '%s' → %s", keyword, asst_id)
            return asst_id
    return DEFAULT_ASST_ID


# ── 응답 텍스트 정제 ──────────────────────────────────────────────────────────

def clean_response(text: str) -> str:
    text = re.sub(r"【.*?】", "", text)
    text = text.split("†")[0].strip()
    return text


# ── 3단계: 외부 문서 검색 및 OpenAI 파일 업로드 ──────────────────────────────

def fetch_and_upload_files(query: str) -> list[str]:
    """커넥터로 문서를 검색하고 OpenAI에 업로드. 파일 ID 목록을 반환한다."""
    from connectors import search_all
    docs = search_all(query)
    if not docs:
        return []

    file_ids = []
    for doc in docs:
        try:
            response = openai.files.create(
                file=(doc.name, doc.content, doc.mime_type),
                purpose="assistants",
            )
            file_ids.append(response.id)
            log.info("파일 업로드: %s → %s (출처: %s)", doc.name, response.id, doc.source)
        except Exception as e:
            log.warning("파일 업로드 실패 %s: %s", doc.name, e)

    return file_ids


def cleanup_files(file_ids: list[str]):
    """업로드한 임시 파일들을 삭제한다."""
    for fid in file_ids:
        try:
            openai.files.delete(fid)
            log.info("파일 삭제: %s", fid)
        except Exception as e:
            log.warning("파일 삭제 실패 %s: %s", fid, e)


# ── 2단계: Assistant run + Function Calling 처리 ──────────────────────────────

def run_assistant_and_wait(thread_id: str, assistant_id: str) -> str:
    """Assistant를 실행하고 완료까지 기다린다. Function Calling도 처리한다."""
    from tools import TOOL_DEFINITIONS, execute as execute_tools

    run_kwargs: dict = {"thread_id": thread_id, "assistant_id": assistant_id}
    if TOOLS_ENABLED:
        run_kwargs["tools"] = [{"type": "file_search"}, *TOOL_DEFINITIONS]
        log.info("Function Calling 활성화: %d개 툴", len(TOOL_DEFINITIONS))

    run = openai.beta.threads.runs.create(**run_kwargs)
    run_id = run.id
    log.info("run 시작: thread=%s run=%s asst=%s", thread_id, run_id, assistant_id)

    elapsed = 0
    terminal_statuses = {"completed", "failed", "cancelled", "expired"}

    while elapsed < POLL_TIMEOUT:
        sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

        run_obj = openai.beta.threads.runs.retrieve(run_id=run_id, thread_id=thread_id)
        status = run_obj.status
        log.info("run 상태: %s (%ds 경과)", status, elapsed)

        if status == "completed":
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            latest = messages.data[0].content[0].text.value
            return clean_response(latest)

        # 2단계: Function Calling 처리
        if status == "requires_action":
            tool_calls = run_obj.required_action.submit_tool_outputs.tool_calls
            log.info("Function Calling 요청: %d개", len(tool_calls))
            outputs = execute_tools(tool_calls)
            openai.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run_id,
                tool_outputs=outputs,
            )
            continue

        if status in terminal_statuses:
            raise RuntimeError(f"run이 '{status}' 상태로 종료되었습니다.")

    raise TimeoutError(f"{POLL_TIMEOUT}초 내에 응답을 받지 못했습니다.")


# ── 메인 처리 흐름 ────────────────────────────────────────────────────────────

def process_chat(user_id: str, user_input: str, response_url: str, reset: bool = False):
    """백그라운드 스레드에서 실행되는 메인 처리 로직."""
    uploaded_file_ids: list[str] = []
    try:
        thread_id = reset_thread(user_id) if reset else get_or_create_thread(user_id)

        # 3단계: 외부 문서 검색 및 파일 첨부
        from connectors import active_connectors
        active = active_connectors()
        attachments = []

        if active:
            log.info("활성 커넥터: %s — '%s' 검색 중", active, user_input[:30])
            uploaded_file_ids = fetch_and_upload_files(user_input)
            attachments = [
                {"file_id": fid, "tools": [{"type": "file_search"}]}
                for fid in uploaded_file_ids
            ]
            if attachments:
                log.info("메시지에 %d개 파일 첨부", len(attachments))

        # 메시지 추가
        msg_kwargs: dict = {"thread_id": thread_id, "role": "user", "content": user_input}
        if attachments:
            msg_kwargs["attachments"] = attachments
        openai.beta.threads.messages.create(**msg_kwargs)

        # 어시스턴트 실행
        assistant_id = resolve_assistant(user_input)
        answer = run_assistant_and_wait(thread_id, assistant_id)

        payload = {"response_type": "in_channel", "text": answer}
        log.info("응답 전송: user=%s len=%d", user_id, len(answer))

    except Exception as e:
        log.exception("처리 오류: user=%s", user_id)
        payload = {
            "response_type": "ephemeral",
            "text": f"오류가 발생했습니다: {e}",
        }
    finally:
        # 업로드한 임시 파일 정리
        if uploaded_file_ids:
            cleanup_files(uploaded_file_ids)

    requests.post(response_url, json=payload, headers={"Content-Type": "application/json"})


# ── Flask 앱 ──────────────────────────────────────────────────────────────────

app = Flask(__name__)
Swagger(app)


def _verify_token() -> bool:
    if not MM_TOKEN:
        return True
    return request.form.get("token") == MM_TOKEN


@app.route("/health", methods=["GET"])
def health():
    """서버 상태 및 활성 커넥터 확인."""
    from connectors import active_connectors
    return jsonify({
        "status": "ok",
        "tools_enabled": TOOLS_ENABLED,
        "active_connectors": active_connectors(),
    })


@app.route("/thread", methods=["GET"])
def create_thread():
    """
    새로운 OpenAI 스레드를 생성하고 ID를 반환합니다.
    ---
    tags: [Thread]
    responses:
      200:
        description: 스레드 ID
        schema:
          type: object
          properties:
            thread_id: {type: string}
    """
    try:
        thread = openai.beta.threads.create()
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        log.exception("스레드 생성 실패")
        return jsonify({"error": str(e)}), 500


@app.route("/intermax", methods=["POST"])
def intermax():
    """
    Mattermost 슬래시 커맨드를 처리합니다.
    ---
    tags: [Chat]
    parameters:
      - {name: token,        in: formData, type: string, description: Mattermost 웹훅 토큰}
      - {name: user_id,      in: formData, type: string, required: true, description: 사용자 ID}
      - {name: text,         in: formData, type: string, required: true, description: 사용자 입력}
      - {name: response_url, in: formData, type: string, required: true, description: 응답 URL}
    responses:
      200:
        description: 즉시 응답 (처리는 백그라운드에서 진행)
    """
    if not _verify_token():
        return jsonify({"response_type": "ephemeral", "text": "인증 실패"}), 403

    user_input   = (request.form.get("text") or "").strip()
    user_id      = request.form.get("user_id", "unknown")
    response_url = request.form.get("response_url", "")

    if not user_input:
        return jsonify({
            "response_type": "ephemeral",
            "text": "질문을 입력해주세요.\n예) `/intermax 장애 원인이 뭔가요?`",
        })

    # 대화 초기화 명령어
    if user_input.lower() in ("reset", "/reset", "초기화"):
        reset_thread(user_id)
        return jsonify({"response_type": "ephemeral", "text": "대화 기록이 초기화되었습니다."})

    log.info("요청 수신: user=%s input='%s'", user_id, user_input[:50])
    Thread(
        target=process_chat,
        args=(user_id, user_input, response_url),
        daemon=True,
    ).start()

    from connectors import active_connectors
    connector_note = ""
    if active_connectors():
        connector_note = f"\n> 외부 문서 검색 중: {', '.join(active_connectors())}"

    return jsonify({
        "response_type": "ephemeral",
        "text": (
            f"**'{user_input[:40]}'** 에 대한 답변을 생성 중입니다.\n"
            f"잠시만 기다려주세요. (최대 {POLL_TIMEOUT}초)"
            f"{connector_note}\n\n"
            "> 답변은 참고용이며 틀릴 수 있습니다."
        ),
    })


if __name__ == "__main__":
    from connectors import active_connectors
    log.info("BotServer 시작 (port=%d)", PORT)
    log.info("Function Calling: %s", "활성화" if TOOLS_ENABLED else "비활성화")
    log.info("활성 커넥터: %s", active_connectors() or "없음")
    app.run(host="0.0.0.0", port=PORT)
