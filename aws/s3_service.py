import boto3
from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET
)


s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
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


def rename_s3_object(old_key, new_key):
    s3.copy_object(
        Bucket=S3_BUCKET,
        CopySource={"Bucket": S3_BUCKET, "Key": old_key},
        Key=new_key
    )
    s3.delete_object(Bucket=S3_BUCKET, Key=old_key)


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

