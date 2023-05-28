import requests
from typing import Union

from ..db.models import db
from ..db.models import Watched as WatchedDB

class Watched():
    def update_item(self, tmdb_id: str, user_id: int, media_type: str) -> None:
        """ Stores tmdb item with user id in 'to_watch' list in database if not already existent """
        # only add item if not already in database
        if not self.connection_exists(tmdb_id, user_id):
            # create object
            item = WatchedDB(tmdb_id=tmdb_id, user_id=user_id, media_type=media_type)

            # add object to database
            db.session.add(item)
            db.session.commit()

        else:
            self.remove_item(tmdb_id, user_id)

    def remove_item(self, tmdb_id: str, user_id: int) -> None:
        """ Removes tmdb and user connection from database """
        # only remove connection if connection exists
        if self.connection_exists:

            # query all items from database with matching user_id and tmdb_id
            items = db.session.query(WatchedDB).filter(WatchedDB.user_id==user_id, WatchedDB.tmdb_id==tmdb_id).all()

            # remove each item with matching connection
            for item in items:
                db.session.delete(item)
            db.session.commit()

    def connection_exists(self, tmdb_id: str, user_id: int) -> bool:
        """ Returns True if connection exists in iamddb database """
        # query all items from database with matching user_id and tmdb_id
        items = db.session.query(WatchedDB).filter(
            WatchedDB.user_id==user_id, WatchedDB.tmdb_id==tmdb_id).all()

        # connection does not exist if query returns empty list
        if items == []:
            return False

        # connection exists
        return True

    def get_all_items_user(self, user_id: int):
        """ Returns all items in watchlist for user """
        items = db.session.query(WatchedDB).filter(WatchedDB.user_id==user_id).all()
        return items
        
