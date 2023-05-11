from helpers import *
from db.models import User as UserDB
from db.models import db


class User():
    """ Class User that works with the table users from database """
    def lookup_user(self, username):
        user = UserDB.query.filter_by(username=username).all()
        return user

    def get_id_user(self, username):
        user = self.lookup_user(username)
        return user[0].id

    def get_username(self, user_id: int) -> str:
        """ Returns username from user id in string """
        user = UserDB.query.filter_by(id=user_id).all()[0]
        return user.username

    def register_user(self, username: str, password: str) -> bool:
        """ Registers user in database """
        # only proceed if username is unique
        if not self.username_available(username) or username == "":
            return False

        # hash password
        hash_pwd = get_hash_pwd(password)

        # create user and add to database
        user = UserDB(username=username, password=hash_pwd)
        db.session.add(user)
        db.session.commit()

        return True

    def login_user(self, username: str, password: str):
        """ Login user by verifying username and password """
        if self.verify_user(username, password):
            return True

        return False

    def verify_user(self, username: str, password):
        """ Returns user data if user in database """
        # assuming that only one person has that username,
        # we only check if passwords match
        user = self.lookup_user(username)

        if check_hash_pwd(user[0].password, password):
            return True
        return False

    def username_available(self, username) -> bool:
        """ Returns True if username is available, False otherwise """
        if self.lookup_user(username) != []:
            return False
        return True
