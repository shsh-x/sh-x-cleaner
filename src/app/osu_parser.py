import os
import re
from dataclasses import dataclass
from pathlib import Path

from ..exceptions import OSUParsingError
from .types import OSUGameModes

# This regex is designed to find background image declarations in the [Events] section.
# Example: 0,0,"bg.jpg",0,0
_IMG_LINE_REGEX = re.compile(r'^\d+,\d+,\"(.+\.(?:jpe?g|png))\"', re.IGNORECASE)

# This regex finds video declarations in the [Events] section.
# Example: Video,1000,"video.mp4"
_VIDEO_LINE_REGEX = re.compile(r'^Video,\d*,.?\"(.+\.(?:avi|mp4|flv))\"', re.IGNORECASE)


@dataclass
class OSUFile:
    """A data class that holds structured information parsed from a single .osu file."""

    filename: str
    """The lowercase name of the .osu file (e.g., "artist - title (creator) [difficulty].osu")."""
    audio_filename: str
    """The lowercase name of the main audio file (e.g., "audio.mp3")."""
    image_filenames: set[str]
    """A set of all lowercase background image filenames referenced in the file."""
    video_filenames: set[str]
    """A set of all lowercase video filenames referenced in the file."""
    mode: OSUGameModes
    """The game mode of this specific difficulty."""


@dataclass
class OSUFilesFolder:
    """A data class that aggregates information from all parsed .osu files within a single beatmap folder."""

    osu_files: list[OSUFile]
    """A list of all the OSUFile objects that were successfully parsed and not skipped."""
    osu_filenames: set[str]
    """A set of all lowercase .osu filenames that were kept."""
    audio_filenames: set[str]
    """A set of all unique lowercase audio filenames from all difficulties."""
    image_filenames: set[str]
    """A set of all unique lowercase image filenames from all difficulties."""
    video_filenames: set[str]
    """A set of all unique lowercase video filenames from all difficulties."""


class OSUParser:
    """A static class that handles parsing of .osu files and folders."""

    # Beatmaps can have a variety of encodings. This list provides a fallback mechanism.
    # It attempts to read files with the most common encodings first.
    possible_encodings = [
        "UTF-8",
        "iso-8859-5",  # Covers Windows-1251 (Cyrillic)
        "iso-8859-1",  # Covers Windows-1252 (Western European)
    ]

    @staticmethod
    def parse_file(file_path: Path, encoding_num: int = 0) -> OSUFile:
        """
        Parses a single .osu file to extract key information.

        If a file cannot be read with one encoding, it recursively tries the next
        one in the `possible_encodings` list. This handles legacy beatmaps saved
        with different character sets.
        """
        audio_filename: str = ""
        image_filenames: set[str] = set()
        video_filenames: set[str] = set()
        mode: OSUGameModes = OSUGameModes.OSU

        try:
            encoding = OSUParser.possible_encodings[encoding_num]
            with open(file_path, 'r', encoding=encoding) as file:
                for line in file:
                    # Performance: strip and check for comments only once.
                    clean_line = line.strip()
                    if not clean_line or clean_line.startswith("//"):
                        continue

                    if line.startswith("AudioFilename: "):
                        audio_filename = line.split(":", 1)[1].strip().lower()
                    elif match := _IMG_LINE_REGEX.match(line):
                        image_filenames.add(match.group(1).lower())
                    elif match := _VIDEO_LINE_REGEX.match(line):
                        video_filenames.add(match.group(1).lower())
                    elif line.startswith("Mode: "):
                        mode = OSUGameModes(int(line.split(":", 1)[1].strip()))
        except UnicodeDecodeError as e:
            # If we haven't exhausted all possible encodings, try the next one.
            if encoding_num < len(OSUParser.possible_encodings) - 1:
                return OSUParser.parse_file(file_path, encoding_num + 1)
            # If all have failed, raise the error.
            raise e
        except Exception as e:
            raise OSUParsingError(e, file_path)

        return OSUFile(
            file_path.name.lower(),
            audio_filename,
            image_filenames,
            video_filenames,
            mode
        )

    @staticmethod
    def parse_folder(
        folder_path: Path,
        skip_modes: list[OSUGameModes]
    ) -> OSUFilesFolder:
        """
        Parses an entire beatmap folder. It iterates through all .osu files,
        parses each one, and aggregates the results into a single `OSUFilesFolder` object.
        
        It filters out difficulties whose game modes are marked for deletion by the user.
        """
        osu_files: list[OSUFile] = []
        audio_filenames: set[str] = set()
        image_filenames: set[str] = set()
        video_filenames: set[str] = set()

        for file in os.listdir(folder_path):
            if not file.lower().endswith('.osu'):
                continue

            file_path = folder_path / file
            osu_file = OSUParser.parse_file(file_path)
            
            # Skip this difficulty if its game mode is in the user's deletion list.
            if osu_file.mode in skip_modes:
                continue
            
            osu_files.append(osu_file)
            image_filenames.update(osu_file.image_filenames)
            video_filenames.update(osu_file.video_filenames)
            if osu_file.audio_filename:
                audio_filenames.add(osu_file.audio_filename)

        return OSUFilesFolder(
            osu_files,
            set(f.filename for f in osu_files),
            audio_filenames,
            image_filenames,
            video_filenames
        )
