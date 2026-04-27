from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Document:
    name: str
    content: bytes
    mime_type: str = "text/plain"
    source: str = ""


class BaseConnector(ABC):
    @abstractmethod
    def is_enabled(self) -> bool: ...

    @abstractmethod
    def search(self, query: str) -> list[Document]: ...
