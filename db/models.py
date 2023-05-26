from flask_sqlalchemy import SQLAlchemy
import datetime

from .users import User

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    media_type = db.Column(db.String, nullable=False)
    tmdb_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, nullable=False)
    poster_path = db.Column(db.String, nullable=True)
    release_date = db.Column(db.String, nullable=True)
    spoken_languages = db.Column(db.String, nullable=True)
    video = db.Column(db.String, nullable=True)
    tagline = db.Column(db.String, nullable=True)
    video_key = db.Column(db.String, nullable=True)
    video_site = db.Column(db.String, nullable=True)


class Serie(db.Model):
    __tablename__ = "series"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    media_type = db.Column(db.String, nullable=False)
    tmdb_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    tagline = db.Column(db.String, nullable=True)
    poster_path = db.Column(db.String, nullable=True)
    last_air_date = db.Column(db.String, nullable=True)
    first_air_date = db.Column(db.String, nullable=True)
    spoken_languages = db.Column(db.String, nullable=False)
    video_key = db.Column(db.String, nullable=True)
    video_site = db.Column(db.String, nullable=True)
    seasons_amt = db.Column(db.Integer, nullable=False)


class Season(db.Model):
    __tablename__ = "seasons"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    serie_title = db.Column(db.String, nullable=False)
    episodes_amt = db.Column(db.Integer, nullable=True)
    air_date = db.Column(db.String, nullable=True)
    poster_path = db.Column(db.String, nullable=True)
    season_nr = db.Column(db.Integer, nullable=False)


class Episode(db.Model):
    __tablename__ = "episodes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    season_nr = db.Column(db.Integer, nullable=False)
    episode_nr = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    watched = db.Column(db.Boolean, default=False, nullable=False)


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)


class People(db.Model):
    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class Actors(db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)


class Director(db.Model):
    __tablename__ = "directors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)


class Watchlist(db.Model):
    __tablename__ = "to_watch"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String, nullable=False)

class Watched(db.Model):
    __tablename__ = "watched"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    media_type = db.Column(db.String, nullable=False)

class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    media_type = db.Column(db.String, nullable=False)

class ListUser(db.Model):
    __tablename__ = "list_users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_id = db.Column(db.Integer, db.ForeignKey("lists.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    tmdb_id = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    review_text = db.Column(db.String, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    datetime = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
