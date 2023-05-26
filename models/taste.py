import requests
from typing import Union

from ..db.models import db
from .to_watch import Watchlist
from .movies import Movie
from .serie import Serie

class Taste():
    def get_score(self, user_id: int):
        """ Returns total popularity score based average of tmdb popularity scores of movies in watchlist """
        # get all items watchlist
        items = self.get_all_tmdb_watchlist(user_id)

        return self.calculate_score(items)

    def get_all_tmdb_watchlist(self, user_id: int) -> list:
        """ Returns a list of all tmdb items in watchlist """
        watchlist = Watchlist()
        items = watchlist.get_all_items_user(user_id)
        return items

    def calculate_score(self, watchlist_items: list) -> list:
        """ Returns accumulation of all tmdb scores """

        total_score = 0
        items_amt = len(watchlist_items)

        for item in watchlist_items:
            score = self.get_popularity_score(item.tmdb_id, item.media_type)
            total_score += score

        score = total_score / items_amt
        return score

    def get_popularity_score(self, tmdb_id: str, media_type: str):
        """ Returns the popularity score from tmdb database """
        if media_type == "serie":
            serie = Serie()
            serie_data = serie.lookup_serie_tmdb(tmdb_id)
            score = serie_data["popularity"]

        elif media_type == "movie":
            movie = Movie()
            movie_data = movie.lookup_movie_tmdb(tmdb_id)
            score = movie_data["popularity"]

        return score
