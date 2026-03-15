from flask import Flask, render_template, session, redirect, request
from config import FLASK_SECRET_KEY
from routes.auth_routes import auth_bp
from routes.file_routes import file_bp, _format_size
from aws.dynamodb_service import get_user_files


app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

app.register_blueprint(auth_bp)
app.register_blueprint(file_bp)

# Make helper available in Jinja templates
app.jinja_env.globals["format_size"] = _format_size


@app.route("/")
def home():
    return redirect("/login")


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    current_folder = request.args.get("folder", "")
    user_files = get_user_files(session["user_id"], current_folder)

    # Build breadcrumb trail
    breadcrumbs = []
    if current_folder:
        parts = current_folder.split("/")
        for i, part in enumerate(parts):
            breadcrumbs.append({
                "name": part,
                "path": "/".join(parts[:i + 1])
            })

    return render_template(
        "dashboard.html",
        files=user_files,
        current_folder=current_folder,
        breadcrumbs=breadcrumbs
    )


if __name__ == "__main__":
    app.run(debug=True)