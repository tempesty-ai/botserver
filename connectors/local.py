import logging
import os
from pathlib import Path

from .base import BaseConnector, Document

log = logging.getLogger(__name__)

SUPPORTED_EXTS = {".txt", ".md", ".pdf", ".docx", ".csv", ".log"}
MIME_MAP = {
    ".pdf":  "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".csv":  "text/csv",
}
MAX_RESULTS = 5
MAX_FILE_BYTES = 512 * 1024  # 512 KB


class LocalConnector(BaseConnector):
    def __init__(self):
        raw = os.environ.get("LOCAL_SEARCH_PATHS", "")
        self.paths = [p.strip() for p in raw.split(",") if p.strip()]

    def is_enabled(self) -> bool:
        return bool(self.paths)

    def search(self, query: str) -> list[Document]:
        keywords = query.lower().split()
        results: list[Document] = []

        for path_str in self.paths:
            base = Path(path_str)
            if not base.exists():
                log.warning("LOCAL 경로 없음: %s", base)
                continue
            for file in base.rglob("*"):
                if file.suffix not in SUPPORTED_EXTS:
                    continue
                if not any(kw in file.name.lower() for kw in keywords):
                    continue
                try:
                    content = file.read_bytes()[:MAX_FILE_BYTES]
                    results.append(Document(
                        name=file.name,
                        content=content,
                        mime_type=MIME_MAP.get(file.suffix, "text/plain"),
                        source=f"local:{file}",
                    ))
                    if len(results) >= MAX_RESULTS:
                        return results
                except Exception as e:
                    log.warning("파일 읽기 실패 %s: %s", file, e)

        return results
