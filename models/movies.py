
import requests
from typing import Union

from ..db.models import db
from ..db.models import Movie as MovieDB, Serie as SerieDB, Media as MediaDB, Genre as GenreDB, Episode as EpisodeDB, People as PeopleDB, Actors as ActorsDB, Director as DirectorDB
from ..db.models import Episode, Genre

""" Functions to get movie data from tmbd Api database"""

class Movie():
    def lookup_movie(self, tmdb_id: str) -> Union[dict, None]:
        """ Returns all movie information in json using TMDB Api """
        # query movie details
        response = requests.get(f"https://api.themoviedb.org/3/movie/{imdb_id}?api_key=669cfa65918d52531e6700a94982ea26&append_to_response=videos,images")
        data = response.json()

        # return details if found successfully
        if self.successful_tmdb(data):
            return data

        return None

    def successful_tmdb(self, data: dict) -> bool:
        """ Returns True if details query is successful, False otherwise """
        try:
            if data["success"] == False:
                return False

        except Exception:
            return True

    def add_database(self, tmdb_id: str) -> None:
        """ Adds relevant movie info to iamddb database if not yet in database """
        if self.in_database(tmdb_id):
            return True

        pass

    def in_database(self, tmdb_id: str) -> bool:
        """ Returns True if movie is stored in iamddb database """
        pass


class Serie():
    def lookup_serie(self, tmdb_id: str) -> Union[dict, None]:
        """ Returns all movie information in json using TMDB Api """
        # query serie details
        response = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key=669cfa65918d52531e6700a94982ea26&append_to_response=videos,images, aggregate_credits")
        data = response.json()

        # return details if found successfully
        if self.successful_tmdb(data):
            return data

        raise Exception("tmdb_invalid")

    def lookup_season(self, tmdb_id: str, season_nr: int) -> Union[list, None]:
        """ Returns all season information in json using TMDB Api """
        # query serie details
        response = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_nr}?api_key=669cfa65918d52531e6700a94982ea26&append_to_response=videos,images, aggregate_credits")
        data = response.json()

        # return details if found successfully
        if self.successful_tmdb(data):
            return data

        raise Exception("tmdb_invalid")

    def successful_tmdb(self, data: dict) -> bool:
        """ Returns True if details query is successful, False otherwise """
        try:
            if data["success"] == False:
                return False

        except Exception:
            return True

    def check_database(self, tmdb_id: str) -> None:
        """ Adds relevant movie info to iamddb database if not yet in database """
        if self.in_database(tmdb_id):
            return True

        self.add_serie_database(tmdb_id)

    def in_database(self, tmdb_id: str) -> bool:
        """ Returns True if all episodes of series are stored in iamddb database """
        serie = SerieDB.query.filter_by(tmdb_id=tmdb_id).all()

        if serie == []:
            return False

        return True

    def add_serie_database(self, tmdb_id: str) -> bool:
        """ Adds all relevant details from serie to iamddb database """
        details = self.lookup_serie(tmdb_id)

        title = details["name"]
        spoken_languages = details["spoken_languages"][0]["english_name"]
        poster_path = details["poster_path"]
        first_air_date = details["first_air_date"]
        last_air_date = details["last_air_date"]
        video = details["videos"]
        tagline = details["tagline"]
        episodes_amt = details["number_of_episodes"]

        genres = details["genres"]

        # add media object
        media = MediaDB(tmdb_id=tmdb_id)

        # add serie object
        serie = SerieDB(tmdb_id=tmdb_id,
                        title=title,
                        episodes_amt=episodes_amt,
                        tagline=tagline,
                        poster_path=poster_path,
                        last_air_date=last_air_date,
                        first_air_date=first_air_date,
                        spoken_languages=spoken_languages,
                        video=video)

        # add each genre object
        for item in genres:
            genre = GenreDB(tmdb_id=tmdb_id, genre=item["name"])
            db.session.add(genre)

        db.session.add(serie)
        db.session.add(media)
        db.session.commit()



# class Episode(db.Model):
#     __tablename__ = "episodes"
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     iamddb_id = db.Column(db.Integer, db.ForeignKey("media.id"), nullable=False)
#     title = db.Column(db.String, nullable=False)
#     description = db.Column(db.String, nullable=True)
#     tmdb_id = db.Column(db.String, nullable=False)
#     season_nr = db.Column(db.Integer, nullable=False)
#     episode_nr = db.Column(db.Integer, nullable=False)

