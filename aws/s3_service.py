import boto3
from config import AWS_REGION, S3_BUCKET


s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id="AWS_ACCESS_KEY",
    aws_secret_access_key="AWS_SECRET_KEY"
)


def upload_file(file, s3_key):

    s3.upload_fileobj(
        file,
        S3_BUCKET,
        s3_key
    )


def delete_file(s3_key):

    s3.delete_object(
        Bucket=S3_BUCKET,
        Key=s3_key
    )


def generate_download_url(s3_key):

    url = s3.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": s3_key
        },
        ExpiresIn=3600
    )

    return url

