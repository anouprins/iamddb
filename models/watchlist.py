import requests
from typing import Union

from ..db.models import db
from ..db.models import Watchlist as WatchlistDB


class Watchlist():
    def add_item(self, tmdb_id: str, user_id: int, media_type: str) -> None:
        """ Stores tmdb item with user id in 'to_watch' list in database """
        item = WatchlistDB(tmdb_id=tmdb_id, user_id=user_id)
        db.session.add(item)
        db.session.commit()

    def remove_item(self, tmdb_id: str, user_id: int) -> None:
        """ Removes tmdb and user connection from database """
        obj = db.session.query(WatchlistDB).filter(tmdb_id==tmdb_id).filter(user_id==user_id).first()
        db.session.delete(obj)
        
#        db.delete(ToWatchDB).where(ToWatchDB.user_id == user_id).where(ToWatchDB.tmdb_id == tmdb_id)
        db.session.commit()
