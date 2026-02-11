import os

import boto3

from .client import ObjectStorageClient


class S3ObjectStorageClient(ObjectStorageClient):
    def __init__(
        self,
        endpoint_url: str | None,
        access_key: str | None,
        secret_key: str | None,
        region: str = "us-east-1",
    ):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    def upload_bytes(
        self, bucket: str, key: str, data: bytes, content_type: str
    ) -> None:
        self.s3.put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)

    def download_bytes(self, bucket: str, key: str) -> bytes:
        obj = self.s3.get_object(Bucket=bucket, Key=key)
        return obj["Body"].read()

    def copy_object(
        self, src_bucket: str, src_key: str, dst_bucket: str, dst_key: str
    ) -> None:
        copy_source = {"Bucket": src_bucket, "Key": src_key}
        self.s3.copy_object(Bucket=dst_bucket, Key=dst_key, CopySource=copy_source)

    def download_to_file(self, bucket: str, key: str, dst_path: str) -> None:
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(dst_path, "wb") as f:
            self.s3.download_fileobj(bucket, key, f)

    def stat_object(self, bucket: str, key: str) -> dict:
        """
        Returns basic metadata for an object without downloading it.
        """
        head = self.s3.head_object(Bucket=bucket, Key=key)
        return {
            "bucket": bucket,
            "key": key,
            "size_bytes": head.get("ContentLength"),
            "content_type": head.get("ContentType"),
            "etag": (head.get("ETag") or "").strip('"'),
        }
