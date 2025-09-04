import requests
from bs4 import BeautifulSoup

class CSFDscraper:
    def __init__(self, query: str):
        self.query = query
        self.csfd_template = None
        self.film_url = None
        self.year = None

        self.csfd_search()

    def csfd_search(self):
        # Build search URL
        search_url = f"https://www.csfd.cz/hledat/?q={self.query.replace(' ', '+')}"
        headers = {"User-Agent": "Mozilla/5.0"}

        # Fetch search page
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find first film link
        first_film_link = soup.select_one("a.film-title-name")
        if not first_film_link:
            print("❌ No film found!")
            return None

        self.film_url = "https://www.csfd.cz" + first_film_link["href"]
        film_title = first_film_link.text.strip()
        print(f"✅ First film found: {film_title} -> {self.film_url}")

        # Fetch film page
        film_response = requests.get(self.film_url, headers=headers)
        film_response.raise_for_status()
        film_soup = BeautifulSoup(film_response.text, "html.parser")

        # --- Genres ---
        genres_elem = film_soup.select_one("div.genres")
        genres = [a.text.strip() for a in genres_elem.find_all("a")] if genres_elem else []

        # --- Origin, year, runtime ---
        origin_elem = film_soup.select_one("div.origin")
        origin_text = " ".join(origin_elem.get_text().split()) if origin_elem else ""
        parts = [p.strip() for p in origin_text.split(",")]
        country = parts[0] if len(parts) > 0 else ""
        self.year = parts[1] if len(parts) > 1 else ""
        runtime = ", ".join(parts[2:]).strip() if len(parts) > 2 else ""

        # --- Actors (first 3) ---
        actors = []
        for div in film_soup.select("div.creators div"):
            header = div.find("h4")
            if header and "Hrají" in header.text:
                actor_links = div.find_all("a")
                actors = [a.text.strip() for a in actor_links][:3]
                break
        actors_str = ", ".join(actors)
        if len(actors) == 3:
            actors_str += "..."

        # --- Rating ---
        rating_elem = film_soup.select_one("div.film-rating-average")
        rating = rating_elem.text.strip() if rating_elem else "Unknown"

        # --- Plot ---
        plot_elem = film_soup.select_one("div.plot-full p")
        plot_text = plot_elem.get_text(separator=" ", strip=True) if plot_elem else "No plot found"

        # --- Format output ---
        self.csfd_template = f"""
[center][color=#ffb140][size=120]-------------------------ČSFD-------------------------
{", ".join(genres)}
{country}, {self.year}, {runtime}
{actors_str}
ČSFD rating: [b]{rating}[/b][/color][/center]

[center][color=#ffb140]{plot_text}[/size][/color][/center]

[center][color=#ffb140]---------------------------------------------------------------------[/color][/center]

[center][screen][/screen][/center]

[center][/center]"""

        return self.csfd_template

    def get_csfd_template(self):
        return self.csfd_template

    def get_film_url(self):
        return self.film_url

    def get_year(self):
        return self.year