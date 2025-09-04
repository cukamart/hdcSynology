import os
import subprocess
import random
import string
from collections import Counter


class WinRarWrapper:
    def __init__(self, input_file, profile="HDC", winrar_path=r"C:\Program Files\WinRAR\WinRAR.exe"):
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        self.input_file = input_file
        self.profile = profile
        self.winrar_path = winrar_path

        self.file_size_bytes = os.path.getsize(input_file)
        self.file_size_mb = self.file_size_bytes / (1024 * 1024)
        self.adjusted_size_mb = self.file_size_mb * 1.05  # HDC adds 5% recovery
        self.first_line = None
        self.password = None
        self.volume_size_str = None
        self.archive_path = None

        self.prepare_metadata()

    def prepare_metadata(self):
        """Prepare first line, password, and archive path, without compression"""
        # --- Determine number of parts ---
        if self.adjusted_size_mb < 5000:
            num_parts = 1
        elif 5000 <= self.adjusted_size_mb < 8000:
            num_parts = 2
        elif 8000 <= self.adjusted_size_mb < 15000:
            num_parts = 3
        elif 15000 <= self.adjusted_size_mb < 30000:
            num_parts = 4
        else:
            num_parts = 5

        volume_size_mb = self.adjusted_size_mb / num_parts + 5

        # --- Build list of part sizes ---
        part_sizes_mb = [int(round(volume_size_mb))] * (num_parts - 1)
        last_part_size_mb = int(round(self.adjusted_size_mb - sum(part_sizes_mb)))
        part_sizes_mb.append(last_part_size_mb)

        # --- First line string ---
        total_gb = round(self.file_size_mb / 1024, 1)
        if num_parts == 1:
            self.first_line = f"{total_gb} GB | single archive | 5% recovery"
        else:
            counts = Counter(part_sizes_mb)
            parts_str = " + ".join(f"{count}× {size} MB" for size, count in counts.items())
            self.first_line = f"{total_gb} GB | {parts_str} | 5% recovery"

        # --- Volume size string ---
        self.volume_size_str = None if self.adjusted_size_mb < 5000 else f"-v{int(volume_size_mb)}m"

        # --- Archive path ---
        random_name = self._generate_random_string(30)
        output_dir = os.path.dirname(self.input_file)
        self.archive_path = os.path.join(output_dir, f"{random_name}.rar")

        # --- Generate password ---
        self.password = self._generate_password(30)

    def compress(self):
        """Run WinRAR compression using profile + prepared settings"""
        if not self.archive_path or not self.password:
            raise RuntimeError("Call prepare_metadata() before compress()")

        cmd = [
            self.winrar_path,
            "a",  # add to archive
            "-ep1",  # exclude base folder
            f"-prf{self.profile}",  # use saved profile
            f"-p{self.password}",
            self.archive_path,
            self.input_file
        ]

        if self.volume_size_str:
            cmd.append(self.volume_size_str)

        print("Running command:", " ".join(cmd))
        subprocess.run(cmd, check=True)

        print(f"✅ Compressed successfully: {self.archive_path}")

    def generate_template(self) -> str:
        """Return BBCode template string"""
        if not self.first_line or not self.password:
            raise RuntimeError("Call prepare_metadata() before generating template")

        return f"""[center][download][/download][/center]
[center][color=#ffb140][size=120]{self.first_line}[/size][/color][/center] 

[center][img]https://imghost.cz/images/2018/07/07/9PifM.png[/img][/center]

[center][hide][code][/code][/hide][/center]

[center][password][/password][/center]
[center][code]{self.password}[/code][/center]"""

    # --- Getters ---
    def get_first_line(self):
        return self.first_line

    def get_password(self):
        return self.password

    def get_archive_path(self):
        return self.archive_path

    # --- Helpers ---
    def _generate_password(self, length):
        letters_and_numbers = string.ascii_letters + string.digits
        symbols = "!@#$%^&*()-_=+[]{};:,.<>?/|"

        first_char = random.choice(letters_and_numbers)
        last_char = random.choice(letters_and_numbers)
        middle_chars = [random.choice(letters_and_numbers + symbols) for _ in range(length - 2)]

        return first_char + "".join(middle_chars) + last_char

    def _generate_random_string(self, length):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
