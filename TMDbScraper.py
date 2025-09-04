import requests
from bs4 import BeautifulSoup
import re

class TMDbScraper:
    def __init__(self, movie: str):
        # Remove year at the end if present
        self.movie = re.sub(r"\s\d{4}$", "", movie).strip()
        self.film_url = None
        self.tmdb_search()

    def tmdb_search(self):
        search_url = f"https://www.themoviedb.org/search?query={self.movie}"
        headers = {"User-Agent": "Mozilla/5.0"}

        # Fetch search page
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find the first movie link
        first_link = soup.select_one("div.search_results.movie a[data-id]")
        if first_link:
            self.film_url = "https://www.themoviedb.org" + first_link["href"]
            print(f"✅ First movie found: {first_link.text.strip()} -> {self.film_url}")
        else:
            print("❌ No movie found")

    def get_film_url(self):
        return self.film_url
