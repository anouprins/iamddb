from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)


class Media(db.Model):
    __tablename__ = "media"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, nullable=False)


class Movie(db.Model):
    __tablename__ = "movies"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, db.ForeignKey("media.tmdb_id"), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    poster_path = db.Column(db.String, nullable=True)
    release_date = db.Column(db.String, nullable=False)
    spoken_languages = db.Column(db.String, nullable=False)
    video = db.Column(db.String, nullable=True)
    tagline = db.Column(db.String, nullable=True)


class Serie(db.Model):
    __tablename__ = "series"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, db.ForeignKey("media.tmdb_id"), nullable=False)
    title = db.Column(db.String, nullable=False)
    episodes_amt = db.Column(db.Integer, nullable=False)
    tagline = db.Column(db.String, nullable=True)
    poster_path = db.Column(db.String, nullable=True)
    last_air_date = db.Column(db.String, nullable=False)
    first_air_date = db.Column(db.String, nullable=False)
    spoken_languages = db.Column(db.String, nullable=False)
    video = db.Column(db.String, nullable=True)


class Episode(db.Model):
    __tablename__ = "episodes"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, db.ForeignKey("media.tmdb_id"), nullable=False)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    season_nr = db.Column(db.Integer, nullable=False)
    episode_nr = db.Column(db.Integer, nullable=False)


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, db.ForeignKey("media.tmdb_id"), nullable=False)
    genre = db.Column(db.String, nullable=False)


class People(db.Model):
    __tablename__ = "people"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)


class Actors(db.Model):
    __tablename__ = "actors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, db.ForeignKey("media.tmdb_id"), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)


class Director(db.Model):
    __tablename__ = "directors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tmdb_id = db.Column(db.String, db.ForeignKey("media.tmdb_id"), nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey("people.id"), nullable=False)
