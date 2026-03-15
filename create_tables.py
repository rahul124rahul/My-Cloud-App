"""
One-time script to create the DynamoDB tables required by the app.
Run this once:  python create_tables.py
"""
import boto3
from config import (
    AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
    DYNAMODB_USERS_TABLE, DYNAMODB_FILES_TABLE
)

dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# ---------- users table ----------
try:
    users_table = dynamodb.create_table(
        TableName=DYNAMODB_USERS_TABLE,
        KeySchema=[
            {"AttributeName": "user_id", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    users_table.wait_until_exists()
    print("✅  'users' table created successfully.")
except dynamodb.meta.client.exceptions.ResourceInUseException:
    print("ℹ️  'users' table already exists.")

# ---------- files_metadata table ----------
try:
    files_table = dynamodb.create_table(
        TableName=DYNAMODB_FILES_TABLE,
        KeySchema=[
            {"AttributeName": "file_id", "KeyType": "HASH"}
        ],
        AttributeDefinitions=[
            {"AttributeName": "file_id", "AttributeType": "S"}
        ],
        BillingMode="PAY_PER_REQUEST"
    )
    files_table.wait_until_exists()
    print("✅  'files_metadata' table created successfully.")
except dynamodb.meta.client.exceptions.ResourceInUseException:
    print("ℹ️  'files_metadata' table already exists.")

print("\nDone — both tables are ready.")
