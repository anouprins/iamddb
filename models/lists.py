"""
List model to manipulate table "lists" in IAMDDB database

Functions
add_item -- makes use of item_exists and create_item to add item to database
item_exists -- checks if list exists
create_item -- adds item to database

"""


from ..db.models import db
from ..db.models import List as ListDB


class List():
    def add_item(self, title: str, user_id: int) -> None:
        """ Uses item_exists and create_item to add item to IAMDDB database
        Parameters
        title -- list title
        user_id -- user id """

        # only add list if not yet existent
        if not self.item_exists(title, user_id):
            self.create_item(title, user_id)

    def item_exists(self, title: str, user_id: int) -> bool:
        """ Returns True if item exists, False otherwise
        Parameters
        title -- list title
        user_id -- user id 

        Returns
        bool -- True if item exists in iamddb database, False otherwise"""

        # extract item from database
        items = db.session.query(ListDB).filter(
            ListDB.title==title,
            ListDB.user_id==user_id).all()

        # item does not exist
        if items == []:
            return False

        # item exists
        return True

    def create_item(self, title, user_id) -> None:
        """ Creates a list item in table "lists" in iamddb database
        Parameters
        title -- list title
        user_id -- user id 
        """
        # create List object
        item = ListDB(title=title, user_id=user_id)

        # add object to database
        db.session.add(item)
        db.session.commit()

    def get_all_items(self, user_id: int) -> list:
        """ Returns all list items for user
        Parameters
        user_id -- user id 

        Returns
        items -- list of all list items for user"""

        # extract list items from iamddb database
        items = db.session.query(ListDB).filter(
            ListDB.user_id==user_id).all()
        return items
