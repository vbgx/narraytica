from abc import ABC, abstractmethod


class ObjectStorageClient(ABC):
    @abstractmethod
    def upload_bytes(
        self, bucket: str, key: str, data: bytes, content_type: str
    ) -> None:
        pass

    @abstractmethod
    def download_bytes(self, bucket: str, key: str) -> bytes:
        pass
