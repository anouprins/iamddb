
import requests
from typing import Union

from ..db.models import db
from ..db.models import Genre as GenreDB, People as PeopleDB, Actors as ActorsDB, Director as DirectorDB
from ..db.models import Season as SeasonDB, Serie as SerieDB


class Season():

    def lookup_season_iamddb(self, tmdb_id: str, season_nr: int) -> Union[dict, None]:
        """ Returns all movie information in json using TMDB Api """
        # query serie details
        season = SeasonDB.query.filter(SeasonDB.tmdb_id==tmdb_id, SeasonDB.season_nr==season_nr).all()
        return season

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

    def check_and_retrieve_database(self, tmdb_id: str, season_nr: int) -> None:
        """ Adds relevant serie info to iamddb database if not yet in database """
        # add serie to database if not yet there
        if not self.in_database_iamddb(tmdb_id, season_nr):
            self.add_database_iamddb(tmdb_id, season_nr)

        # return movie object
        season = self.lookup_season_iamddb(tmdb_id, season_nr)
        return season

    def in_database_iamddb(self, tmdb_id: str, season_nr: int) -> bool:
        """ Returns True if all episodes of series are stored in iamddb database """

        season = SeasonDB.query.filter(SeasonDB.tmdb_id==tmdb_id, SeasonDB.season_nr==season_nr).all()

        if season == []:
            return False

        return True

    def serie_in_database_iamddb(self, tmdb_id: str) -> bool:
        """ Returns True if serie in iamddb database"""
        serie = SerieDB.query.filter_by(tmdb_id=tmdb_id).all()

        if serie == []:
            return False

        return True

    def add_database_iamddb(self, tmdb_id: str, season_nr: int) -> bool:
        """ Adds all relevant details from serie to iamddb database """
        details = self.lookup_season_tmdb(tmdb_id, season_nr)

        serie_title = self.lookup_serie_title(tmdb_id)
        title = details["name"]
        poster_path = details["poster_path"]
        air_date = details["air_date"]
        episodes_amt = len(details["episodes"])
        season_nr = details["season_number"]

        if not poster_path:
            # add season object
            season = SeasonDB(tmdb_id=tmdb_id,
                              title=title,
                              serie_title=serie_title,
                              episodes_amt=episodes_amt,
                              poster_path=poster_path,
                              air_date=air_date,
                              season_nr=season_nr)

        # add serie object
        season = SeasonDB(tmdb_id=tmdb_id,
                          title=title,
                          serie_title=serie_title,
                          episodes_amt=episodes_amt,
                          poster_path=poster_path,
                          air_date=air_date,
                          season_nr=season_nr)

        db.session.add(season)
        db.session.commit()
