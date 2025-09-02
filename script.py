import string
import random
import subprocess
import os

def rar_compress_with_profile(input_file, profile="HDC", winrar_path=r"C:\Program Files\WinRAR\WinRAR.exe"):

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
    total_gb = round(adjusted_size_mb / 1024, 1)
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
    txt_content = generate_template(first_line, password)

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


# Example usage
if __name__ == "__main__":
    input_mkv = r"C:\Users\cukam\Downloads\Day of Reckoning 2025.mkv"

    rar_compress_with_profile(input_mkv)
