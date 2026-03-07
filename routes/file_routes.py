from flask import Blueprint, request, redirect, session
from aws.s3_service import upload_file
from aws.dynamodb_service import save_file_metadata, delete_file_metadata_by_s3_key
from aws.s3_service import delete_file
from aws.s3_service import generate_download_url
from flask import redirect

file_bp = Blueprint("files", __name__)


@file_bp.route("/upload", methods=["POST"])
def upload():

    if "user_id" not in session:
        return redirect("/login")

    file = request.files["file"]
    folder = request.form.get("folder", "")

    user_id = session["user_id"]

    if folder:
        s3_key = f"{user_id}/{folder}/{file.filename}"
    else:
        s3_key = f"{user_id}/{file.filename}"

    upload_file(file, s3_key)

    save_file_metadata(user_id, file.filename, s3_key, folder)

    return redirect("/dashboard")


@file_bp.route("/download/<path:s3_key>")
def download(s3_key):

    url = generate_download_url(s3_key)

    return redirect(url)



@file_bp.route("/delete/<path:s3_key>")
def delete(s3_key):
    if "user_id" not in session:
        return redirect("/login")

    # 1) Delete from S3
    delete_file(s3_key)

    # 2) Delete metadata from DynamoDB
    delete_file_metadata_by_s3_key(s3_key)

    return redirect("/dashboard")