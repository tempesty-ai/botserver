import logging

from .base import Document
from .clickup import ClickUpConnector
from .exem_docs import ExemDocsConnector
from .google_docs import GoogleDocsConnector
from .local import LocalConnector

log = logging.getLogger(__name__)

_connectors = [
    LocalConnector(),
    ExemDocsConnector(),
    GoogleDocsConnector(),
    ClickUpConnector(),
]


def search_all(query: str) -> list[Document]:
    """활성화된 모든 커넥터에서 query로 문서를 검색한다."""
    results: list[Document] = []
    for connector in _connectors:
        if not connector.is_enabled():
            continue
        name = type(connector).__name__
        try:
            docs = connector.search(query)
            log.info("%s: %d개 문서 발견", name, len(docs))
            results.extend(docs)
        except Exception as e:
            log.warning("%s 오류: %s", name, e)
    return results


def active_connectors() -> list[str]:
    return [type(c).__name__ for c in _connectors if c.is_enabled()]
