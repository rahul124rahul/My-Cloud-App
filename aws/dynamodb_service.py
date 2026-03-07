import boto3
import uuid
from config import AWS_REGION, DYNAMODB_USERS_TABLE
from config import DYNAMODB_FILES_TABLE
from boto3.dynamodb.conditions import Attr  # <-- add

dynamodb = boto3.resource(
    "dynamodb",
    region_name="us-east-1",
    aws_access_key_id="AWS_ACCESS_KEY",
    aws_secret_access_key="AWS_SECRET_KEY"
)


files_table = dynamodb.Table("files_metadata")
users_table = dynamodb.Table("users")


def save_file_metadata(user_id, file_name, s3_key, folder):

    file = {
        "file_id": str(uuid.uuid4()),
        "user_id": user_id,
        "file_name": file_name,
        "folder": folder,
        "s3_key": s3_key
    }

    files_table.put_item(Item=file)


def create_user(email, password_hash):
    user = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "password_hash": password_hash
    }
    users_table.put_item(Item=user)
    return user


def get_user_by_email(email):
    response = users_table.scan(
        FilterExpression="email = :email",
        ExpressionAttributeValues={
            ":email": email
        }
    )
    items = response.get("Items")
    return items[0] if items else None



def get_user_files(user_id):

    response = files_table.scan(
        FilterExpression="user_id = :uid",
        ExpressionAttributeValues={
            ":uid": user_id
        }
    )

    return response.get("Items", [])




def delete_file_metadata_by_s3_key(s3_key: str):
    """
    Finds all records with the given s3_key and deletes them.
    (Uses scan since current schema doesn't expose file_id in the route.)
    """
    # 1) Find items by s3_key
    response = files_table.scan(
        FilterExpression=Attr("s3_key").eq(s3_key)
    )
    items = response.get("Items", [])

    # 2) Delete each item by its primary key(s)
    for item in items:
        # Assumes partition key is 'file_id' (as written during save_file_metadata)
        files_table.delete_item(
            Key={"file_id": item["file_id"]}
        )