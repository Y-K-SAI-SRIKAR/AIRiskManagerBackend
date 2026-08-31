from app.services.s3_service import s3_service


def test_s3_upload():
    content = b"AI Risk Manager S3 test"

    location = s3_service.upload_file(
        file_content=content,
        object_key="test/s3-test.txt",
        content_type="text/plain",
    )

    assert location.startswith("s3://")

    print(f"\nUploaded: {location}")