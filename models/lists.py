import requests
from typing import Union

from ..db.models import db
from ..db.models import List as ListDB
from .list_users import ListUser


class List():
    def add_item(self, tmdb_id: str, user_id: int, media_type: str, title: str, users: list) -> None:
        """ Stores tmdb item with user id in list in database if not already existent """
        # only create list item if not yet existent in database
        if not self.item_exists(tmdb_id, user_id, title):
            self.create_item(tmdb_id, user_id, media_type, title)

        breakpoint()
        list_id = self.lookup_id(title, user_id)
        list_users = ListUser()
        list_users.add_users(users, list_id)

    def create_item(self, tmdb_id: str, user_id: int, media_type: str, title: str) -> None:
        """ Creates a list item in list database """
        item = ListDB(tmdb_id=tmdb_id, user_id=user_id, media_type=media_type)

        # add object to database
        db.session.add(item)
        db.session.commit()

    def item_exists(self, tmdb_id: str, user_id: int, title: str) -> bool:
        """ Returns True if list exists with given title for user """
        items = db.session.query(ListDB).filter(ListDB.tmdb_id==tmdb_id,
                                                ListDB.user_id==user_id,
                                                ListDB.title==title).all()

        if items == []:
            return False

        return True        

    def lookup_id(self, title: str, user_id: int) -> int:
        """ Returns list id of list with given title for user """
        items = db.session.query(ListDB).filter(ListDB.tmdb_id==tmdb_id, ListDB.user_id==user_id, ListDB.title==title).all()
        return items[0].id

    def get_all_items_user(self, user_id: int):
        """ Returns all items in watchlist for user """
        items = db.session.query(ListDB).filter(ListDB.user_id==user_id).all()
        return items

