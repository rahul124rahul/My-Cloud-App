import boto3
import uuid
from datetime import datetime
from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    DYNAMODB_USERS_TABLE, DYNAMODB_FILES_TABLE
)
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


files_table = dynamodb.Table(DYNAMODB_FILES_TABLE)
users_table = dynamodb.Table(DYNAMODB_USERS_TABLE)


def save_file_metadata(user_id, file_name, s3_key, folder, file_size, file_type):
    item = {
        "file_id": str(uuid.uuid4()),
        "user_id": user_id,
        "file_name": file_name,
        "folder": folder,
        "s3_key": s3_key,
        "file_size": file_size,
        "file_type": file_type,
        "uploaded_at": datetime.utcnow().isoformat(),
        "item_type": "file"
    }
    files_table.put_item(Item=item)


def create_folder(user_id, folder_name, parent_folder):
    path = f"{parent_folder}/{folder_name}" if parent_folder else folder_name
    item = {
        "file_id": str(uuid.uuid4()),
        "user_id": user_id,
        "file_name": folder_name,
        "folder": parent_folder,
        "s3_key": "",
        "file_size": 0,
        "file_type": "folder",
        "uploaded_at": datetime.utcnow().isoformat(),
        "item_type": "folder",
        "folder_path": path
    }
    files_table.put_item(Item=item)


def create_user(email, password_hash):
    user = {
        "user_id": str(uuid.uuid4()),
        "email": email,
        "password_hash": password_hash
    }
    users_table.put_item(Item=user)
    return user


def get_user_by_email(email):
    items = []
    scan_kwargs = {
        "FilterExpression": Attr("email").eq(email),
        "ConsistentRead": True
    }

    while True:
        response = users_table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))

        if "LastEvaluatedKey" in response:
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        else:
            break

    return items[0] if items else None


def get_user_files(user_id, folder=""):
    items = []
    scan_kwargs = {
        "FilterExpression": Attr("user_id").eq(user_id) & Attr("folder").eq(folder),
        "ConsistentRead": True
    }

    while True:
        response = files_table.scan(**scan_kwargs)
        items.extend(response.get("Items", []))

        if "LastEvaluatedKey" in response:
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        else:
            break

    # Sort: folders first, then files by upload time (newest first)
    folders = [i for i in items if i.get("item_type") == "folder"]
    files = [i for i in items if i.get("item_type") != "folder"]
    folders.sort(key=lambda x: x.get("file_name", "").lower())
    files.sort(key=lambda x: x.get("uploaded_at", ""), reverse=True)

    return folders + files


def delete_file_metadata_by_s3_key(s3_key: str):
    """
    Finds all records with the given s3_key and deletes them.
    """
    scan_kwargs = {
        "FilterExpression": Attr("s3_key").eq(s3_key)
    }

    while True:
        response = files_table.scan(**scan_kwargs)
        items = response.get("Items", [])

        for item in items:
            files_table.delete_item(
                Key={"file_id": item["file_id"]}
            )

        if "LastEvaluatedKey" in response:
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        else:
            break


def rename_item(file_id, new_name, new_s3_key=None):
    """
    Renames a file or folder by updating its file_name (and s3_key for files).
    """
    update_expr = "SET file_name = :n"
    expr_values = {":n": new_name}

    if new_s3_key:
        update_expr += ", s3_key = :sk"
        expr_values[":sk"] = new_s3_key

    files_table.update_item(
        Key={"file_id": file_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )


def get_item_by_id(file_id):
    response = files_table.get_item(Key={"file_id": file_id})
    return response.get("Item")


def delete_folder_and_contents(user_id, folder_path):
    """
    Deletes a folder record and all items inside it (recursively).
    """
    scan_kwargs = {
        "FilterExpression": (
            Attr("user_id").eq(user_id) &
            (Attr("folder").begins_with(folder_path) | Attr("folder").eq(folder_path))
        ),
        "ConsistentRead": True
    }

    while True:
        response = files_table.scan(**scan_kwargs)
        items = response.get("Items", [])

        for item in items:
            # Delete file from S3 if it's a file
            if item.get("item_type") != "folder" and item.get("s3_key"):
                from aws.s3_service import delete_file
                delete_file(item["s3_key"])
            files_table.delete_item(Key={"file_id": item["file_id"]})

        if "LastEvaluatedKey" in response:
            scan_kwargs["ExclusiveStartKey"] = response["LastEvaluatedKey"]
        else:
            break

    # Also delete the folder record itself (where item_type=folder and folder_path=folder_path)
    folder_scan = {
        "FilterExpression": (
            Attr("user_id").eq(user_id) &
            Attr("item_type").eq("folder") &
            Attr("folder_path").eq(folder_path)
        ),
        "ConsistentRead": True
    }
    response = files_table.scan(**folder_scan)
    for item in response.get("Items", []):
        files_table.delete_item(Key={"file_id": item["file_id"]})