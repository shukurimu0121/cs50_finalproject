from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import calendar
from datetime import datetime, timedelta

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

# is_teacher
def is_teacher(user_id):
    usertype = db.execute("SELECT type FROM users WHERE id = ?", user_id)[0]["type"]
    if usertype != "teacher":
        return False
    else:
        return True

def get_calendar_html(year):
    now = datetime(year, 1, 1)
    end = datetime(year, 12, 31)
    html = "<table border='1'>"

    while now.year == year:
        html += "<tr><td colspan='7' align='center'><b>" + now.strftime("%B %Y") + "</b></td></tr>"
        html += "<tr><td>Mo</td><td>Tu</td><td>We</td><td>Th</td><td>Fr</td><td>Sa</td><td>Su</td></tr>"
        html += "<tr>"
        first_weekday, last_day = calendar.monthrange(now.year, now.month)
        current_day = 1
        while current_day <= last_day:
            html += "<td>" + str(current_day) + "</td>"
            if (first_weekday + current_day - 1) % 7 == 6:
                html += "</tr><tr>"
            current_day += 1
            if current_day <= last_day:
                first_weekday = 0
        now += timedelta(days=last_day)

    html += "</table>"
    return html

# each route
@app.route("/")
@login_required
def index():
    """Show user's schedule"""
    # Get user_id
    user_id = session["user_id"]

    # If user is teacher
    if is_teacher(user_id) == True:
        classes = db.execute("SELECT * FROM classes WHERE user_id = ?", user_id)
        return render_template("index.html", classes=classes)

    # If user is student
    else:
        username = db.execute("SELECT name FROM users WHERE id = ?", user_id)[0]["name"]
        classes = db.execute("SELECT * FROM classes WHERE studentname LIKE '%?%'", username)
        return render_template("index.html", classes=classes)

@app.route("/deregister", methods=["POST"])
def deregister():
    """Deregister class"""
     # Delete the class

    # Only teacher or student can delete the class
    # If teacher
    if is_teacher(user_id) == True:
        # Check user is a teacher of the class
        teacherid = db.execute("SELECT user_id FROM classes WHERE id = ?", classeid)[0]["user_id"]
        if user_id == teacherid:
            db.execute("DELETE FROM classes WHERE id = ?", classid)
        else:
            return render_template("apology.html", msg="You can delete only your class.")

    else:
        # Check user is a student of the class
        studentname1 = db.execute("SELECT studentname FROM classes WHERE id = ?", classeid)[0]["studentname"]
        studentname2 = db.execute("SELECT name FROM users WHERE id = ?", user_id)[0]["name"]

        if studentname1 == studentname2:
            db.execute("DELETE FROM classes WHERE id = ?", classid)
        else:
            return render_template("apology.html", msg="You can delete only your class.")

@app.route("/calender")
@login_required
def calender():
    """Show Entire Class Calendar and Print"""
    # Only teacher can use
    # get user's type from database
    user_id = session["user_id"]
    if is_teacher(user_id) == False:
        return render_template("apology.html", msg="Only teacher can use this page")

    # Get datetime now
    dt_now = datetime.now()
    year = dt_now.year
    html = get_calendar_html(year)

    return render_template("calendar.html", html=html)


@app.route("/course", methods=["GET", "POST"])
@login_required
def course():
    """Course Setting"""
    # Only teacher can use
    # get user's type from database
    user_id = session["user_id"]
    if is_teacher(user_id) == False:
        return render_template("apology.html", msg="Only teacher can use this page")

    SUBJECTS = ["Language", "Classic", "Moth", "English", "History", "Physics", "Chemistry"]
    MONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    DAYS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]
    MINUTES = [00, 15, 30, 45]

    # When POST
    if request.method == "POST":
        # Get from request
        teachername = request.form.get("teachername")
        studentname = request.form.get("studentname")
        subject = request.form.get("subject")
        month = int(request.form.get("month"))
        day = int(request.form.get("day"))
        hour = int(request.form.get("hour"))
        minute = int(request.form.get("minute"))

        # Check the form is correct
        if not teachername or not studentname or not subject or not month or not day or not hour or not minute:
            return render_template("apology.html", msg="must provide input")

        if subject not in SUBJECTS or month not in MONTHS or day not in DAYS or hour not in HOURS or minute not in MINUTES:
            return render_template("apology.html", msg="must provide accurate input")

        # Teacher can register only their own course
        teacher = db.execute("SELECT name FROM users WHERE id = ?", user_id)[0]["name"]
        if teachername != teacher:
            return render_template("apology.html", msg="Register only your class")

        # Insert to database
        db.execute("INSERT INTO classes (user_id, teachername, studentname, subject, month, day, hour, minute) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", user_id, teachername, studentname, subject, month, day, hour, minute)
        return redirect("/")

    # When GET
    else:
        return render_template("course.html", subjects=SUBJECTS, months=MONTHS, days=DAYS, hours=HOURS, minutes=MINUTES)

@app.route("/entire")
@login_required
def entire():
    "Show Entire Schedule to only teacher"
    # Only teacher can use
    # get user's type from database
    user_id = session["user_id"]
    if is_teacher(user_id) == False:
        return render_template("apology.html", msg="Only teacher can use this page")

    # Display entire schedule
    classes = db.execute("SELECT * FROM classes ORDER BY month, day, hour, minute")
    return render_template("entire.html", classes=classes)

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
        rows = db.execute("SELECT * FROM users WHERE name = ?", username)

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
    # Two User Type
    TYPES = ["teacher", "student"]

    # When POST
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        usertype = request.form.get("type")

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

        # Check type is valid
        elif usertype not in TYPES:
            return render_template("apology.html", msg="Invalid Type")


        # Check the username already exists
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE name = ?", username)
        if rows or rows == None:
            return render_template("apology.html", msg="the username is already used")

        else:
            # Insert username and password hash to table
            password_hash = generate_password_hash(password)
            db.execute("INSERT INTO users (name, hash, type) VALUES(?, ?, ?)", username, password_hash, usertype)

            # redirect log in page
            return redirect("/")

    else:
        return render_template("register.html", types=TYPES)



