"""
Movie model to manipulate "series" table in IAMDDB database

Movie data is retrieved by connecting to free TMDB database with personal API key, if movie data not yet in IAMDDB database.
The relevant data is then added to IAMDDB database for future use.
Source -- https://developer.themoviedb.org/docs
"""
import requests
from typing import Union


from ..db.models import db
from ..db.models import Movie as MovieDB
from .to_watch import Watchlist
from .watched import Watched
from .lists import List


class Movie():
    def lookup_movie_tmdb(self, tmdb_id: str) -> Union[dict, None]:
        """ Returns all movie information in json using TMDB Api """
        # query movie details
        response = requests.get(f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key=669cfa65918d52531e6700a94982ea26&append_to_response=videos,images")
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

    def check_and_retrieve_database(self, tmdb_id: str) -> None:
        """ Adds relevant movie info to iamddb database if not yet in database """
        # add movie to database if not yet there
        if not self.in_database_iamddb(tmdb_id):
            self.add_database_iamddb(tmdb_id)

        # return movie object
        movie = self.lookup_movie_iamddb(tmdb_id)
        return movie

    def lookup_movie_iamddb(self, tmdb_id: str) -> None:
        """ Returns movie object from iamddb database """
        movie = MovieDB.query.filter_by(tmdb_id=tmdb_id).all()
        return movie

    def in_database_iamddb(self, tmdb_id: str) -> bool:
        """ Returns True if all episodes of series are stored in iamddb database """
        movie = self.lookup_movie_iamddb(tmdb_id)

        if movie == []:
            return False

        return True

    def in_list(self, list_title: str, user_id: int, tmdb_id: str) -> bool:
        """ Returns True if movie in list object, False otherwise """
        if list_title == "watchlist":
            list_obj = Watchlist()
            return list_obj.connection_exists(tmdb_id, user_id)

        elif list_title == "watched":
            list_obj = Watched()
            return list_obj.connection_exists(tmdb_id, user_id)

        else:
            list_obj = List()
            return list_obj.item_exists(tmdb_id, user_id, list_title)

    def add_database_iamddb(self, tmdb_id: str) -> bool:
        """ Adds all relevant details from serie to iamddb database """
        details = self.lookup_movie_tmdb(tmdb_id)

        try:
            spoken_languages = details["spoken_languages"][0]["english_name"]
        except Exception:
            spoken_languages = ""

        title = details["title"]
        poster_path = details["poster_path"]
        release_date = details["release_date"]
        tagline = details["tagline"]
        media_type = "movie"

        if details["video"] is True:
            video_key = details["video"]["results"][0]["key"]
            video_site = details["video"]["results"][0]["site"]
            # add movie object
            movie = MovieDB(tmdb_id=tmdb_id,
                            title=title,
                            tagline=tagline,
                            poster_path=poster_path,
                            release_date=release_date,
                            spoken_languages=spoken_languages,
                            video_key=video_key,
                            video_site=video_site,
                            media_type=media_type)

        else:
            # add movie object
            movie = MovieDB(tmdb_id=tmdb_id,
                            title=title,
                            tagline=tagline,
                            poster_path=poster_path,
                            release_date=release_date,
                            spoken_languages=spoken_languages,
                            media_type=media_type)

        db.session.add(movie)
        db.session.commit()

        genres = details["genres"]

        # TODO
        # add cast movie
        # add directors movie


        # add each genre object
        for item in genres:
            genre = GenreDB(tmdb_id=tmdb_id, name=item["name"])
            db.session.add(genre)
            db.session.commit()

