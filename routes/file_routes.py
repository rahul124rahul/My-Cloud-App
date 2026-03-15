from flask import Blueprint, request, redirect, session
from aws.s3_service import upload_file, delete_file, generate_download_url, rename_s3_object
from aws.dynamodb_service import (
    save_file_metadata, delete_file_metadata_by_s3_key,
    create_folder, delete_folder_and_contents,
    rename_item, get_item_by_id
)

file_bp = Blueprint("files", __name__)


def _format_size(size_bytes):
    """Convert bytes to human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


@file_bp.route("/upload", methods=["POST"])
def upload():
    if "user_id" not in session:
        return redirect("/login")

    file = request.files.get("file")
    if not file or file.filename == "":
        return redirect("/dashboard")

    folder = request.form.get("folder", "")
    user_id = session["user_id"]

    if folder:
        s3_key = f"{user_id}/{folder}/{file.filename}"
    else:
        s3_key = f"{user_id}/{file.filename}"

    # Read file size before uploading
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)

    # Guess file type from extension
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "unknown"

    upload_file(file, s3_key)
    save_file_metadata(user_id, file.filename, s3_key, folder, file_size, ext)

    return redirect(f"/dashboard?folder={folder}" if folder else "/dashboard")


@file_bp.route("/create-folder", methods=["POST"])
def create_folder_route():
    if "user_id" not in session:
        return redirect("/login")

    folder_name = request.form.get("folder_name", "").strip()
    parent_folder = request.form.get("parent_folder", "")

    if not folder_name:
        return redirect(f"/dashboard?folder={parent_folder}" if parent_folder else "/dashboard")

    create_folder(session["user_id"], folder_name, parent_folder)

    return redirect(f"/dashboard?folder={parent_folder}" if parent_folder else "/dashboard")


@file_bp.route("/rename", methods=["POST"])
def rename():
    if "user_id" not in session:
        return redirect("/login")

    file_id = request.form.get("file_id", "")
    new_name = request.form.get("new_name", "").strip()
    folder = request.form.get("folder", "")

    if not file_id or not new_name:
        return redirect(f"/dashboard?folder={folder}" if folder else "/dashboard")

    item = get_item_by_id(file_id)
    if not item or item.get("user_id") != session["user_id"]:
        return redirect(f"/dashboard?folder={folder}" if folder else "/dashboard")

    if item.get("item_type") == "folder":
        rename_item(file_id, new_name)
    else:
        old_s3_key = item.get("s3_key", "")
        if old_s3_key:
            parts = old_s3_key.rsplit("/", 1)
            new_s3_key = f"{parts[0]}/{new_name}" if len(parts) > 1 else new_name
            rename_s3_object(old_s3_key, new_s3_key)
            rename_item(file_id, new_name, new_s3_key)

    return redirect(f"/dashboard?folder={folder}" if folder else "/dashboard")


@file_bp.route("/download/<path:s3_key>")
def download(s3_key):
    if "user_id" not in session:
        return redirect("/login")

    url = generate_download_url(s3_key)
    return redirect(url)


@file_bp.route("/delete/<path:s3_key>")
def delete(s3_key):
    if "user_id" not in session:
        return redirect("/login")

    folder = request.args.get("folder", "")

    delete_file(s3_key)
    delete_file_metadata_by_s3_key(s3_key)

    return redirect(f"/dashboard?folder={folder}" if folder else "/dashboard")


@file_bp.route("/delete-folder")
def delete_folder():
    if "user_id" not in session:
        return redirect("/login")

    folder_path = request.args.get("path", "")
    parent = request.args.get("parent", "")

    if folder_path:
        delete_folder_and_contents(session["user_id"], folder_path)

    return redirect(f"/dashboard?folder={parent}" if parent else "/dashboard")