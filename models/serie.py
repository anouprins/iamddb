
import requests
from typing import Union

from ..db.models import db
from ..db.models import Serie as SerieDB, Genre as GenreDB, Episode as EpisodeDB, People as PeopleDB, Actors as ActorsDB, Director as DirectorDB, Season as SeasonDB

class Serie():
    def lookup_serie_tmdb(self, tmdb_id: str) -> Union[dict, None]:
        """ Returns all movie information in json using TMDB Api """
        # query serie details
        response = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key=669cfa65918d52531e6700a94982ea26&append_to_response=videos,images, aggregate_credits")

        data = response.json()

        # return details if found successfully
        if self.successful_tmdb(data):
            return data

        raise Exception("tmdb_invalid")

    def lookup_serie_iamddb(self, tmdb_id: str) -> Union[dict, None]:
        """ Returns all movie information in json using TMDB Api """
        # query serie details
        serie = SerieDB.query.filter_by(tmdb_id=tmdb_id).all()
        return serie

    def lookup_season_tmdb(self, tmdb_id: str, season_nr: int) -> Union[list, None]:
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

    def check_and_retrieve_database(self, tmdb_id: str) -> None:
        """ Adds relevant serie info to iamddb database if not yet in database """
        # add serie to database if not yet there
        if not self.in_database_iamddb(tmdb_id):
            self.add_database_iamddb(tmdb_id)

        # return movie object
        serie = self.lookup_serie_iamddb(tmdb_id)
        return serie

    def in_database_iamddb(self, tmdb_id: str) -> bool:
        """ Returns True if all episodes of series are stored in iamddb database """
        serie = SerieDB.query.filter_by(tmdb_id=tmdb_id).all()

        if serie == []:
            return False

        return True

    def add_database_iamddb(self, tmdb_id: str) -> bool:
        """ Adds all relevant details from serie to iamddb database """
        details = self.lookup_serie_tmdb(tmdb_id)

        serie_title = details["name"]
        spoken_languages = details["spoken_languages"][0]["english_name"]
        poster_path = details["poster_path"]
        first_air_date = details["first_air_date"]
        last_air_date = details["last_air_date"]
        tagline = details["tagline"]
        seasons_amt = details["number_of_seasons"]
        media_type = "serie"

#        details["seasons"]
        if details["videos"] is True:
            video_key = details["videos"]["results"][0]["key"]
            video_site = details["videos"]["results"][0]["site"]

            # add serie object
            serie = SerieDB(tmdb_id=tmdb_id,
                            title=serie_title,
                            tagline=tagline,
                            poster_path=poster_path,
                            last_air_date=last_air_date,
                            first_air_date=first_air_date,
                            spoken_languages=spoken_languages,
                            video_key=video_key,
                            video_site=video_site,
                            seasons_amt=seasons_amt,
                            media_type=media_type)

        else:
            # add serie object
            serie = SerieDB(tmdb_id=tmdb_id,
                            title=serie_title,
                            tagline=tagline,
                            poster_path=poster_path,
                            last_air_date=last_air_date,
                            first_air_date=first_air_date,
                            spoken_languages=spoken_languages,
                            seasons_amt=seasons_amt,
                            media_type=media_type)

        for season in details["seasons"]:
            season_title = season["name"]
            episodes_amt = season["episode_count"]
            season_nr = season["season_number"]
            air_date = season["air_date"]

        season = SeasonDB(tmdb_id=tmdb_id,
                          title=season_title,
                          serie_title=serie_title,
                          episodes_amt=episodes_amt,
                          season_nr=season_nr,
                          air_date=air_date,
                          poster_path=poster_path)

        db.session.add(season)

        genres = details["genres"]
        # add each genre object
        for item in genres:
            genre = GenreDB(tmdb_id=tmdb_id, name=item["name"])
            db.session.add(genre)

        db.session.add(serie)
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

