import os
import subprocess
import random
import string


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
        # --- Decide number of parts (same thresholds as before) ---
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
        self.num_parts = num_parts

        # --- Byte-accurate math & safe volume size ---
        total_bytes_est = int(round(self.file_size_bytes * 1.05))  # estimate final with 5% recovery
        lower = (total_bytes_est + num_parts - 1) // num_parts  # ceil(total/N)
        if num_parts > 1:
            upper = (total_bytes_est - 1) // (num_parts - 1)  # floor(< total/(N-1))
        else:
            upper = total_bytes_est

        # Safety margin: 64 MiB or 0.5% of estimated-per-part, whichever is bigger
        per_part_est = total_bytes_est / max(1, num_parts)
        safety = max(64 * 1024 * 1024, int(0.005 * per_part_est))

        # Start from lower bound + safety, but clamp below upper bound
        s_bytes = lower + safety
        if num_parts > 1 and s_bytes >= upper:
            s_bytes = max(lower, upper - safety)

        # Final volume size for WinRAR (in bytes, to avoid unit drift)
        self.volume_size_bytes = int(s_bytes)
        self.volume_size_str = None if num_parts == 1 else f"-v{self.volume_size_bytes}b"

        # --- Predict part sizes for display (based on estimate) ---
        if num_parts == 1:
            part_sizes_bytes = [total_bytes_est]
        else:
            full = num_parts - 1
            part_sizes_bytes = [self.volume_size_bytes] * full
            last = max(1, total_bytes_est - self.volume_size_bytes * full)
            part_sizes_bytes.append(last)

        # Build first line (GB, 2 decimals)
        total_gb = round(self.file_size_bytes / (1024 ** 3), 2)
        parts_gb = [round(x / (1024 ** 3), 2) for x in part_sizes_bytes]

        if len(parts_gb) == 1:
            # Single archive
            self.first_line = f"{total_gb} GB | single archive | 5% recovery"
        else:
            main_part = parts_gb[0]
            main_count = len(parts_gb) - 1
            last_part = parts_gb[-1]

            if abs(main_part - last_part) < 0.01:  # all parts roughly equal
                self.first_line = f"{total_gb} GB | {len(parts_gb)}x {main_part} GB | 5% recovery"
            else:
                self.first_line = f"{total_gb} GB | {main_count}x {main_part} GB + 1x {last_part} GB | 5% recovery"

        # --- Archive path & password (unchanged) ---
        random_name = self._generate_random_string(30)
        output_dir = os.path.dirname(self.input_file)
        self.archive_path = os.path.join(output_dir, f"{random_name}.rar")
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
