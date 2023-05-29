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
from .models.reviews import Review
from .models.lists import List
from .models.list_users import ListUser
from .models.list_items import ListItem
from .models.taste import Taste

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


@app.route("/taste", methods=["GET", "POST"])
@login_required
def taste():
    """ Taste page """
    with app.app_context():
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    # extract all personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    if request.method == "GET":
        return render_template("taste.html", username=username, list_items=list_items)

    else:
        if request.form.get("get_score"):
            taste = Taste()
            score = taste.get_score(user_id)

            return render_template("taste.html", score=score, username=username, list_items=list_items)

@app.route("/search", methods=["GET", "POST"])
def search():
    with app.app_context():
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    # extract all personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)
    if request.method == "GET":
        return render_template("search.html", username=username, list_items=list_items)

    else:
        page_nr = request.form.get("page_nr")
        search_value = request.form.get("search_value")
        search_type = request.form.get("search_type")

        search = Search()
        results = search.search(search_type, search_value, page_nr)
        if search_type == "movies" or search_type == "series":
            return render_template("searched.html", results=results, search_type=search_type, search_value=search_value, username=username, page_nr=page_nr)
        else:
            return render_template("search.html", username=username, list_items=list_items)


@app.route("/")
def index():
    with app.app_context():
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    return render_template("index.html", username=username)


@app.route("/watchlist", methods=["GET"])
@login_required
def watchlist():
    """ Watchlist page """
    with app.app_context():
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""
    watchlist = Watchlist()
    watchlist_tmdb = watchlist.get_all_items_user(user_id)

    # extract all personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)


    movies = Movie()
    series = Serie()

    watchlist_data = {}

    # add each media object to watched dict
    for item in watchlist_tmdb:
        if item.media_type == "movie":
            movie = movies.check_and_retrieve_database(item.tmdb_id)
            watchlist_data[item.tmdb_id] = [movie[0]]

        elif item.media_type == "serie":
            # extract serie data
            serie = series.check_and_retrieve_database(item.tmdb_id)
            # extract data for last episode watched
            episodes = Episode()
            last_episode = episodes.lookup_last_watched(item.tmdb_id, user_id)

            item_list = [serie[0], last_episode]

            # add serie data to dictionary
            watchlist_data[item.tmdb_id] = item_list

    if request.method == "GET":
        return render_template("watchlist.html", watchlist_data=watchlist_data, username=username, list_items=list_items)


@app.route("/watched", methods=["GET"])
@login_required
def watched():
    """ Watched page """
    with app.app_context():
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

        watched = Watched()
        watched_tmdb = watched.get_all_items_user(user_id)

        # extract all personal list data
        list_item = List()
        list_items = list_item.get_all_items(user_id)

        movies = Movie()
        series = Serie()

        watched_data = {}

        # add each media object to watched dict
        for item in watched_tmdb:
            if item.media_type == "movie":
                movie = movies.check_and_retrieve_database(item.tmdb_id)
                watched_data[item.tmdb_id] = [movie[0]]

            elif item.media_type == "serie":
                # extract serie data
                serie = series.check_and_retrieve_database(item.tmdb_id)
                # extract data for last episode watched
                episodes = Episode()
                last_episode = episodes.lookup_last_watched(item.tmdb_id, user_id)

                item_list = [serie[0], last_episode]

                # add serie data to dictionary
                watched_data[item.tmdb_id] = item_list

    if request.method == "GET":
        return render_template("watched.html", watched_data=watched_data, username=username, list_items=list_items)


@app.route("/create_list/<media_type>/<tmdb_id>", methods=["GET", "POST"])
@login_required
def create_list(media_type, tmdb_id):
    """ Create new list page """
    with app.app_context():
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    # extract all personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    if request.method == "GET":
        return render_template("create_list.html", list_items=list_items, username=username, media_type=media_type, tmdb_id=tmdb_id)

    else:
        # get list title input
        list_title = request.form.get("list_title")

        # ensure list_title is filled in
        if not list_title:
            return render_template("create_list.html", username=username, list_items=list_items, error="empty_form", media_type=media_type, tmdb_id=tmdb_id)

        # make list object
        list_obj = List()
        list_obj.add_item(list_title, user_id)

        # add tmdb_id to new list
        list_item = ListItem()
        list_item.add_item(list_title, tmdb_id, user_id, media_type)

        # extract new personal list data
        list_items = list_item.get_all_items(user_id, list_title)

        return render_template("create_list.html", list_items=list_items, username=username, media_type=media_type, tmdb_id=tmdb_id)


@app.route("/list/<title>/", methods=["GET", "POST"])
@login_required
def list(title):
    """ List page """
    with app.app_context():
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    list_item = ListItem()
    list_items = list_item.get_all_items(user_id, title)

    movies = Movie()
    series = Serie()
    list_objects = {}

    # add each media object to watched dict
    for item in list_items:
        if item.media_type == "movie":
            movie = movies.check_and_retrieve_database(item.tmdb_id)
            list_objects[item.tmdb_id] = [movie[0]]

        elif item.media_type == "serie":
            # extract serie data
            serie = series.check_and_retrieve_database(item.tmdb_id)

            # extract data for last episode watched
            episodes = Episode()
            last_episode = episodes.lookup_last_watched(item.tmdb_id, user_id)

            item_list = [serie[0], last_episode]

            # add serie data to dictionary
            list_objects[item.tmdb_id] = item_list

    return render_template("list.html", username=username, list_objects=list_objects, list_title=title, list_items=list_items)


@app.route("/series/<tmdb_id>/", methods=["GET", "POST"])
@login_required
def series(tmdb_id):
    """ Series page """
    with app.app_context():

        # extract username and user_id
        user_id = session.get("user_id")
        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    # make models to work with database
    serie = Serie()
    episodes = Episode()

    # extract all personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    # extract serie data

    serie_data = serie.check_and_retrieve_database(tmdb_id)[0]

    # extract watched episodes and last episode
    watched_episodes = episodes.lookup_watched_episodes(tmdb_id, user_id)
    last_episode = episodes.lookup_last_watched(tmdb_id, user_id)

    # get bools for if movie is in list
    in_watchlist = serie.in_list("watchlist", user_id, tmdb_id)
    in_watched = serie.in_list("watched", user_id, tmdb_id)

    # extract review data
    reviews = Review()
    all_reviews = reviews.get_all_reviews(tmdb_id)

    # extract data and add all seasons from database to dict
    season_data = {}
    for season_nr in range(1, serie_data.seasons_amt+1):
        season_details = serie.lookup_season_tmdb(tmdb_id, season_nr)
        season_data[season_nr] = len(season_details["episodes"])

    if request.method == "GET":
        watched_episodes = episodes.lookup_watched_episodes(tmdb_id, user_id)
        last_episode = episodes.lookup_last_watched(tmdb_id, user_id)
        return render_template("serie.html", serie=serie_data, username=username, season_data=season_data, watched_episodes=watched_episodes, last_episode=last_episode, all_reviews=all_reviews, list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

    else:
        list_type = request.form.get("list_value")
        media_type = "serie"
        submit_value = request.form.get("submit_value")
        watchlist = Watchlist()

        if list_type == 'add to watchlist' or list_type == "remove from watchlist":
            watchlist.update_item(tmdb_id, user_id, media_type)
            in_watchlist = serie.in_list("watchlist", user_id, tmdb_id)

        if list_type == 'watched' or list_type == "unwatched":
            watched = Watched()
            watched.update_item(tmdb_id, user_id, media_type)
            in_watched = serie.in_list("watched", user_id, tmdb_id)

        if submit_value == "watched episodes":
            checked_episodes = [form_value[form_value.index('_') + 1:] for form_value in request.form if form_value.startswith('episode')]

            episodes.evaluate_checked_episodes(tmdb_id, user_id, checked_episodes)

            watched_episodes = episodes.lookup_watched_episodes(tmdb_id, user_id)
            last_episode = episodes.lookup_last_watched(tmdb_id, user_id)

        if list_type == "list":
            list_title = request.form.get("list_title")

            # do nothing if instruction was submitted
            if list_title == "Add to personal list":
                return render_template("serie.html", serie=serie_data, season_data=season_data, username=username, all_reviews=all_reviews, watched_episodes=watched_episodes, last_episode=last_episode, list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

            # create new list
            elif list_title == "new_list":
                return redirect(f"/create_list/{media_type}/{tmdb_id}")

            else:
                # add movie to existing list
                list_item = ListItem()
                list_item.add_item(list_title, tmdb_id, user_id, media_type)

        # add reviews
        if request.form.get("review"):
            review = request.form.get("review")
            rating = request.form.get("rating")

            # ensure a filled in review
            if not request.form.get("review"):
                return render_template("serie.html", serie=serie_data, season_data=season_data, username=username, all_reviews=all_reviews, watched_episodes=watched_episodes, last_episode=last_episode, error="empty_form", list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

            # ensure a filled in rating
            if not request.form.get("rating"):
                return render_template("serie.html", serie=serie_data, season_data=season_data, username=username, all_reviews=all_reviews, watched_episodes=watched_episodes, last_episode=last_episode, error="empty_form", list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

            # add review
            add_review = reviews.add_review(tmdb_id, user_id, rating, review)
            all_reviews = reviews.get_all_reviews(tmdb_id)

            # only add one review per person
            if not add_review:
                return render_template("serie.html", serie=serie_data, season_data=season_data, username=username, all_reviews=all_reviews, error="review_unavailable", watched_episodes=watched_episodes, last_episode=last_episode, list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

        return render_template("serie.html", serie=serie_data, username=username, season_data=season_data, watched_episodes=watched_episodes, last_episode=last_episode, all_reviews=all_reviews, list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

@app.route("/movies/<tmdb_id>/", methods=["GET", "POST"])
@login_required
def movies(tmdb_id):
    """ Movie page """
    with app.app_context():
        user_id = session.get("user_id")
        movie = Movie()
        movie_data = movie.check_and_retrieve_database(tmdb_id)[0]

        reviews = Review()
        all_reviews = reviews.get_all_reviews(tmdb_id)

        if user_id:
            user = User()
            username = user.get_username(user_id)

        else:
            username = ""

    # extract all personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    # get bools for if movie is in list
    in_watchlist = movie.in_list("watchlist", user_id, tmdb_id)
    in_watched = movie.in_list("watched", user_id, tmdb_id)

    if request.method == "GET":
        return render_template("movie.html", movie=movie_data, username=username, all_reviews=all_reviews, list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

    else:
        list_type = request.form.get("list_value")
        media_type = "movie"
        watchlist = Watchlist()

        if list_type == 'add to watchlist' or list_type == "remove from watchlist":
            watchlist.update_item(tmdb_id, user_id, media_type)
            in_watchlist = movie.in_list("watchlist", user_id, tmdb_id)

        if list_type == 'watched' or list_type == "unwatched":
            watched = Watched()
            watched.update_item(tmdb_id, user_id, media_type)
            in_watched = movie.in_list("watched", user_id, tmdb_id)

        if list_type == "list":
            list_title = request.form.get("list_title")

            # do nothing if instruction was submitted
            if list_title == "Add to personal list":
                return render_template("movie.html", movie=movie_data, username=username, all_reviews=all_reviews, list_items=list_items, in_watched=in_watched, in_watchlist=in_watchlist)

            # create new list
            elif list_title == "new_list":
                return redirect(f"/create_list/{media_type}/{tmdb_id}")

            else:
                # add movie to existing list
                list_item = ListItem()
                list_item.add_item(list_title, tmdb_id, user_id, media_type)

        if request.form.get("review"):
            review = request.form.get("review")
            rating = request.form.get("rating")

            # ensure a filled in review
            if not request.form.get("review"):
                return render_template("movie.html", movie=movie_data, username=username, all_reviews=all_reviews, error="empty_form", in_watched=in_watched, in_watchlist=in_watchlist)

            # ensure a filled in rating
            if not request.form.get("rating"):
                return render_template("movie.html", movie=movie_data, username=username, all_reviews=all_reviews, error="empty_form", in_watched=in_watched, in_watchlist=in_watchlist)

            # add review
            add_review = reviews.add_review(tmdb_id, user_id, rating, review)
            all_reviews = reviews.get_all_reviews(tmdb_id)

            # only add one review per person
            if not add_review:
                return render_template("movie.html", movie=movie_data, username=username, all_reviews=all_reviews, error="review_unavailable", in_watched=in_watched, in_watchlist=in_watchlist)

        return render_template("movie.html", movie=movie_data, username=username, all_reviews=all_reviews, in_watched=in_watched, in_watchlist=in_watchlist)

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
