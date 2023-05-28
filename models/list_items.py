import requests
from typing import Union

from ..db.models import db
from ..db.models import ListItem as ListItemDB
from ..db.models import List
from .movies import Movie
from .serie import Serie

class ListItem():
    def add_item(self, list_title: int, tmdb_id: str, user_id: int, media_type: str) -> None:
        """ Stores tmdb item with user id in list in database if not already existent """
        # only create list item if not yet existent in database
        if not self.item_exists(tmdb_id, user_id, list_title):
            self.create_item(list_title, tmdb_id, user_id, media_type)

    def create_item(self, list_title, tmdb_id: str, user_id: int, media_type: str) -> None:
        """ Creates a list item in list database """
        list_id = self.get_list_id(user_id, list_title)

        item = ListItemDB(list_id=list_id,
                          tmdb_id=tmdb_id,
                          title=list_title,
                          user_id=user_id,
                          media_type=media_type)

        # add object to database
        db.session.add(item)
        db.session.commit()

    def item_exists(self, tmdb_id: str, user_id: int, title: str) -> bool:
        """ Returns True if list exists with given title for user """
        items = db.session.query(ListItemDB).filter(ListItemDB.tmdb_id==tmdb_id,
                                                    ListItemDB.user_id==user_id,
                                                    ListItemDB.title==title).all()

        if items == []:
            return False

        return True        

    def get_all_items(self, user_id: int, list_title: str):
        """ Returns all listitems for given user and list title """
        items = db.session.query(ListItemDB).filter(
            ListItemDB.user_id==user_id,
            ListItemDB.title==list_title).all()
        return items

    def get_list_id(self, user_id: int, list_title: str) -> int:
        """ Returns list id """
        items = db.session.query(List).filter(List.user_id==user_id,
                                              List.title==list_title).all()

        if items == []:
            breakpoint()
        return items[0].id

    def get_serie_object(tmdb_id: str) -> Serie:
        """ Returns a serie object """
        series = Serie()
        serie = series.check_and_retrieve_database(tmdb_id)
        return serie

