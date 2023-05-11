import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from .helpers import login_required, pwd_match
from .models.users import *
from .models.movies import Movie, Serie

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/movies/<imdb_id>/", methods=["GET", "POST"])
def movies(imdb_id):
    """ Movie page """
    with app.app_context():
        user_id = session.get("user_id")
        media = Media()
        movie = media.lookup_movie(imdb_id)


    if request.method == "GET":
        #return movie_data
        return render_template("movie.html", movie=movie)

    pass


@app.route("/series/<tmdb_id>/", methods=["GET", "POST"])
def series(tmdb_id):
    """ Series page """
    with app.app_context():
        user_id = session.get("user_id")
        serie = Serie()
        serie.add_serie_database(tmdb_id)
        serie.lookup_season(tmdb_id, 1)

    if request.method == "GET":
        return render_template("series.html", serie=serie)

    pass


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not request.form.get("username"):
            return render_template("register.html", password=password, error="empty_form")

        elif not request.form.get("password"):
            return render_template("register.html", password=password, error="empty_form")

        elif not request.form.get("confirmation"):
            return render_template("register.html", password=password, error="empty_form")

        # error if passwords don't match
        if not pwd_match(password, confirmation):
            return render_template("register.html", password=password, error="password_incorrect")

        # register user in database
        with app.app_context():
            user = User()

            # error if not username already exists
            if not user.register_user(username, password):
                return render_template("register.html", error="username_unavailable")

        return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":
        return render_template("login.html")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", error="empty_form")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", error="empty_form")

        with app.app_context():
            user = User()
            if not user.login_user(username, password):
                return render_template("login.html", error="password_incorrect")

        # Remember which user has logged in
        session["user_id"] = user.get_id_user(username)

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
