import logging
import os

import requests

from .base import BaseConnector, Document

log = logging.getLogger(__name__)
MAX_RESULTS = 5


class ClickUpConnector(BaseConnector):
    BASE_URL = "https://api.clickup.com/api/v2"

    def __init__(self):
        self.token = os.environ.get("CLICKUP_API_TOKEN", "")
        self.workspace_id = os.environ.get("CLICKUP_WORKSPACE_ID", "")

    def is_enabled(self) -> bool:
        return bool(self.token and self.workspace_id)

    def search(self, query: str) -> list[Document]:
        if not self.is_enabled():
            return []
        try:
            resp = requests.get(
                f"{self.BASE_URL}/team/{self.workspace_id}/task",
                headers={"Authorization": self.token},
                params={"query": query, "page": 0, "subtasks": True},
                timeout=10,
            )
            resp.raise_for_status()
            tasks = resp.json().get("tasks", [])[:MAX_RESULTS]

            docs = []
            for task in tasks:
                lines = [
                    f"# {task['name']}",
                    f"상태: {task['status']['status']}",
                    f"우선순위: {(task.get('priority') or {}).get('priority', '-')}",
                    "",
                    task.get("description") or "(설명 없음)",
                ]
                docs.append(Document(
                    name=f"clickup_{task['id']}.txt",
                    content="\n".join(lines).encode("utf-8"),
                    source=f"clickup:{task['id']}",
                ))

            log.info("ClickUp: %d개 태스크", len(docs))
            return docs

        except Exception as e:
            log.warning("ClickUp 검색 실패: %s", e)
            return []
