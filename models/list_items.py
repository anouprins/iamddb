""" ListItem model to manipulate ListItem in database """

from typing import Union

from ..db.models import db
from ..db.models import ListItem as ListItemDB
from ..db.models import List
from .serie import Serie


class ListItem():
    """ Model for database table "list_items" """

    def add_item(self, list_title: int, tmdb_id: str, user_id: int, media_type: str) -> None:
        """ Stores tmdb item with user id in list in database if not already existent
        Parameters
        list_title -- title of list in which tmdb item will be placed
        tmdb_id -- tmdb id
        user_id -- user id
        media_type -- media type: movie/serie"""
        # only create list item if not yet existent in database
        if not self.item_exists(tmdb_id, user_id, list_title):
            self.create_item(list_title, tmdb_id, user_id, media_type)

    def create_item(self, list_title, tmdb_id: str, user_id: int, media_type: str) -> None:
        """ Creates a list item in list database
        Parameters
        list_title -- title of list in which tmdb item will be placed
        tmdb_id -- tmdb id
        user_id -- user id
        media_type -- media type: movie/serie"""

        # extract list id
        list_id = self.get_list_id(user_id, list_title)

        # create list item object
        item = ListItemDB(list_id=list_id,
                          tmdb_id=tmdb_id,
                          title=list_title,
                          user_id=user_id,
                          media_type=media_type)

        # add object to database
        db.session.add(item)
        db.session.commit()

    def item_exists(self, tmdb_id: str, user_id: int, title: str) -> bool:
        """ Returns True if list exists with given title for user
        Parameters
        tmdb_id -- tmdb id
        user_id -- user id
        title -- list title

        Returns
        bool -- true if item exists in database, false otherwise"""

        # query item in database
        items = db.session.query(ListItemDB).filter(ListItemDB.tmdb_id==tmdb_id,
                                                    ListItemDB.user_id==user_id,
                                                    ListItemDB.title==title).all()

        # item does not exist
        if items == []:
            return False

        # item exists
        return True        

    def get_all_items(self, user_id: int, list_title: str) -> List:
        """ Returns list of all listitems for given user and list title
        Parameters
        user_id -- user id
        list_title -- list title

        Returns
        items -- list of all ListItem objects connected to given list"""

        # extract all list item objects from database
        items = db.session.query(ListItemDB).filter(
            ListItemDB.user_id==user_id,
            ListItemDB.title==list_title).all()

        return items

    def get_list_id(self, user_id: int, list_title: str) -> Union[None, int]:
        """ Returns list id
        Parameters
        user_id -- user id
        list_title -- list title

        Returns
        items[0].id -- id int for list object
        None -- list item does not exist
        """

        # extract list object from database
        items = db.session.query(List).filter(List.user_id==user_id,
                                              List.title==list_title).all()

        # list item does not exist
        if items == []:
            return None

        # return list id
        return items[0].id

    def get_serie_object(tmdb_id: str) -> Serie:
        """ Returns a serie object 
        Parameters
        tmdb_id -- tmdb id

        Returns
        serie -- serie object"""

        # extract serie object from tmdb or iamddb database
        series = Serie()
        serie = series.check_and_retrieve_database(tmdb_id)
        return serie
