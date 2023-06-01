"""
App file for IAMDDB website.


Page routes
-- search movies or series, using TMDB database
-- serie page, shows serie info, user can add serie to lists(watchlist, watched, personal lists), user can add/remove episodes as watched, user can add reviews, reviews are shown
-- movie page, shows movie info, user can add movie to lists(watchlist, watched, personal lists), user can add reviews, reviews are shown
-- watched page, all movies and series in list are shown
-- watchlist page, all movies and series in list are shown
-- list page, all movies and series in list are shown
-- taste page, shows popularity average of users watchlist
-- login page
-- logout
-- register


for serie and movie pages, serie/movie data is retrieved from:
--- TMDB database if not yet in IAMDDB database, and serie data will be put in IAMDDB database for future
--- IAMDDB database if already in IAMDDB database

source TMDB database: https://developer.themoviedb.org/docs

by: Anou Prins
"""
import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


from .helpers import login_required, pwd_match, get_list_dict, create_list_item, get_season_data
from .models.users import *
from .models.serie import Serie
from .models.movies import Movie
from .models.episodes import Episode
from .models.search import Search
from .models.to_watch import Watchlist
from .models.watched import Watched
from .models.reviews import Review
from .models.lists import List
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
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    list_item = List()
    list_items = list_item.get_all_items(user_id)

    if request.method == "GET":
        return render_template("taste.html",
                               username=username,
                               list_items=list_items)

    if request.method == "POST":
        # return score page if pushed on score button
        if request.form.get("get_score"):

            # calculate score for user's watchlist
            taste = Taste()
            score = taste.get_score(user_id)

            # return score page
            return render_template("taste.html",
                                   score=score,
                                   username=username,
                                   list_items=list_items)


@app.route("/search", methods=["GET", "POST"])
def search():
    """ Search page """
    with app.app_context():
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    # list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    if request.method == "GET":
        # return search page
        return render_template("search.html",
                               username=username,
                               list_items=list_items)

    elif request.method == "POST":
        page_nr = request.form.get("page_nr")
        search_value = request.form.get("search_value")
        search_type = request.form.get("search_type")

        # empty form error
        if not search_type:
            return render_template("search.html",
                                   username=username,
                                   list_items=list_items,
                                   error="empty_form")

        # empty form error
        elif not search_value:
            return render_template("search.html",
                                   username=username,
                                   list_items=list_items,
                                   error="empty_form")

        # search results
        search = Search()
        results = search.search(search_type, search_value, page_nr)

        # results page
        if search_type == "movies" or search_type == "series":
            return render_template("searched.html",
                                   results=results,
                                   search_type=search_type,
                                   search_value=search_value,
                                   username=username,
                                   page_nr=page_nr)


@app.route("/")
def index():
    """ Index page """
    with app.app_context():
        # extract user info
        username = session.get("username")

    # return index page
    return render_template("index.html", username=username)


@app.route("/watchlist", methods=["GET"])
@login_required
def watchlist():
    """ Watchlist page """
    with app.app_context():
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    # list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    watchlist = Watchlist()
    watchlist_tmdb = watchlist.get_all_items_user(user_id)
    watchlist_data = get_list_dict(watchlist_tmdb, user_id)

    if request.method == "GET":

        # return watchlist page
        return render_template("watchlist.html",
                               list_items=list_items,
                               watchlist_data=watchlist_data,
                               username=username)


@app.route("/watched", methods=["GET"])
@login_required
def watched():
    """ Watched page """
    with app.app_context():
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    # list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    # watched data
    watched = Watched()
    watched_list = watched.get_all_items_user(user_id)
    watched_data = get_list_dict(watched_list, user_id)

    if request.method == "GET":

        # return watched page
        return render_template("watched.html",
                               watched_data=watched_data,
                               list_items=list_items,
                               username=username)


@app.route("/create_list/<media_type>/<tmdb_id>", methods=["GET", "POST"])
@login_required
def create_list(media_type, tmdb_id):
    """ Create new list page """
    with app.app_context():
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    # list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    if request.method == "GET":
        return render_template("create_list.html",
                               username=username,
                               list_items=list_items,
                               media_type=media_type,
                               tmdb_id=tmdb_id)

    elif request.method == "POST":
        list_title = request.form.get("list_title")

        # empty title error
        if not list_title:
            return render_template("create_list.html",
                                   username=username,
                                   list_items=list_items,
                                   media_type=media_type,
                                   tmdb_id=tmdb_id,
                                   error="empty_form")

        # add list and list item to new list
        create_list_item(list_title, tmdb_id, user_id, media_type)

        return redirect(f"/list/{list_title}")


@app.route("/list/<title>/", methods=["GET", "POST"])
@login_required
def list(title):
    """ List page """
    with app.app_context():
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    # extract list items
    list_obj = List()
    list_items = list_obj.get_all_items(user_id)

    list_item = ListItem()
    list_item_list = list_item.get_all_items(user_id, title)
    list_data = get_list_dict(list_item_list, user_id)

    # return list page
    return render_template("list.html",
                           username=username,
                           list_data=list_data,
                           list_title=title,
                           list_items=list_items)


@app.route("/series/<tmdb_id>/", methods=["GET", "POST"])
@login_required
def series(tmdb_id):
    """ Series page """
    with app.app_context():
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    # extract personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    # initialize serie and episode models
    serie = Serie()
    episodes = Episode()

    # extract serie data
    serie_data = serie.check_and_retrieve_database(tmdb_id)[0]
    season_data = get_season_data(serie_data, tmdb_id)

    # exntract watched episodes and last episode
    watched_episodes = episodes.lookup_watched_episodes(tmdb_id, user_id)
    last_episode = episodes.lookup_last_watched(tmdb_id, user_id)

    # get bools for if serie is in list
    in_watchlist = serie.in_list("watchlist", user_id, tmdb_id)
    in_watched = serie.in_list("watched", user_id, tmdb_id)

    # extract review data
    reviews = Review()
    all_reviews = reviews.get_all_reviews(tmdb_id)

    if request.method == "GET":
        # return serie page
        return render_template("serie.html",
                               serie=serie_data,
                               username=username,
                               season_data=season_data,
                               watched_episodes=watched_episodes,
                               last_episode=last_episode,
                               all_reviews=all_reviews,
                               list_items=list_items,
                               in_watched=in_watched,
                               in_watchlist=in_watchlist)

    elif request.method == "POST":
        list_type = request.form.get("list_value")
        media_type = "serie"
        submit_value = request.form.get("submit_value")
        watchlist = Watchlist()
        watched = Watched()

        # button watchlist
        if list_type == 'add to watchlist' or list_type == "remove from watchlist":
            watchlist.update_item(tmdb_id, user_id, media_type)
            in_watchlist = serie.in_list("watchlist", user_id, tmdb_id)

        # button watched list
        if list_type == 'watched' or list_type == "unwatched":
            watched.update_item(tmdb_id, user_id, media_type)

            # remove item from watchlist
            if in_watchlist and list_type == "watched":
                watchlist.update_item(tmdb_id, user_id, media_type)
                in_watchlist = False

            in_watched = serie.in_list("watched", user_id, tmdb_id)

        # button watched episodes
        if submit_value == "watched episodes":
            checked_episodes = [form_value[form_value.index('_') + 1:]
                                for form_value in request.form if form_value.startswith('episode')]

            episodes.evaluate_checked_episodes(tmdb_id, user_id, checked_episodes)

            # re-evaluate watched episodes and last episode watched
            watched_episodes = episodes.lookup_watched_episodes(tmdb_id, user_id)
            last_episode = episodes.lookup_last_watched(tmdb_id, user_id)

        # button list
        if list_type == "list":
            list_title = request.form.get("list_title")

            # instruction text was submitted
            if list_title == "Add to personal list":

                # return serie page
                return render_template("serie.html",
                                       serie=serie_data,
                                       season_data=season_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       watched_episodes=watched_episodes,
                                       last_episode=last_episode,
                                       list_items=list_items,
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist)

            # new list
            elif list_title == "new_list":
                return redirect(f"/create_list/{media_type}/{tmdb_id}")

            else:
                # existing list
                list_item.add_item(list_title, tmdb_id, user_id, media_type)

        # add review
        if request.form.get("review"):
            review = request.form.get("review")
            rating = request.form.get("rating")

            # ensure a filled in review
            if not request.form.get("review"):
                return render_template("serie.html",
                                       serie=serie_data,
                                       season_data=season_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       watched_episodes=watched_episodes,
                                       last_episode=last_episode,
                                       error="empty_form",
                                       list_items=list_items,
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist)

            # ensure a filled in rating
            if not request.form.get("rating"):
                return render_template("serie.html",
                                       serie=serie_data,
                                       season_data=season_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       watched_episodes=watched_episodes,
                                       last_episode=last_episode,
                                       error="empty_form",
                                       list_items=list_items,
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist)

            # add review
            add_review = reviews.add_review(tmdb_id, user_id, rating, review)
            all_reviews = reviews.get_all_reviews(tmdb_id)

            # only add one review per person
            if not add_review:
                return render_template("serie.html",
                                       serie=serie_data,
                                       season_data=season_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       error="review_unavailable",
                                       watched_episodes=watched_episodes,
                                       last_episode=last_episode,
                                       list_items=list_items,
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist)

        # return serie page
        return render_template("serie.html",
                               serie=serie_data,
                               username=username,
                               season_data=season_data,
                               watched_episodes=watched_episodes,
                               last_episode=last_episode,
                               all_reviews=all_reviews,
                               list_items=list_items,
                               in_watched=in_watched,
                               in_watchlist=in_watchlist)


@app.route("/movies/<tmdb_id>/", methods=["GET", "POST"])
@login_required
def movies(tmdb_id):
    """ Movie page """
    with app.app_context():
        # extract user info
        user_id = session.get("user_id")
        username = session.get("username")

    # extract movie data
    movie = Movie()
    movie_data = movie.check_and_retrieve_database(tmdb_id)[0]

    # extract review data
    reviews = Review()
    all_reviews = reviews.get_all_reviews(tmdb_id)

    # extract personal list data
    list_item = List()
    list_items = list_item.get_all_items(user_id)

    # get bools for if movie is in list
    in_watchlist = movie.in_list("watchlist", user_id, tmdb_id)
    in_watched = movie.in_list("watched", user_id, tmdb_id)

    if request.method == "GET":

        # return movie page
        return render_template("movie.html",
                               movie=movie_data,
                               username=username,
                               all_reviews=all_reviews,
                               list_items=list_items,
                               in_watched=in_watched,
                               in_watchlist=in_watchlist)

    elif request.method == "POST":

        # extract form values
        list_type = request.form.get("list_value")
        media_type = "movie"
        watchlist = Watchlist()

        # button watchlist
        if list_type == 'add to watchlist' or list_type == "remove from watchlist":
            watchlist.update_item(tmdb_id, user_id, media_type)
            in_watchlist = movie.in_list("watchlist", user_id, tmdb_id)

        # button watched
        if list_type == 'watched' or list_type == "unwatched":
            watched = Watched()
            watched.update_item(tmdb_id, user_id, media_type)

            # re-evaluate if movie in watched list
            in_watched = movie.in_list("watched", user_id, tmdb_id)

        # button list
        if list_type == "list":

            # extract form value
            list_title = request.form.get("list_title")

            # do nothing if instruction text was submitted
            if list_title == "Add to personal list":

                # return movie page
                return render_template("movie.html", movie=movie_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       list_items=list_items,
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist)

            # create new list
            elif list_title == "new_list":
                return redirect(f"/create_list/{media_type}/{tmdb_id}")

            else:
                # add movie to existing list
                list_item = ListItem()
                list_item.add_item(list_title, tmdb_id, user_id, media_type)

        # review button
        if request.form.get("review"):

            # extract form values
            review = request.form.get("review")
            rating = request.form.get("rating")

            # return error statement if review is empty
            if not request.form.get("review"):
                return render_template("movie.html",
                                       movie=movie_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       error="empty_form",
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist,
                                       list_items=list_items)

            # return error statement if rating is empty
            if not request.form.get("rating"):
                return render_template("movie.html",
                                       movie=movie_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       error="empty_form",
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist,
                                       list_items=list_items)
            # add review
            add_review = reviews.add_review(tmdb_id, user_id, rating, review)

            # re-evaluate reviews list
            all_reviews = reviews.get_all_reviews(tmdb_id)

            # only add one review per person
            if not add_review:
                return render_template("movie.html",
                                       movie=movie_data,
                                       username=username,
                                       all_reviews=all_reviews,
                                       error="review_unavailable",
                                       in_watched=in_watched,
                                       in_watchlist=in_watchlist,
                                       list_items=list_items)
        # return movie page
        return render_template("movie.html",
                               movie=movie_data,
                               username=username,
                               all_reviews=all_reviews,
                               in_watched=in_watched,
                               in_watchlist=in_watchlist,
                               list_items=list_items)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        # return register page
        return render_template("register.html")

    elif request.method == "POST":

        # extract form values
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # return error statement if empty username
        if not request.form.get("username"):
            return render_template("register.html", password=password, error="empty_form")

        # return error statement if empty password
        elif not request.form.get("password"):
            return render_template("register.html", password=password, error="empty_form")

        # return error statement if empty confirmation
        elif not request.form.get("confirmation"):
            return render_template("register.html", password=password, error="empty_form")

        # return error statement if confirmation different from password
        if not pwd_match(password, confirmation):
            return render_template("register.html", password=password, error="password_incorrect")

        # register user in database
        if not user.register_user(username, password):
            return render_template("register.html", error="username_unavailable")

        # return login page
        return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Login page """

    # forget old user_id
    session.clear()

    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        # form values
        username = request.form.get("username")
        password = request.form.get("password")
        user = User()

        # empty username page
        if not request.form.get("username"):
            return render_template("login.html", error="empty_form")

        # empty password page
        elif not request.form.get("password"):
            return render_template("login.html", error="empty_form")

        # password incorrect page
        if not user.login_user(username, password):
            return render_template("login.html", error="password_incorrect")

        # Remember user
        session["user_id"] = user.get_id_user(username)
        session["username"] = username

        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # forget old user_id
    session.clear()

    # redirect user to login form
    return redirect("/")
