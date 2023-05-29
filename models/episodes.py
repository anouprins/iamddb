
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

    def exists(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        """ Returns True if episode object exists """
        item = EpisodeDB.query.filter(EpisodeDB.tmdb_id==tmdb_id,
                                      EpisodeDB.season_nr==season_nr,
                                      EpisodeDB.episode_nr==episode_nr,
                                      EpisodeDB.user_id==user_id).all()

        if item == []:
            return False

        return True

    def set_unwatched(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        """ Removes watched episode from database """
        # only remove connection if connection exists
        if self.exists(tmdb_id, season_nr, episode_nr, user_id):
            # query all items from database with matching user_id and tmdb_id
            items = db.session.query(EpisodeDB).filter(
                EpisodeDB.user_id==user_id,
                EpisodeDB.tmdb_id==tmdb_id,
                EpisodeDB.season_nr==season_nr,
                EpisodeDB.episode_nr==episode_nr).all()

            # remove each item with matching connection
            for item in items:
                db.session.delete(item)
            db.session.commit()

    def evaluate_checked_episodes(self, tmdb_id: str, user_id: int, checked_episodes: list) -> None:
        """
        Looks up difference between watched episodes in database and checked episodes, then removes the episodes from database that were unchecked, adds the episodes in database that were not yet there
        """
        watched_episodes = self.lookup_watched_episodes(tmdb_id, user_id)
        watched_episodes_list = []
        for key, value in watched_episodes.items():
            for episode in value:
                watched_episodes_list.append(f"{key}.{episode}")

        episodes_to_delete = [item for item in watched_episodes_list if item not in checked_episodes]
        episodes_to_add = [item for item in checked_episodes if item not in watched_episodes_list]


        for episode in episodes_to_add:
            # extract season_nr and episode_nr from form values
            season_nr = episode[:episode.index('.')]
            episode_nr = episode[episode.index('.')+1:]
            self.set_watched(tmdb_id, season_nr, episode_nr, user_id)

        for episode in episodes_to_delete:
            # extract season_nr and episode_nr from form values
            season_nr = episode[:episode.index('.')]
            episode_nr = episode[episode.index('.')+1:]
            self.set_unwatched(tmdb_id, season_nr, episode_nr, user_id)
            

    def lookup_watched_episodes(self, tmdb_id: str, user_id: int) -> dict:
        """ Returns dict of all episodes for user and tmdb item that are set as watched """
        # find all episodes with from serie watched by user
        episodes = EpisodeDB.query.filter(EpisodeDB.tmdb_id==tmdb_id,
                                          EpisodeDB.user_id==user_id).all()

        # put all episodes in lists, ordered by season dictionaries
        episode_data = self.translate_dict(episodes)

        return episode_data

    def lookup_last_watched(self, tmdb_id: str, user_id: int) -> Union[None, int]:
        """ Returns dictionary of last watched episode for serie """
        # get all watched episodes for user and serie
        watched_episodes = self.lookup_watched_episodes(tmdb_id, user_id)

        # return None if no episodes watched
        if watched_episodes == {}:
            return None

        # extract last season
        ordered_seasons = dict(sorted(watched_episodes.items()))
        last_season = list(ordered_seasons.keys())[-1]

        # extract last episode from season
        episodes = watched_episodes[last_season]
        sorted_episodes = sorted(episodes)
        last_episode = sorted_episodes[-1]

        # return into dict
        episode_data = {"season": last_season, "episode": last_episode, "tmdb_id": tmdb_id}

        return episode_data

    def translate_dict(self, episodes: list) -> dict:

        episode_data = {}

        for episode in episodes:
            season_nr = episode.season_nr
            episode_nr = episode.episode_nr

            # add episode to episode data list
            episode_data = self.add_episode(episode_data, season_nr, episode_nr)

        return episode_data

    def add_episode(self, episode_data: dict, season_nr: int, episode_nr: int) -> dict:
        # update episode list if season already has a list
        if season_nr in episode_data:

            # do not change if episode already in list
            if episode_nr in episode_data[season_nr]:
                return episode_data

            # append episode to episode list
            episode_list = episode_data[season_nr]
            episode_list.append(episode_nr)

            # add updated list to dictionary and return it
            episode_data[season_nr] = episode_list
            return episode_data

        # if no episode is in list, create new dictionary item
        episode_data[season_nr] = [episode_nr]
        return episode_data

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

