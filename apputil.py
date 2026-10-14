"""
A client for the Genius API.

As a module, this file only defines the `Genius` class and has no side
effects on import:

    from apputil import Genius

As a script, it loads ACCESS_TOKEN from the `.env` file and prints artist
information for a few example search terms:

    python apputil.py
"""

import os

import requests
import pandas as pd
from dotenv import load_dotenv


class Genius:
    """
    A small client for the Genius API.

    Parameters
    ----------
    access_token : str
        Genius API client access token.
    """

    BASE_URL = "https://api.genius.com"

    def __init__(self, access_token):
        self.access_token = access_token

    def _headers(self):
        """Return the authorization header for API requests."""
        return {"Authorization": "Bearer " + self.access_token}

    def _get(self, path, params=None):
        """
        Make a GET request to the Genius API and return the 'response' part
        of the JSON payload.
        """
        response = requests.get(self.BASE_URL + path,
                                headers=self._headers(),
                                params=params,
                                timeout=10)
        response.raise_for_status()
        return response.json()["response"]

    def search(self, search_term, per_page=15):
        """Return the list of search hits for `search_term`."""
        params = {"q": search_term, "per_page": per_page}
        return self._get("/search", params=params)["hits"]

    def get_artist_id(self, search_term):
        """
        Return the primary artist ID from the first hit of `search_term`,
        or None if the search returned no hits.
        """
        hits = self.search(search_term, per_page=1)
        if not hits:
            return None
        return hits[0]["result"]["primary_artist"]["id"]

    def get_artist_by_id(self, artist_id):
        """Return the full API JSON for the artist with `artist_id`."""
        return self._get(f"/artists/{artist_id}")

    def get_artist(self, search_term):
        """
        Return a dictionary of artist information for the (most likely)
        primary artist of the first hit for `search_term`.
        """
        artist_id = self.get_artist_id(search_term)
        if artist_id is None:
            return {}
        return self.get_artist_by_id(artist_id)

    @staticmethod
    def _artist_row(search_term, artist_json):
        """Flatten the artist JSON into a single row for a DataFrame."""
        artist = artist_json.get("artist", {})
        return {
            "search_term": search_term,
            "artist_name": artist.get("name"),
            "artist_id": artist.get("id"),
            "followers_count": artist.get("followers_count"),
        }

    def get_artists(self, search_terms):
        """
        Return a DataFrame with one row per search term, containing the
        search term, artist name, artist ID, and followers count.
        """
        rows = [self._artist_row(term, self.get_artist(term))
                for term in search_terms]
        return pd.DataFrame(rows, columns=["search_term", "artist_name",
                                           "artist_id", "followers_count"])


def main():
    """Run a demo of the Genius client using the token in `.env`."""
    load_dotenv()
    genius = Genius(access_token=os.environ["ACCESS_TOKEN"])
    print(genius.get_artists(["Rihanna", "Tycho", "Seal", "U2"]))


if __name__ == "__main__":
    main()
