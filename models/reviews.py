from ..db.models import Review as ReviewDB
from ..db.models import db
from .users import User

""" Review Model """


class Review():
    def add_review(self, tmdb_id: int, user_id: int, rating: int, review: str) -> bool:
        """ Registers a review into the review database if available """
        # only do review if available
        if self.review_available(tmdb_id, user_id):
            username = self.lookup_username(user_id)
            review = ReviewDB(review_text=review, user_id=user_id, tmdb_id=tmdb_id, rating=rating, username=username)
            db.session.add(review)
            db.session.commit()
            return True

        return False

    def lookup_username(self, user_id: int) -> str:
        """ Returns username from user id in string """
        user = User()
        username = user.get_username(user_id)
        return username

    def lookup_review(self, tmdb_id: int, user_id: int):
        """ Returns review from database by given user and for given book """
        review = ReviewDB.query.filter(ReviewDB.tmdb_id == tmdb_id, ReviewDB.user_id == user_id).all()
        return review

    def review_available(self, tmdb_id: int, user_id: int) -> bool:
        """ Returns True if user has not yet committed a review for book, False otherwise """
        if self.lookup_review(tmdb_id, user_id) != []:
            return False

        return True

    def get_all_reviews(self, tmdb_id: int):
        """ Returns all reviews from database in dictionary """
        reviews = ReviewDB.query.filter(tmdb_id==tmdb_id).all()
        return reviews
