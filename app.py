import os

from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from .helpers import login_required, pwd_match
from .models.users import *
from .models.serie import Serie
from .models.movies import Movie
from .models.episodes import Episode
from .models.seasons import Season
from .models.search import Search

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

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "GET":
        return render_template("search.html")

    else:
        page_nr = request.form.get("page_nr")
        search_value = request.form.get("search")
        search_type = request.form.get("search_type")
        search = Search()

        if search_type == "movies":
            results = search.search_movies(search_value, page_nr)
            return render_template("searched.html", results=results, search_type=search_type)

        elif search_type == "series":
            results = search.search_series(search_value, page_nr)
            return render_template("searched.html", results=results, search_type=search_type)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/movies/<tmdb_id>/", methods=["GET", "POST"])
def movies(tmdb_id):
    """ Movie page """
    with app.app_context():
        user_id = session.get("user_id")
        movie = Movie()
        movie_data = movie.check_and_retrieve_database(tmdb_id)[0]

    if request.method == "GET":
        #return movie_data
        return render_template("movie.html", movie=movie_data)

    pass


@app.route("/series/<tmdb_id>/", methods=["GET", "POST"])
def series(tmdb_id):
    """ Series page """
    with app.app_context():
        user_id = session.get("user_id")
        serie = Serie()
        serie_data = serie.check_and_retrieve_database(tmdb_id)[0]

    if request.method == "GET":
        return render_template("serie.html", serie=serie_data)

    pass


@app.route("/series/<tmdb_id>/season/<season_nr>/", methods=["GET", "POST"])
def season(tmdb_id, season_nr):
    """ Season page """
    with app.app_context():
        user_id = session.get("user_id")
        season = Season()
        season_data = season.check_and_retrieve_database(tmdb_id, season_nr)[0]
    if request.method == "GET":
        return render_template("season.html", season=season_data)


@app.route("/series/<tmdb_id>/season/<season_nr>/episode/<episode_nr>", methods=["GET", "POST"])
def episode(tmdb_id, season_nr, episode_nr):
    """ Series page """
    with app.app_context():
        user_id = session.get("user_id")
        episode = Episode()
        episode_data = episode.check_and_retrieve_database(tmdb_id, season_nr, episode_nr)

    if request.method == "GET":
        return render_template("episode.html ", episode=episode_data)

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
