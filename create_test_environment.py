import os
import shutil
from pathlib import Path

# CONFIG
TEST_ROOT_DIR = Path("test_env")
SONGS_DIR = TEST_ROOT_DIR / "Songs"
OSU_EXE_PATH = TEST_ROOT_DIR / "osu!.exe"

# This template will be used for all .osu files
OSU_FILE_TEMPLATE = """osu file format v14

[General]
AudioFilename: audio.mp3
Mode: {mode}
Author: Test Author
Version: {diff_name}

[Metadata]
Title: {song_title}
Artist: Test Artist
Creator: Test Creator
BeatmapID:{beatmap_id}

[Events]
//Background and Video events
Video,{video_timestamp},"video.mp4"
0,0,"bg.jpg",0,0

[HitObjects]
1,1,1,1,0,0:0:0:0:
"""


def create_beatmap(
    beatmap_id: int | None,
    song_name: str,
    modes: list[tuple[int, str]],
    has_video: bool = True,
    has_storyboard: bool = True,
    has_skin_elements: bool = True,
    encoding: str = "utf-8",
    custom_beatmap_name: str | None = None,
):
    """
    Creates a beatmap folder with specified properties.
    """
    folder_name = f"{beatmap_id} {song_name}" if beatmap_id else song_name
    folder_path = SONGS_DIR / folder_name
    folder_path.mkdir()

    # Create .osu files for each mode
    for mode, diff_name in modes:
        osu_content = OSU_FILE_TEMPLATE.format(
            mode=mode,
            diff_name=diff_name,
            song_title=song_name,
            beatmap_id=beatmap_id if beatmap_id else 0,
            video_timestamp="1000" if has_video else ""
        )
        osu_filename = custom_beatmap_name or f"Test Artist - {song_name} (Test Creator) [{diff_name}].osu"
        with open(folder_path / osu_filename, "w", encoding=encoding, errors="ignore") as f:
            f.write(osu_content)

    # Create dummy files
    (folder_path / "audio.mp3").touch()
    (folder_path / "bg.jpg").touch()
    if has_video:
        (folder_path / "video.mp4").touch()
    if has_storyboard:
        (folder_path / "storyboard.osb").touch()
        (folder_path / "sb_element.png").touch()
    if has_skin_elements:
        (folder_path / "skin-hitcircle.png").touch()
        (folder_path / "skin-slider.wav").touch()

    print(f"Created beatmap: {folder_name}")


def main():
    """
    Generates a complete test environment for sh(x)cleaner.
    """
    print("Creating test environment...")

    # Clean up previous environment
    if TEST_ROOT_DIR.exists():
        print(f"Removing existing '{TEST_ROOT_DIR}' directory...")
        shutil.rmtree(TEST_ROOT_DIR)

    # Create root, Songs dir, and dummy osu!.exe
    TEST_ROOT_DIR.mkdir()
    SONGS_DIR.mkdir()
    OSU_EXE_PATH.touch()
    print(f"Created '{TEST_ROOT_DIR}' and '{SONGS_DIR}'")
    print("-" * 20)

    # --- Test Cases ---

    # 1. Standard map with all junk and modes
    create_beatmap(
        beatmap_id=1001,
        song_name="Standard Full Map",
        modes=[(0, "Osu diff"), (1, "Taiko diff"), (2, "Catch diff"), (3, "Mania diff")],
    )

    # 2. Duplicate of the standard map to test duplicate ID cleaning
    create_beatmap(
        beatmap_id=1001,
        song_name="Standard Full Map DUPLICATE",
        modes=[(0, "Osu diff")],
    )

    # 3. Map with no ID for "dangerous clean" option
    create_beatmap(
        beatmap_id=None,
        song_name="Map Without ID",
        modes=[(0, "Normal")],
        has_video=False,
    )

    # 4. Map with a long ID for "ignore id limit" option
    create_beatmap(
        beatmap_id=1234567890,
        song_name="Long ID Map",
        modes=[(0, "Normal")],
    )

    # 5. Map with Cyrillic encoding (Windows-1251)
    create_beatmap(
        beatmap_id=2002,
        song_name="Кириллица",
        modes=[(0, "Нормальный")],
        encoding="iso-8859-5", # Simulating Windows-1251
        custom_beatmap_name="Тестовый Артист - Кириллица (Тестовый Создатель) [Нормальный].osu"
    )

    # 6. Map with another legacy encoding (Latin-1)
    create_beatmap(
        beatmap_id=3003,
        song_name="Lätin-1 Map with Ümlauts",
        modes=[(0, "Härd")],
        encoding="iso-8859-1",
    )

    # 7. Map with only Taiko and Mania modes to test mode deletion
    create_beatmap(
        beatmap_id=4004,
        song_name="Taiko Mania Only",
        modes=[(1, "Inner Oni"), (3, "4K MX")],
        has_video=False,
        has_storyboard=False,
        has_skin_elements=False,
    )

    # 8. A clean map with no junk to ensure it's skipped
    create_beatmap(
        beatmap_id=5005,
        song_name="A Clean Map",
        modes=[(0, "Insane")],
        has_video=False,
        has_storyboard=False,
        has_skin_elements=False,
    )

    print("-" * 20)
    print("Test environment created successfully!")
    print(f"Run the app and select the '{OSU_EXE_PATH.resolve()}' file.")


if __name__ == "__main__":
    main()
