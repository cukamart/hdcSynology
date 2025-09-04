import string
import random
import subprocess
import os
import requests
from bs4 import BeautifulSoup

from CSFDscraper import CSFDscraper
from MediaInfoWrapper import MediaInfoWrapper
from WinrarWrapper import WinRarWrapper

if __name__ == "__main__":
    path = r"C:\Users\cukam\Downloads\\"
    movie = "Carrie 2 Zuřivost"
    input_mkv = os.path.join(path, f"{movie}.mkv")

    csfd = CSFDscraper(movie)
    media_info = MediaInfoWrapper(input_mkv, movie)
    winrar = WinRarWrapper(input_mkv)
    template = winrar.generate_template()

    txt_content = f"""[center][color=#4baddc][size=180][b]Mummies / {movie} / {media_info.get_resolution_label()} / DD+ 5.1 EN,CZ / {csfd.get_year()}[/b][/size][/color][/center]



[center][color=#FFFFFF][size=120]Release:[/size][/color] [color=#747474][size=120]Mummies.2023.1080p.WEB-DL.DD+5.1.H.264-CMRG[/size][/color]
[color=#FFFFFF][size=120]Původ CZ  stopy:[/size][/color] [color=#74d4d3][size=120]VOD[/size][/color] 
[color=#FFFFFF][size=120]Nástroje:[/size][/color] [color=#747474][size=120]WinRAR 7.13, MediaInfo 25.07, FFmpeg, SubtitleEdit, MKVToolNix 93.00[/size][/color]
{media_info.get_hdr_tags()}[center]


[center][img][/img][/center]

[center][csfd]{csfd.get_film_url()}[/csfd]   [imdb][/imdb]    [tmdb][/tmdb][/center]"""
    txt_content += "\n\n\n"
    txt_content += csfd.get_csfd_template()
    txt_content += "\n\n"
    txt_content += media_info.get_media_info_template()
    txt_content += "\n\n"
    txt_content += winrar.generate_template()

    # Derive output paths from wrapper
    output_dir = os.path.dirname(winrar.input_file)
    archive_name = os.path.basename(winrar.get_archive_path())
    password_file = os.path.join(output_dir, os.path.splitext(archive_name)[0] + ".txt")

    # Save to file
    with open(password_file, "w", encoding="utf-8") as f:
        f.write(txt_content)

    # winrar.compress()

# pip install requests beautifulsoup4