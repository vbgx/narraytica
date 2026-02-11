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
