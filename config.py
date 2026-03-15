import os

# Load AWS credentials from environment variables or a .env file.
# Never hardcode credentials here — add them to your .env file instead.
AWS_ACCESS_KEY_ID     = os.environ.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")






FLASK_SECRET_KEY = "super-secret-key-change-me"

AWS_REGION = "us-east-1"

S3_BUCKET = "flask-cloud-drive-storage"

DYNAMODB_USERS_TABLE = "users"
DYNAMODB_FILES_TABLE = "files_metadata"

