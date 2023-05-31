"""
Model for table "episodes" in IAMDDB database

Functions
exists -- checks if episode exists in database
set_unwatched -- sets one episode as unwatched, only if it exists (using exists function)
evaluate_checked_episodes -- adds new episodes and deletes unchecked episodes that exist in "episode" table (using set_watched/set_unwatched)
lookup_watched_episodes -- returns all episodes for serie registered in database
lookup_last_watched -- returns last episode for serie registered in database
set_watched -- adds episode to database
add_episode -- adds new episode to episode data dict
translate_dict -- turns list of episode objects into dictionary

by: Anou Prins
"""
from typing import Union


from ..db.models import db
from ..db.models import Episode as EpisodeDB


class Episode():
    def exists(self, tmdb_id: str, season_nr: int, episode_nr: int, user_id: int) -> None:
        """ Returns True if episode object exists, False otherwise
        Paramaters
        tmdb_id -- tmdb id
        season_nr -- season number
        episode_nr -- episode number
        user_id -- user id """
        # search for episode in database
        item = EpisodeDB.query.filter(EpisodeDB.tmdb_id==tmdb_id,
                                      EpisodeDB.season_nr==season_nr,
                                      EpisodeDB.episode_nr==episode_nr,
                                      EpisodeDB.user_id==user_id).all()

        # episode does not exist
        if item == []:
            return False

        # episode exists
        return True

    def set_unwatched(self, tmdb_id: str, episode_str: str, user_id: int) -> None:
        """ Removes watched episode from database
        Paramaters
        tmdb_id -- tmdb id
        season_nr -- season number
        episode_nr -- episode number
        user_id -- user id """

        # extract season_nr and episode_nr from form values
        season_nr = episode_str[:episode_str.index('.')]
        episode_nr = episode_str[episode_str.index('.')+1:]

        # only remove episode if episode exists
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

            # commit to database
            db.session.commit()

    def evaluate_checked_episodes(self, tmdb_id: str, user_id: int, checked_episodes: list) -> None:
        """
        Looks up difference between watched episodes in database and checked episodes, 
        then removes the episodes from database that were unchecked, 
        adds the episodes in database that were not yet there.

        Paramaters
        tmdb_id -- tmdb id
        user_id -- user id
        checked_episodes -- list of episodes checked, episodes are presented as [season].[episode] """

        # get users watched episodes
        watched_episodes = self.lookup_watched_episodes(tmdb_id, user_id)

        watched_episodes_list = []

        # iterate over seasons
        for key, value in watched_episodes.items():
            # iterate over episodes
            for episode in value:
                # add episode to list
                watched_episodes_list.append(f"{key}.{episode}")

        # determine which to add/delete
        episodes_to_delete = [
            item for item in watched_episodes_list if item not in checked_episodes]
        episodes_to_add = [
            item for item in checked_episodes if item not in watched_episodes_list]

        # add episodes
        for episode in episodes_to_add:
            self.set_watched(tmdb_id, episode, user_id)

        # delete episodes
        for episode in episodes_to_delete:
            self.set_unwatched(tmdb_id, episode, user_id)

    def lookup_watched_episodes(self, tmdb_id: str, user_id: int) -> dict:
        """ Returns dict of all episodes for user and tmdb item that are set as watched
        Paramaters
        tmdb_id -- tmdb id
        user_id -- user id

        Returns
        episode_data -- a dictionary of watched episodes, key = season_nr, value = list of episode_nr"""

        # extract watched episodes
        episodes = EpisodeDB.query.filter(EpisodeDB.tmdb_id==tmdb_id,
                                          EpisodeDB.user_id==user_id).all()

        # add watched episodes in lists, ordered by season dictionaries
        episode_data = self.translate_dict(episodes)
        return episode_data

    def lookup_last_watched(self, tmdb_id: str, user_id: int) -> Union[None, dict]:
        """ Returns dictionary of last watched episode for serie
        Paramaters
        tmdb_id -- tmdb id
        user_id -- user id

        Returns
        None -- if no episodes are set as watched, there is no last watched episode to return
        episode_data -- a dictionary with keys: season, episode, tmdb_id"""

        # extract watched episodes
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

        # return episode data into dict
        episode_data = {"season": last_season, "episode": last_episode, "tmdb_id": tmdb_id}

        return episode_data

    def translate_dict(self, episodes: list) -> dict:
        """ Returns a list of episode objects into a dictionary
        Paramaters
        episodes -- list of episodes of class Episode

        Returns
        episode_data -- a dictionary of episode data, keys = season_nr, values = list of episodes"""
        episode_data = {}

        # iterate over episode objects
        for episode in episodes:
            # extract season_nr and episode_nr from episode object
            season_nr = episode.season_nr
            episode_nr = episode.episode_nr

            # add episode to episode data dict
            episode_data = self.add_episode(episode_data, season_nr, episode_nr)

        return episode_data

    def add_episode(self, episode_data: dict, season_nr: int, episode_nr: int) -> dict:
        """ Returns given episode data dict with added episode
        Paramaters
        episode_data -- episode data to which episode will be added
        season_nr -- season number
        episode_nr -- episode number

        Returns
        episode_data -- new episode data dictionary with new episode"""
        # update episode list if season already has a list
        if season_nr in episode_data:

            # do not update if episode already in list
            if episode_nr in episode_data[season_nr]:
                return episode_data

            # append episode to episode list
            episode_list = episode_data[season_nr]
            episode_list.append(episode_nr)

            # add updated list to dictionary and return it
            episode_data[season_nr] = episode_list
            return episode_data

        # if no episode is in list, create new dictionary item and return dict
        episode_data[season_nr] = [episode_nr]
        return episode_data

    def set_watched(self, tmdb_id: str, episode_str: str, user_id: int) -> None:
        """ Adds episode to database
        Paramaters
        tmdb_id -- tmdb id
        season_nr -- season number
        episode_nr -- episode number
        user_id -- user id """

        # extract season_nr and episode_nr from form values
        season_nr = episode_str[:episode_str.index('.')]
        episode_nr = episode_str[episode_str.index('.')+1:]

        # only remove episode if episode exists
        if self.exists(tmdb_id, season_nr, episode_nr, user_id):
            return None

        # make episode object
        watched = EpisodeDB(tmdb_id=tmdb_id,
                            season_nr=season_nr,
                            episode_nr=episode_nr,
                            user_id=user_id,
                            watched=True)

        # add episode object to database
        db.session.add(watched)
        db.session.commit()
