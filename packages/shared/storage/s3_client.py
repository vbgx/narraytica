import boto3

from .client import ObjectStorageClient


class S3ObjectStorageClient(ObjectStorageClient):
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
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
