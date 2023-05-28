import requests
from typing import Union

from ..db.models import db
from ..db.models import List as ListDB


class List():
    def add_item(self, title: str, user_id: int) -> None:
        """ Creates list item """
        if not self.item_exists(title, user_id):
            self.create_item(title, user_id)

    def item_exists(self, title: str, user_id: int) -> bool:
        """ Returns True if item exists, False otherwise """
        items = db.session.query(ListDB).filter(ListDB.title==title,
                                                ListDB.user_id==user_id).all()

        if items == []:
            return False

        return True        

    def create_item(self, title, user_id) -> None:
        """ Creates a list item in table "lists" in iamddb database """
        item = ListDB(title=title, user_id=user_id)

        # add object to database
        db.session.add(item)
        db.session.commit()

    def get_all_items(self, user_id: int):
        """ Returns all tmdb items for user """
        items = db.session.query(ListDB).filter(ListDB.user_id==user_id).all()
        return items
