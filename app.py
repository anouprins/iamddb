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
from .models.to_watch import Watchlist
from .models.watched import Watched

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
        search_value = request.form.get("search_value")
        search_type = request.form.get("search_type")
        search = Search()

        if search_type == "movies":
            results = search.search_movies(search_value, page_nr)
            return render_template("searched.html", results=results, search_type=search_type, search_value=search_value)

        elif search_type == "series":
            results = search.search_series(search_value, page_nr)
            return render_template("searched.html", results=results, search_type=search_type, search_value=search_value)

        else:
            return render_template("search.html")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/watchlist", methods=["GET"])
@login_required
def watchlist():
    """ Watchlist page """
    with app.app_context():
        user_id = session.get("user_id")
        watchlist = Watchlist()

        watchlist_tmdb = watchlist.get_all_items_user(user_id)

        movies = Movie()
        series = Serie()

        watchlist_data = {}

        # add each media object to watched dict
        for item in watchlist_tmdb:
            if item[1] == "movie":
                movie = movies.check_and_retrieve_database(item[0])
                watchlist_data[movie[0].tmdb_id] = movie

            elif item[1] == "serie":
                # extract serie data
                serie = series.check_and_retrieve_database(item[0])

                # extract data for last episode watched
                episodes = Episode()
                last_episode = episodes.lookup_last_watched(serie[0].tmdb_id, user_id)
                serie.append(last_episode)

                # add serie data to dictionary
                watchlist_data[serie[0].tmdb_id] = serie

    if request.method == "GET":
        return render_template("watchlist.html", watchlist_data=watchlist_data)


@app.route("/watched", methods=["GET"])
@login_required
def watched():
    """ Watched page """
    user_id = session.get("user_id")
    user = User()
    username = user.get_username(user_id)

    with app.app_context():
        watched = Watched()
        watched_tmdb = watched.get_all_items_user(user_id)

        movies = Movie()
        series = Serie()

        watched_data = {}

        # add each media object to watched dict
        for item in watched_tmdb:
            if item.media_type == "movie":
                movie = movies.check_and_retrieve_database(item.tmdb_id)
                watched_data[movie[0].tmdb_id] = movie

            elif item.media_type == "serie":
                # extract data for serie
                serie = series.check_and_retrieve_database(item.tmdb_id)

                # extract data for last episode watched
                episodes = Episode()
                last_episode = episodes.lookup_last_watched(serie[0].tmdb_id, user_id)
                serie.append(last_episode)

                # add serie data to dictionary
                watched_data[serie[0].tmdb_id] = serie

    if request.method == "GET":
        return render_template("watched.html", watched_data=watched_data, username=username)


@app.route("/movies/<tmdb_id>/", methods=["GET", "POST"])
@login_required
def movies(tmdb_id):
    """ Movie page """
    with app.app_context():
        user_id = session.get("user_id")
        movie = Movie()
        movie_data = movie.check_and_retrieve_database(tmdb_id)[0]


        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""


    if request.method == "GET":
        return render_template("movie.html", movie=movie_data, username=username)

    else:
        list_type = request.form.get("list_value")
        media_type = "movie"
        watchlist = Watchlist()

        if list_type == 'add to watchlist':
            watchlist.add_item(tmdb_id, user_id, media_type)

        if list_type == 'watched':
            watched = Watched()
            watched.add_item(tmdb_id, user_id, media_type)

            # remove item from watchlist if existent in watchlist
            if watchlist.connection_exists(tmdb_id, user_id):
                watchlist.remove_item(tmdb_id, user_id)

        return render_template("movie.html", movie=movie_data, username=username)


@app.route("/series/<tmdb_id>/", methods=["GET", "POST"])
@login_required
def series(tmdb_id):
    """ Series page """
    with app.app_context():

        # make models to work with database
        serie = Serie()
        season = Season()

        # extract serie data
        serie_data = serie.check_and_retrieve_database(tmdb_id)[0]


        # extract data and add all seasons from database to dict
        season_data = {}
        for season_nr in range(1, serie_data.seasons_amt+1):
            season_details = serie.lookup_season_tmdb(tmdb_id, season_nr)
            season_data[season_nr] = len(season_details["episodes"])


        # extract username
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    episodes = Episode()

    if request.method == "GET":
        watched_episodes = episodes.lookup_watched_episodes(tmdb_id, user_id)
        last_episode = episodes.lookup_last_watched(tmdb_id, user_id)
        return render_template("serie.html", serie=serie_data, username=username, season_data=season_data, watched_episodes=watched_episodes, last_episode=last_episode)

    else:
        list_type = request.form.get("list_value")
        media_type = "serie"
        submit_value = request.form.get("submit_value")
        watchlist = Watchlist()

        if list_type == 'add to watchlist':
            watchlist.add_item(tmdb_id, user_id, media_type)

        if list_type == 'watched':
            watched = Watched()
            watched.add_item(tmdb_id, user_id, media_type)

            # remove item from watchlist if existent in watchlist
            if watchlist.connection_exists(tmdb_id, user_id):
                watchlist.remove_item(tmdb_id, user_id)

        if submit_value == "watched episodes":
            checked_episodes = [form_value[form_value.index('_') + 1:] for form_value in request.form if form_value.startswith('episode')]

            for episode in checked_episodes:
                # extract season_nr and episode_nr from form values
                season_nr = episode[:episode.index('.')]
                episode_nr = episode[episode.index('.')+1:]

                # set episode as watched in database
                episodes.add_watched(tmdb_id, season_nr, episode_nr, user_id)

        watched_episodes = episodes.lookup_watched_episodes(tmdb_id, user_id)
        last_episode = episodes.lookup_last_watched(tmdb_id, user_id)
        return render_template("serie.html", serie=serie_data, username=username, season_data=season_data, watched_episodes=watched_episodes, last_episode=last_episode)


@app.route("/series/<tmdb_id>/season/<season_nr>/", methods=["GET", "POST"])
def season(tmdb_id, season_nr):
    """ Season page """
    with app.app_context():
        user_id = session.get("user_id")
        season = Season()
        season_data = season.check_and_retrieve_database(tmdb_id, season_nr)[0]

        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    if request.method == "GET":
        return render_template("season.html", season=season_data, username=username)


@app.route("/series/<tmdb_id>/season/<season_nr>/episode/<episode_nr>", methods=["GET", "POST"])
def episode(tmdb_id, season_nr, episode_nr):
    """ Series page """
    with app.app_context():
        user_id = session.get("user_id")
        episode = Episode()
        episode_data = episode.check_and_retrieve_database(tmdb_id, season_nr, episode_nr)

        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    if request.method == "GET":
        return render_template("episode.html ", episode=episode_data, username=username)


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
        return render_template("index.html", username=username)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
