import boto3

from app.config import (
    AWS_ACCESS_KEY_ID,
    AWS_REGION,
    AWS_SECRET_ACCESS_KEY,
    S3_INPUT_BUCKET_NAME,
)


class S3Service:

    def __init__(self):
        self.client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

        self.bucket_name = S3_INPUT_BUCKET_NAME

    # ==========================================================
    # Upload
    # ==========================================================

    def upload_file(
        self,
        file_content: bytes,
        object_key: str,
        content_type: str | None = None,
    ) -> str:

        extra_args = {}

        if content_type:
            extra_args["ContentType"] = content_type

        self.client.put_object(
            Bucket=self.bucket_name,
            Key=object_key,
            Body=file_content,
            **extra_args,
        )

        return f"s3://{self.bucket_name}/{object_key}"

    # ==========================================================
    # Presigned Download URL
    # ==========================================================

    def generate_download_url(
        self,
        object_key: str,
        expires_in: int = 900,
    ) -> str:

        return self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": object_key,
            },
            ExpiresIn=expires_in,
        )

    # ==========================================================
    # Single Transaction File
    # ==========================================================

    def upload_transaction_file(
        self,
        transaction_id: str,
        file_content: bytes,
        filename: str = "transaction.csv",
        content_type: str = "text/csv",
    ) -> tuple[str, str]:

        object_key = (
            f"transactions/"
            f"{transaction_id}/"
            f"uploads/"
            f"{filename}"
        )

        s3_location = self.upload_file(
            file_content=file_content,
            object_key=object_key,
            content_type=content_type,
        )

        download_url = self.generate_download_url(
            object_key=object_key
        )

        return s3_location, download_url

    # ==========================================================
    # Batch Transaction File
    # ==========================================================

    def upload_batch_file(
        self,
        batch_id: str,
        file_content: bytes,
        filename: str = "transactions.csv",
        content_type: str = "text/csv",
    ) -> tuple[str, str]:

        object_key = (
            f"batches/"
            f"{batch_id}/"
            f"uploads/"
            f"{filename}"
        )

        s3_location = self.upload_file(
            file_content=file_content,
            object_key=object_key,
            content_type=content_type,
        )

        download_url = self.generate_download_url(
            object_key=object_key
        )

        return s3_location, download_url


s3_service = S3Service()