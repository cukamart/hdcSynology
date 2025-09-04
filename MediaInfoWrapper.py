import subprocess
import os

class MediaInfoWrapper:
    def __init__(self, input_mkv: str, movie: str):
        self.input_mkv = input_mkv
        self.movie = movie
        self.mediainfo_path = r"C:\Program Files\MediaInfo\cli\MediaInfo.exe"
        self.media_info_text = None
        self.media_info_template = None

        self.run_mediainfo()

    def run_mediainfo(self):
        try:
            result = subprocess.run(
                [self.mediainfo_path, "--Output=Text", self.input_mkv],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )

            output_text = result.stdout

            # Replace "Complete name" line
            lines = output_text.splitlines()
            for i, line in enumerate(lines):
                if line.startswith("Complete name"):
                    lines[i] = f"Complete name                            : {self.movie}.mkv"
                    break

            self.media_info_text = "\n".join(lines)

            # Wrap with BBCode template
            self.media_info_template = (
                f"[center][rozklikavaciinfo][color=#ffb140]\n\n"
                f"{self.media_info_text}\n\n"
                f"[/color][/rozklikavaciinfo][/center]"
            )

        except subprocess.CalledProcessError as e:
            print("❌ MediaInfo failed:", e.stderr)
        except FileNotFoundError:
            print("❌ Could not find MediaInfo CLI at:", self.mediainfo_path)

    def get_height(self):
        """Extracts video height from MediaInfo output as int (e.g., 2160)."""
        for line in self.media_info_text.splitlines():
            if line.strip().startswith("Height"):
                # Example: "Height                                   : 2 160 pixels"
                digits = "".join(ch for ch in line if ch.isdigit())
                if digits:
                    return int(digits)
        return None

    def get_resolution_label(self):
        """Returns 2160p if height > 1440, else 1080p"""
        height = self.get_height()
        if height and height > 1440:
            return "2160p"
        return "1080p"

    def get_hdr_tags(self):
        """Return bbcode HDR tags based on MediaInfo analysis (only if 2160p)."""
        if self.get_resolution_label() != "2160p":
            return ""

        hdr_tags = ["[h265][/h265]"]  # always include h265 for 2160p

        for line in self.media_info_text.splitlines():
            if line.strip().startswith("HDR format"):
                hdr_line = line.lower()
                if "dolby vision" in hdr_line:
                    hdr_tags.append("[dolbyvision][/dolbyvision]")
                if "hdr10+" in hdr_line:
                    hdr_tags.append("[hdr10plus][/hdr10plus]")
                elif "hdr10" in hdr_line:
                    hdr_tags.append("[hdr][/hdr]")
                break

        return "".join(hdr_tags)

    def get_media_info_text(self):
        return self.media_info_text

    def get_media_info_template(self):
        return self.media_info_template
