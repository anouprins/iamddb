"""
These functions facilitate the running of app.py

Functions:
get_list_dict -- turns a list of list items into a dictionary with serie and movie objects
get_season_data -- retrieves all seasons and their episode amount in dict form
create_list_item -- creates new list and adds tmdb object to list
login_required -- wrapper that redirects user to login page if login needed to enter page
pwd_match -- checks if password and confirmation match for register page
get_hash_pwd -- turns password into hash string for register page
check_hash_pwd -- checks if password is same as hash password

by: Anou Prins

"""
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask import redirect, render_template, request, session
from .models.movies import Movie
from .models.serie import Serie
from .models.episodes import Episode
from .models.list_items import ListItem
from .models.lists import List

movies = Movie()
series = Serie()
episodes = Episode()


def get_list_dict(list_items: list, user_id: int) -> dict:
    """  Returns dict with serie and movie objects from list of list items

    Parameters
    list_items -- list of list items from IAMDDB list database

    Returns
    data -- dictionary of serie and movie objects"""

    data = {}

    # iterate over list items
    for item in list_items:

        # add movie to list dict
        if item.media_type == "movie":
            movie = movies.check_and_retrieve_database(item.tmdb_id)
            data[item.tmdb_id] = [movie[0]]

        # add serie and episode to watchlist dict
        elif item.media_type == "serie":
            serie = series.check_and_retrieve_database(item.tmdb_id)
            last_episode = episodes.lookup_last_watched(item.tmdb_id, user_id)

            # serie data list
            item_list = [serie[0], last_episode]

            # add serie data list to watchlist dict
            data[item.tmdb_id] = item_list

    return data


def get_season_data(serie_data: list, tmdb_id: str) -> dict:
    """ Returns dictionary of season data
    Parameters
    serie_data -- list of serie objects from IAMDDB database
    tmdb_id -- tmdb id

    Returns
    season_data -- dictionary of seasons as keys, episode amounts as values
"""
    season_data = {}

    # iterate over serie seasons
    for season_nr in range(1, serie_data.seasons_amt+1):
        season_details = series.lookup_season_tmdb(tmdb_id, season_nr)

        # add season data to season data dict
        season_data[season_nr] = len(season_details["episodes"])

    return season_data


def create_list_item(list_title: str, tmdb_id: str, user_id: int, media_type: str) -> None:
    """
    Adds new list object in table "lists", 
    and adds list item object in table "list_items" in IAMDDB database,
    using List and ListItem models
    """
    list_obj = List()
    list_item = ListItem()
    list_obj.add_item(list_title, user_id)
    list_item.add_item(list_title, tmdb_id, user_id, media_type)


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


def pwd_match(password: str, confirmation: str) -> bool:
    """ 
    Returns True if password and confirmation are the same and are not empty
    """
    # password should not be empty
    if not password or not confirmation:
        return False

    # password should match confirmation
    if password != confirmation:
        return False

    return True


def get_hash_pwd(password: str):
    """ Returns hashed version of string password """
    hash_pwd = generate_password_hash(
        password, method='pbkdf2:sha256', salt_length=8)
    return hash_pwd


def check_hash_pwd(hash_pwd, password) -> bool:
    """ Returns True if password is the same as hash password, False otherwise """
    return check_password_hash(hash_pwd, password)
