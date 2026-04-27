import logging
import os

import requests

from .base import BaseConnector, Document

log = logging.getLogger(__name__)
MAX_RESULTS = 5


class ExemDocsConnector(BaseConnector):
    """exemDocs 내부 문서 시스템 커넥터.
    EXEM_DOCS_URL이 설정되어 있으면 활성화됨.
    응답 형식: {"results": [{"title": "...", "content": "..."}]}
    """

    def __init__(self):
        self.base_url = os.environ.get("EXEM_DOCS_URL", "").rstrip("/")
        self.api_key = os.environ.get("EXEM_DOCS_API_KEY", "")

    def is_enabled(self) -> bool:
        return bool(self.base_url)

    def search(self, query: str) -> list[Document]:
        if not self.is_enabled():
            return []
        try:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            resp = requests.get(
                f"{self.base_url}/api/search",
                headers=headers,
                params={"q": query, "limit": MAX_RESULTS},
                timeout=10,
            )
            resp.raise_for_status()
            items = resp.json().get("results", [])

            docs = []
            for item in items:
                title = item.get("title", "document")
                content = item.get("content") or item.get("text") or ""
                docs.append(Document(
                    name=f"{title}.txt",
                    content=content.encode("utf-8"),
                    source=f"exem_docs:{item.get('id', title)}",
                ))

            log.info("exemDocs: %d개 문서", len(docs))
            return docs

        except Exception as e:
            log.warning("exemDocs 검색 실패: %s", e)
            return []
