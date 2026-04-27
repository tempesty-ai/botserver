import json
import logging
import os

import requests

log = logging.getLogger(__name__)


def execute(tool_calls) -> list[dict]:
    """OpenAI requires_action의 tool_calls를 실행하고 outputs를 반환한다."""
    outputs = []
    for tc in tool_calls:
        name = tc.function.name
        try:
            args = json.loads(tc.function.arguments)
            result = _dispatch(name, args)
        except Exception as e:
            log.exception("툴 실행 오류: %s", name)
            result = {"error": str(e)}

        outputs.append({
            "tool_call_id": tc.id,
            "output": json.dumps(result, ensure_ascii=False),
        })
        log.info("툴 실행: %s → %s", name, str(result)[:100])
    return outputs


def _dispatch(name: str, args: dict) -> dict:
    if name == "search_documents":
        return _search_documents(args.get("query", ""))
    if name == "call_webhook":
        return _call_webhook(args.get("endpoint", ""), args.get("params", {}))
    return {"error": f"알 수 없는 툴: {name}"}


def _search_documents(query: str) -> dict:
    from connectors import search_all
    docs = search_all(query)
    if not docs:
        return {"result": "관련 문서를 찾을 수 없습니다.", "count": 0}

    content = "\n\n---\n\n".join(
        f"### [{d.source}] {d.name}\n{d.content.decode('utf-8', errors='ignore')[:2000]}"
        for d in docs
    )
    return {"result": content, "count": len(docs)}


def _call_webhook(endpoint: str, params: dict) -> dict:
    raw = os.environ.get("TOOL_WEBHOOKS", "{}")
    try:
        webhooks: dict = json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "TOOL_WEBHOOKS 환경 변수 형식이 잘못되었습니다."}

    url = webhooks.get(endpoint)
    if not url:
        available = list(webhooks.keys())
        return {"error": f"웹훅 '{endpoint}'이 설정되지 않았습니다. 사용 가능: {available}"}

    try:
        resp = requests.post(url, json=params, timeout=10)
        resp.raise_for_status()
        return {"result": resp.json()}
    except Exception as e:
        return {"error": str(e)}
