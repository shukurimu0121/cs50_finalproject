from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///schedule.db")

# login required
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# each route
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show user's schedule"""

@app.route("/course", methods=["GET", "POST"])
@login_required
def course():
    """Course Setting"""
    # Only teacher can use
    # get user's type from database
    user_id = session["user_id"]
    usertype = db.execute("SELECT type FROM users WHERE id = ?", user_id)[0]["type"]
    if usertype != "teacher":
        return render_template("apology.html", msg="Only teacher can use this page")

    # When POST
    if request.method = "POST":
        

    # When GET
    else:
        return render_template("course.html")



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
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return render_template("apology.html", msg="invalid username or password")

        # All OK add user to session
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # When GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # When POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return render_template("apology.html", msg="must provide username")

        # Ensure password was submitted
        elif not password:
            return render_template("apology.html", msg="must provide password")

        # Ensure password was submitted again
        elif not confirmation:
            return render_template("apology.html", msg="must provide password again")

        # password matches confirmation
        elif password != confirmation:
            return render_template("apology.html", msg="must provide the same passwords")

        # Check the username already exists
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if rows:
            return render_template("apology.html", msg="the username is already used")

        else:
            # Insert username and password hash to table
            password_hash = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, password_hash)

            # redirect log in page
            return redirect("/")

    else:
        return render_template("register.html")



