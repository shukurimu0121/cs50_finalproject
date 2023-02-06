from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///schedule.db")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show user's schedule"""

@app.route("/course", methods=["GET", "POST"])
@login_required
def course():
    """Course Setting"""

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # When POST
    if request.method == "POST":
        # get the user's input
        username = request.form.get("username")
        password = request.form.get("password")

        # When invalid input
        if not username:
            return render_template("apology.html", msg="must provide username")

        elif not password:
            return render_template("apology.html", msg="must provide password")

        # Get all username from database
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Check the username and password are correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):

    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""



