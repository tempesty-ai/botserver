import io
import logging
import os

from .base import BaseConnector, Document

log = logging.getLogger(__name__)
MAX_RESULTS = 5


class GoogleDocsConnector(BaseConnector):
    def __init__(self):
        self.credentials_file = os.environ.get("GOOGLE_CREDENTIALS_FILE", "")
        self.folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
        self._service = None

    def is_enabled(self) -> bool:
        return bool(self.credentials_file and self.folder_id)

    def _get_service(self):
        if self._service:
            return self._service
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError:
            raise RuntimeError("google-auth, google-api-python-client 패키지가 필요합니다: pip install google-auth google-api-python-client")

        creds = service_account.Credentials.from_service_account_file(
            self.credentials_file,
            scopes=["https://www.googleapis.com/auth/drive.readonly"],
        )
        self._service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return self._service

    def search(self, query: str) -> list[Document]:
        if not self.is_enabled():
            return []
        try:
            service = self._get_service()
            resp = service.files().list(
                q=f"name contains '{query}' and '{self.folder_id}' in parents and trashed=false",
                fields="files(id, name, mimeType)",
                pageSize=MAX_RESULTS,
            ).execute()

            docs = []
            for f in resp.get("files", []):
                content = self._download(service, f["id"], f["mimeType"])
                if content:
                    docs.append(Document(
                        name=f["name"],
                        content=content,
                        source=f"google_drive:{f['id']}",
                    ))
            log.info("GoogleDocs: %d개 문서", len(docs))
            return docs

        except Exception as e:
            log.warning("GoogleDocs 검색 실패: %s", e)
            return []

    def _download(self, service, file_id: str, mime_type: str) -> bytes | None:
        try:
            from googleapiclient.http import MediaIoBaseDownload
            if "google-apps" in mime_type:
                request = service.files().export_media(fileId=file_id, mimeType="text/plain")
            else:
                request = service.files().get_media(fileId=file_id)
            buf = io.BytesIO()
            dl = MediaIoBaseDownload(buf, request)
            done = False
            while not done:
                _, done = dl.next_chunk()
            return buf.getvalue()
        except Exception as e:
            log.warning("Google 파일 다운로드 실패 %s: %s", file_id, e)
            return None
