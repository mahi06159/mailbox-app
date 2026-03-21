import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Secret key (important for sessions)
app.secret_key = os.environ.get("SECRET_KEY", "dev")

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure DB exists (important for Render)
if not os.path.exists("project.db"):
    open("project.db", "w").close()

# Configure database
db = SQL("sqlite:///project.db")
# Create tables if not exist
# ✅ Auto create tables (IMPORTANT for Render)
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
)
""")

db.execute("""
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# ✅ FIXED HOME ROUTE
@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/login")

    userId = session["user_id"]
    usernameDB = db.execute("SELECT username FROM users WHERE id = ?", userId)

    if not usernameDB:
        return redirect("/login")

    username = usernameDB[0]["username"]
    emails = db.execute("SELECT * FROM emails WHERE recipient = ?", username)

    return render_template("index.html", emails=emails)


@app.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    if request.method == "GET":
        userId = session["user_id"]
        senderDB = db.execute("SELECT username FROM users WHERE id = ?", userId)
        sender = senderDB[0]["username"]
        return render_template("compose.html", sender=sender)

    sender = request.form.get("sender")
    recipient = request.form.get("recipient")
    subject = request.form.get("subject")
    body = request.form.get("body")

    if not sender or not recipient or not subject or not body:
        return apology("No Empty Fields")

    db.execute(
        "INSERT INTO emails (sender, recipient, subject, body) VALUES (?, ?, ?, ?)",
        sender, recipient, subject, body
    )

    return redirect("/sent")


@app.route("/sent")
@login_required
def sent():
    userId = session["user_id"]
    usernameDB = db.execute("SELECT username FROM users WHERE id = ?", userId)
    username = usernameDB[0]["username"]
    emails = db.execute("SELECT * FROM emails WHERE sender = ?", username)
    return render_template("index.html", emails=emails)


# ✅ FIXED LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username:
            return apology("must provide username", 403)
        if not password:
            return apology("must provide password", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        if len(rows) != 1:
            return apology("invalid username", 403)

        if not check_password_hash(rows[0]["hash"], password):
            return apology("invalid password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/email", methods=["POST"])
@login_required
def email():
    emailId = request.form.get("emailId")

    emailDetailDB = db.execute("SELECT * FROM emails WHERE id = ?", emailId)

    if not emailDetailDB:
        return apology("Email not found")

    emailDetail = emailDetailDB[0]
    return render_template("email.html", emailDetail=emailDetail)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    email = request.form.get("email")
    password = request.form.get("password")
    confirm = request.form.get("confirm")

    if not email or not password or not confirm:
        return apology("No Empty Fields")

    if password != confirm:
        return apology("Passwords Do Not Match")

    hash_pw = generate_password_hash(password)

    try:
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            email, hash_pw
        )
    except:
        return apology("Email Already Used")

    user = db.execute("SELECT id FROM users WHERE username = ?", email)

    if not user:
        return apology("Registration failed")

    session["user_id"] = user[0]["id"]
    return redirect("/")


@app.route("/reply", methods=["POST"])
@login_required
def reply():
    emailId = request.form.get("emailId")

    emailDetailDB = db.execute("SELECT * FROM emails WHERE id = ?", emailId)

    if not emailDetailDB:
        return apology("Email not found")

    emailDetail = emailDetailDB[0]
    return render_template("reply.html", emailDetail=emailDetail)
