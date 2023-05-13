
import requests
from typing import Union

from ..db.models import db
from ..db.models import Movie as MovieDB, Genre as GenreDB, People as PeopleDB, Actors as ActorsDB, Director as DirectorDB

""" Functions to get movie data from tmbd Api database"""

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

    def add_database_iamddb(self, tmdb_id: str) -> bool:
        """ Adds all relevant details from serie to iamddb database """
        details = self.lookup_movie_tmdb(tmdb_id)

        title = details["title"]
        spoken_languages = details["spoken_languages"][0]["english_name"]
        poster_path = details["poster_path"]
        release_date = details["release_date"]
        tagline = details["tagline"]

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
                            video_site=video_site)

        else:
            # add movie object
            movie = MovieDB(tmdb_id=tmdb_id,
                            title=title,
                            tagline=tagline,
                            poster_path=poster_path,
                            release_date=release_date,
                            spoken_languages=spoken_languages)

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

