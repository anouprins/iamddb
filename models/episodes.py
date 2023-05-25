
import requests
from typing import Union

from ..db.models import db
from ..db.models import Genre as GenreDB, Episode as EpisodeDB, People as PeopleDB, Actors as ActorsDB, Director as DirectorDB


class Episode():
    def add_watched(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> bool:
        """ Sets an episode as watched """
        # make new episode object if not yet in database
        if not self.exists(tmdb_id, season_nr, episode_nr, user_id):
            self.set_watched(tmdb_id, season_nr, episode_nr, user_id)
            return True

        # update episode if it is set as 'unwatched'
        if not self.is_watched(tmdb_id, season_nr, episode_nr, user_id):
            self.update_watched(tmdb_id, season_nr, episode_nr, user_id)
            return True

        # if episode exists and is watched, do nothing
        return True


    def set_watched(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        watched = EpisodeDB(tmdb_id=tmdb_id,
                            season_nr=season_nr,
                            episode_nr=episode_nr,
                            user_id=user_id,
                            watched=True)

        db.session.add(watched)
        db.session.commit()

    def update_watched(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        pass

    def update_unwatched(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        pass

    def is_watched(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        pass

    def exists(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        """ Returns True if episode object exists """
        item = EpisodeDB.query.filter(tmdb_id==tmdb_id,
                                      season_nr==season_nr,
                                      episode_nr==episode_nr,
                                      user_id==user_id).all()

        if item == []:
            return False

        return True
