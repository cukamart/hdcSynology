import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

class IMDbScraper:
    def __init__(self, movie: str):
        self.movie = movie
        self.film_url = None
        self.imdb_search()

    def imdb_search(self):
        # Build search URL
        query_encoded = quote_plus(self.movie)
        search_url = f"https://www.imdb.com/find?q={query_encoded}&s=tt"
        headers = {"User-Agent": "Mozilla/5.0"}

        # Fetch search page
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Select the first li inside the search results ul
        first_li = soup.select_one("ul.ipc-metadata-list li")
        if first_li:
            link = first_li.find("a")
            if link and link.get("href"):
                url = "https://www.imdb.com" + link["href"]
                self.film_url = url.split("?")[0]
            else:
                self.film_url = "no film found"
        else:
            self.film_url = "no film found"

    def get_film_url(self):
        return self.film_url
