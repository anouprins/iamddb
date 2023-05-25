import requests
from typing import Union

from ..db.models import db
from ..db.models import Watchlist as WatchlistDB


class Watchlist():
    def add_item(self, tmdb_id: str, user_id: int, media_type: str) -> None:
        """ Stores tmdb item with user id in 'to_watch' list in database """
        #if not self.connection_exists(tmdb_id, user_id):
        item = WatchlistDB(tmdb_id=tmdb_id, user_id=user_id, media_type=media_type)
        db.session.add(item)
        db.session.commit()

    def remove_item(self, tmdb_id: str, user_id: int) -> None:
        """ Removes tmdb and user connection from database """
        obj = db.session.query(WatchlistDB).filter(tmdb_id==tmdb_id).filter(user_id==user_id).first()
        db.session.delete(obj)
        
#        db.delete(ToWatchDB).where(ToWatchDB.user_id == user_id).where(ToWatchDB.tmdb_id == tmdb_id)
        db.session.commit()

    def connection_exists(self, tmdb_id: str, user_id: int) -> bool:
        """ Returns True if connection exists in iamddb database """
        items = db.session.execute(db.select(WatchlistDB).where(user_id == user_id).where(tmdb_id == tmdb_id))
        breakpoint()


    def get_all_items_user(self, user_id: int):
        """ Returns all items in watchlist for user """
        items = db.session.execute(
            db.select(WatchlistDB.tmdb_id, WatchlistDB.media_type).where(user_id == user_id))
        all_items = items.all()
        return all_items
        
