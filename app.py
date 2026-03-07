import boto3
from flask import Flask, render_template, session, redirect
from routes.auth_routes import auth_bp
from aws.dynamodb_service import get_user_files


app = Flask(__name__)
app.secret_key = "AWS_SECRET_KEY"

app.register_blueprint(auth_bp)



from aws.dynamodb_service import get_user_files

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    user_files = get_user_files(session["user_id"])

    return render_template(
        "dashboard.html",
        files=user_files
    )
@app.route("/")
def home():
    return redirect("/login")



from routes.file_routes import file_bp
app.register_blueprint(file_bp)

if __name__ == "__main__":
    app.run(debug=True)