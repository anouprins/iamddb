"""
Serie model to manipulate "series" table in IAMDDB database

Serie data is retrieved by connecting to free TMDB database with personal API key, if movie data not yet in IAMDDB database.
The relevant data is then added to IAMDDB database for future use.
Source -- https://developer.themoviedb.org/docs
"""

import requests
from typing import Union

from ..db.models import db
from ..db.models import Serie as SerieDB
from ..db.models import Season as SeasonDB
from .watched import Watched
from .to_watch import Watchlist


class Serie():
    """ class Serie to manipulate "series" table in database """
    def lookup_serie_tmdb(self, tmdb_id: str) -> Union[dict, None]:
        """ Returns all serie information in json using TMDB api
        Parameters
        tmdb_id -- tmdb id

        Returns
        None -- returns none if tmdb_id invalid
        data -- dictionary of serie data retrieved"""
        # query serie details
        response = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}?api_key=669cfa65918d52531e6700a94982ea26&append_to_response=videos,images, aggregate_credits")

        # save details in json format
        data = response.json()

        # success
        if self.successful_tmdb(data):
            return data

        # unsuccessful
        raise Exception("tmdb_invalid")

    def lookup_serie_iamddb(self, tmdb_id: str) -> Union[dict, None]:
        """ Returns all movie information from IAMDDB database table "series" 
        Parameters
        tmdb_id -- tmdb id
        
        Returns
        None -- returns none if tmdb_id invalid
        data -- dictionary of serie data retrieved"""
        # query serie details
        serie = SerieDB.query.filter_by(tmdb_id=tmdb_id).all()
        return serie

    def lookup_season_tmdb(self, tmdb_id: str, season_nr: int) -> Union[dict, None]:
        """ Returns all season information in json using TMDB Api
        tmdb_id -- tmdb id
        season_nr -- season number

        Returns
        data -- dictionary of serie details """
        # query serie details
        response = requests.get(f"https://api.themoviedb.org/3/tv/{tmdb_id}/season/{season_nr}?api_key=669cfa65918d52531e6700a94982ea26&append_to_response=videos,images, aggregate_credits")

        # save serie details in dictionary
        data = response.json()

        # successful
        if self.successful_tmdb(data):
            return data

        # unsuccessful
        return None

    def successful_tmdb(self, data: dict) -> bool:
        """ Returns True if details query is successful, False otherwise
        Parameters
        data -- dictionary of retrieved query data

        Returns
        bool -- True if successful, False otherwise"""

        # unsuccessful 
        try:
            if data["success"] == False:
                return False

        # successful
        except Exception:
            return True

    def check_and_retrieve_database(self, tmdb_id: str) -> None:
        """ Adds relevant serie info to iamddb database if not yet in database
        Parameters
        tmdb_id -- tmdb id
        """
        # add serie to database if not yet there
        if not self.in_database_iamddb(tmdb_id):
            self.add_database_iamddb(tmdb_id)

        # return serie object
        serie = self.lookup_serie_iamddb(tmdb_id)
        return serie

    def in_database_iamddb(self, tmdb_id: str) -> bool:
        """ Returns True if all episodes of series are stored in iamddb database
        Parameters
        tmdb_id -- tmdb id

        Returns
        bool -- True if serie in database, False otherwise"""

        # extract serie data from database
        serie = SerieDB.query.filter_by(tmdb_id=tmdb_id).all()

        # unsuccessful
        if serie == []:
            return False

        # successful
        return True

    def add_database_iamddb(self, tmdb_id: str) -> bool:
        """ Adds all relevant details from serie to IAMDDB database
        Parameters
        tmdb_id -- tmdb id

        Returns
        bool -- True if serie in database, False otherwise"""

        # extract serie details
        details = self.lookup_serie_tmdb(tmdb_id)

        # if spoken languages is present, extract it
        try:
            spoken_languages = details["spoken_languages"][0]["english_name"]

        # if not, make spoken languages empty
        except Exception:
            spoken_languages = ""

        # extract serie details
        serie_title = details["name"]
        poster_path = details["poster_path"]
        first_air_date = details["first_air_date"]
        last_air_date = details["last_air_date"]
        tagline = details["tagline"]
        seasons_amt = details["number_of_seasons"]
        media_type = "serie"

        # extract video if available
        if details["videos"] is True:
            video_key = details["videos"]["results"][0]["key"]
            video_site = details["videos"]["results"][0]["site"]

            # create serie object with video
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
            # create serie object without video
            serie = SerieDB(tmdb_id=tmdb_id,
                            title=serie_title,
                            tagline=tagline,
                            poster_path=poster_path,
                            last_air_date=last_air_date,
                            first_air_date=first_air_date,
                            spoken_languages=spoken_languages,
                            seasons_amt=seasons_amt,
                            media_type=media_type)

        # create season object if season details available
        if details["seasons"] != []:

            # iterate over season details
            for season in details["seasons"]:

                # extract season values
                season_title = season["name"]
                episodes_amt = season["episode_count"]
                season_nr = season["season_number"]
                air_date = season["air_date"]

                # create season object
                season = SeasonDB(tmdb_id=tmdb_id,
                                  title=season_title,
                                  serie_title=serie_title,
                                  episodes_amt=episodes_amt,
                                  season_nr=season_nr,
                                  air_date=air_date,
                                  poster_path=poster_path)

            # add season object to commit
            db.session.add(season)

        # add serie object and commit
        db.session.add(serie)
        db.session.commit()

    def in_list(self, list_title: str, user_id: int, tmdb_id: str) -> bool:
        """ Returns True if serie in list object, False otherwise
        Parameters
        list_title -- list title
        user_id -- user id
        tmdb_id -- tmdb id

        Returns
        bool -- True if item in given list, False otherwise
        """

        # watchlist
        if list_title == "watchlist":

            # see if serie in watchlist
            list_obj = Watchlist()
            return list_obj.connection_exists(tmdb_id, user_id)

        # watched list
        elif list_title == "watched":

            # see if serie in watched list
            list_obj = Watched()
            return list_obj.connection_exists(tmdb_id, user_id)

        # list
        else:

            # see if serie in list
            list_obj = List()
            return list_obj.item_exists(tmdb_id, user_id, list_title)
