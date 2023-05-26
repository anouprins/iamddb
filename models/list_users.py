import requests
from typing import Union

from ..db.models import db
from ..db.models import List as ListDB, ListUser as ListUserDB


class ListUser():
    def add_users(self, users: list, list_id: int) -> None:
        """ Adds all connected users of a list to database table "list_users" """
        # iterate over all users
        for user in users:
            # connect them to list only if not yet connected
            if not self.item_exists(user, list_id):
                self.create_item(user, list_id)

    def create_item(self, user_id: int, list_id: int) -> None:
        """ Creates a list user item and adds it to table "list_users" in database """
        item = ListUserDB(user_id=user_id, list_id=list_id)

        # add object to database
        db.session.add(item)
        db.session.commit()

    def item_exists(self, user_id: int, list_id: int) -> bool:
        """ Returns True if user is connected to list """
        items = db.session.query(ListUserDB).filter(ListUserDB.user_id==user_id,
                                                    ListUserDB.list_id==list_id).all()

        if items == []:
            return False

        return True
