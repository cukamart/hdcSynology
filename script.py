import string
import random
import subprocess
import os
import requests
from bs4 import BeautifulSoup

def rar_compress_with_profile(input_file, movie, profile="HDC", winrar_path=r"C:\Program Files\WinRAR\WinRAR.exe"):

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    file_size_bytes = os.path.getsize(input_file)
    file_size_mb = file_size_bytes / (1024 * 1024)
    print(f"Compressing file: {input_file} ({file_size_mb:.2f} MB)")

    adjusted_size_mb = file_size_mb * 1.05  # HDC adds 5% recovery

    # Determine volume size
    if adjusted_size_mb < 5000:
        num_parts = 1
    elif 5000 <= adjusted_size_mb < 8000:
        num_parts = 2
    elif 8000 <= adjusted_size_mb < 15000:
        num_parts = 3
    elif 15000 <= adjusted_size_mb < 30000:
        num_parts = 4
    else:
        num_parts = 5

    volume_size_mb = adjusted_size_mb / num_parts + 5

    # Build list of part sizes
    part_sizes_mb = [int(round(volume_size_mb))] * (num_parts - 1)
    last_part_size_mb = int(round(adjusted_size_mb - sum(part_sizes_mb)))
    part_sizes_mb.append(last_part_size_mb)

    # Build first line string
    total_gb = round(file_size_mb / 1024, 1)
    if num_parts == 1:
        first_line = f"{total_gb} GB | single archive | 5% recovery"
    else:
        first_line = f"{total_gb} GB | {num_parts}× {int(volume_size_mb)} MB | 5% recovery"

    # Determine WinRAR volume string
    volume_size_str = None if adjusted_size_mb < 5000 else f"-v{int(volume_size_mb)}m"

    output_dir = os.path.dirname(input_file)

    # Archive name
    random_name = generate_random_string(30)
    archive_name = f"{random_name}.rar"
    archive_path = os.path.join(output_dir, archive_name)

    password = generate_password(30)

    # Use WinRAR with profile
    cmd = [
        winrar_path,
        "a",                # add to archive
        "-ep1",             # exclude base folder
        f"-prf{profile}",   # use saved profile
        f"-p{password}",
        archive_path,
        input_file
    ]

    if volume_size_str:
        cmd.append(volume_size_str)

    # cmd.extend([archive_path, input_file])  # add archive path and input file

    print("Running command:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    # Build .txt content
    txt_content = """[center][color=#4baddc][size=180][b]Mummies / Mumie / 1080p / DD+ 5.1 EN,CZ / 2023[/b][/size][/color][/center]



[center][color=#FFFFFF][size=120]Release:[/size][/color] [color=#747474][size=120]Mummies.2023.1080p.WEB-DL.DD+5.1.H.264-CMRG[/size][/color]
[color=#FFFFFF][size=120]Původ CZ  stopy:[/size][/color] [color=#74d4d3][size=120]VOD[/size][/color] 
[color=#FFFFFF][size=120]Nástroje:[/size][/color] [color=#747474][size=120]WinRAR 7.13, MediaInfo 25.07, FFmpeg, SubtitleEdit, MKvToolNix 93.00[/size][/color][center]


[center][img]https://i.ibb.co/QF8Gj9Lp/bnsdp-PZton-Wd-O3-AUh-Rl-Ans9u-UYn.jpg[/img][/center]

[center][csfd]https://www.csfd.cz/film/1250762-mumie/[/csfd]   [imdb]https://www.imdb.com/title/tt23177868/[/imdb]    [tmdb]https://www.themoviedb.org/movie/816904-momias[/tmdb][/center]
"""
    txt_content += "\n\n"
    txt_content += csfd_search(movie)
    txt_content += "\n\n"
    txt_content += media_info_generate()
    txt_content += "\n\n"
    txt_content += generate_template(first_line, password)

    # Save txt_content to .txt
    password_file = os.path.join(output_dir, os.path.splitext(archive_name)[0] + ".txt")
    with open(password_file, "w", encoding="utf-8") as f:
        f.write(txt_content)

    print(f"✅ Compressed successfully: {archive_path}")
    print(f"🔑 Password saved to: {password_file}")


def generate_template(first_line: str, password) -> str:
    txt_content = f"""[center][download][/download][/center]
[center][color=#ffb140][size=120]{first_line}[/size][/color][/center] 

[center][img]https://imghost.cz/images/2018/07/07/9PifM.png[/img][/center]

[center][hide][code][/code][/hide][/center]

[center][password][/password][/center]
[center][code]{password}[/code][/center]"""
    return txt_content


def generate_password(length):

    letters_and_numbers = string.ascii_letters + string.digits
    symbols = "!@#$%^&*()-_=+[]{};:,.<>?/|"

    # First and last characters cannot be symbols
    first_char = random.choice(letters_and_numbers)
    last_char = random.choice(letters_and_numbers)

    # Middle characters can include symbols
    middle_chars = [random.choice(letters_and_numbers + symbols) for _ in range(length - 2)]

    return first_char + "".join(middle_chars) + last_char

def generate_random_string(length):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def csfd_search(query):
    # build search URL
    search_url = f"https://www.csfd.cz/hledat/?q={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}  # pretend to be browser

    # fetch page
    response = requests.get(search_url, headers=headers)
    response.raise_for_status()

    # parse results
    soup = BeautifulSoup(response.text, "html.parser")

    # find first film link in search results
    first_film_link = soup.select_one("a.film-title-name")
    if not first_film_link:
        print("No film found!")
        exit()

    film_url = "https://www.csfd.cz" + first_film_link["href"]
    film_title = first_film_link.text.strip()

    print(f"✅ First film found: {film_title} -> {film_url}")

    film_response = requests.get(film_url, headers={"User-Agent": "Mozilla/5.0"})
    film_response.raise_for_status()
    film_soup = BeautifulSoup(film_response.text, "html.parser")
    # print(film_soup.prettify())

    # --- Genres ---
    genres_elem = film_soup.select_one("div.genres")
    if genres_elem:
        genres = [a.text.strip() for a in genres_elem.find_all("a")]
    else:
        genres = []

    # --- Origin, year, runtime ---
    origin_elem = film_soup.select_one("div.origin")
    if origin_elem:
        origin_text = " ".join(origin_elem.get_text().split())  # normalize spaces
    else:
        origin_text = ""

    # Example: "USA, 1999, 136 min (Alternativní 131 min)"
    parts = [p.strip() for p in origin_text.split(",")]

    country = parts[0] if len(parts) > 0 else ""
    year = parts[1] if len(parts) > 1 else ""
    runtime = ", ".join(parts[2:]).strip() if len(parts) > 2 else ""

    # --- First 3 actors from "Hrají:" ---
    actors_divs = film_soup.select("div.creators div")
    actors = []
    for div in actors_divs:
        header = div.find("h4")
        if header and "Hrají" in header.text:
            actor_links = div.find_all("a")
            actors = [a.text.strip() for a in actor_links][:3]  # first 3 actors
            break

    rating_elem = film_soup.select_one("div.film-rating-average")
    if rating_elem:
        rating = rating_elem.text.strip()  # "46%" as string
    else:
        rating = "Unknown"

    plot_elem = film_soup.select_one("div.plot-full p")
    if plot_elem:
        # Get the text, strip extra spaces
        plot_text = plot_elem.get_text(separator=" ", strip=True)
    else:
        plot_text = "No plot found"

    # print("Plot:", plot_text)
    #
    # # --- Print results ---
    # print("Genres:", ", ".join(genres))
    # print("Country:", country)
    # print("Year:", year)
    # print("Runtime:", runtime)
    # print("Actors:", ", ".join(actors))
    # print("Rating:", rating)

    # --- Format output ---
    actors_str = ", ".join(actors)
    if len(actors) == 3:
        actors_str += "..."

    formatted_output = f"""
[center][color=#ffb140][size=120]-------------------------ČSFD-------------------------
{", ".join(genres)}
{country}, {year}, {runtime}
{actors_str}
ČSFD rating: [b]{rating}[/b][/color][/center]

[center][color=#ffb140]{plot_text}[/size][/color][/center]

[center][color=#ffb140]---------------------------------------------------------------------[/color][/center]

[center][screen][/screen][/center]

[center][/center]"""

    print(formatted_output)

    if formatted_output:
        print("✅ Found movie:")
    else:
        print("❌ No result found.")

    return formatted_output


def media_info_generate():
    global result
    # Path to MediaInfo cli executable
    mediainfo_path = r"C:\Program Files\MediaInfo\cli\MediaInfo.exe"

    try:
        result = subprocess.run(
            [mediainfo_path, "--Output=Text", input_mkv],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True
        )

        output_text = result.stdout

        # Replace the "Complete name" line with just the filename
        lines = output_text.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("Complete name"):
                lines[i] = f"Complete name                            : {movie}.mkv"
                break

        output_text = "\n".join(lines)

        return f"[center][rozklikavaciinfo][color=#ffb140]\n\n{output_text}\n\n[/color][/rozklikavaciinfo][/center]"


    except subprocess.CalledProcessError as e:
        print("❌ MediaInfo failed:", e.stderr)
    except FileNotFoundError:
        print("❌ Could not find MediaInfo CLI at:", mediainfo_path)




# Example usage
if __name__ == "__main__":
    path = r"C:\Users\cukam\Downloads\\"
    movie = "Ice Road Vengeance"
    # result = csfd_search(movie)

    input_mkv = os.path.join(path, f"{movie}.mkv")
    rar_compress_with_profile(input_mkv, movie)


# pip install requests beautifulsoup4