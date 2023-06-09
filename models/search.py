"""
Model to make searches for movies and serie data using TMDB database.

Functions
search -- retrieves movie/serie search results
search_movies -- retrieves movie data using TMDB database
search_series -- retrieves serie data using TMDB database

by: Anou Prins
"""
import requests


class Search():
    def search(self, search_type: str, search_value, page_nr: int):
        """ Returns search results for given search value """
        if search_type == "movies":
            return self.search_movies(search_value, page_nr)

        if search_type == "series":
            return self.search_series(search_value, page_nr)
        raise Exception

    def search_movies(self, search_value: str, page_nr: int):
        """ Returns movie search results from tmdb api """

        page_nr = int(page_nr)

        url = f"https://api.themoviedb.org/3/search/movie?query={search_value}&include_adult=false&language=en-US&page={page_nr}"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NjljZmE2NTkxOGQ1MjUzMWU2NzAwYTk0OTgyZWEyNiIsInN1YiI6IjY0NDdjYWI4Mzk3ZGYwMDRlODRjMGEwMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5Q0gxMO8gDbOHNpZ5TJK6nCTBpClmhpqI0IuSCHpEjc"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        return data

    def search_series(self, search_value: str, page_nr: int):
        """ Returns serie search results from tmdb api """
        url = f"https://api.themoviedb.org/3/search/tv?query={search_value}&include_adult=false&language=en-US&page={page_nr}"

        headers = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2NjljZmE2NTkxOGQ1MjUzMWU2NzAwYTk0OTgyZWEyNiIsInN1YiI6IjY0NDdjYWI4Mzk3ZGYwMDRlODRjMGEwMyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.5Q0gxMO8gDbOHNpZ5TJK6nCTBpClmhpqI0IuSCHpEjc"
        }

        response = requests.get(url, headers=headers)
        data = response.json()
        return data
