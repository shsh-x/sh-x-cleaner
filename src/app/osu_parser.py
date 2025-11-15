import os
import re
from dataclasses import dataclass
from pathlib import Path

from ..exceptions import OSUParsingError
from .types import OSUGameModes

# The \d+,\d+ is a fallback, in case it's not 0,0
_IMG_LINE_REGEX = re.compile(r'^\d+,\d+,\"(.+\.(?:jpe?g|png))\"')
"""Regex for a line with a background image."""
_VIDEO_LINE_REGEX = re.compile(r'^Video,\d*,.?\"(.+\.(?:avi|mp4|flv))\"')


@dataclass
class OSUFile:
    """A class describing an .osu file."""

    filename: str
    """Filename"""
    audio_filename: str
    """Audio filename"""
    image_filenames: set[str]
    """Image filenames"""
    video_filenames: set[str]
    """Video filenames"""
    mode: OSUGameModes
    """Game mode"""


@dataclass
class OSUFilesFolder:
    """A class describing a folder of .osu files."""

    osu_files: list[OSUFile]
    """.osu file objects"""
    osu_filenames: set[str]
    """.osu filenames"""
    audio_filenames: set[str]
    """Audio filenames"""
    image_filenames: set[str]
    """Image filenames"""
    video_filenames: set[str]
    """Video filenames"""


class OSUParser:
    possible_encodings = [
        "UTF-8",
        "iso-8859-5",  # Windows-1251
        "iso-8859-1",  # Windows-1252
    ]

    @staticmethod
    def parse_file(file_path: Path, encoding_num: int = 0) -> OSUFile:
        """Parses an .osu file."""
        audio_filename: str = ""
        image_filenames: set[str] = set()
        video_filenames: set[str] = set()
        mode: OSUGameModes = OSUGameModes.OSU

        try:
            encoding = OSUParser.possible_encodings[encoding_num]
            with open(file_path, 'r', encoding=encoding) as file:
                for line in file:
                    # Skip comments
                    if line.strip().startswith("//"):
                        continue

                    if line.startswith("AudioFilename: "):
                        # Found the AudioFilename line
                        audio_filename = line.split(": ")[1].strip().lower()
                    elif match := re.match(_IMG_LINE_REGEX, line):
                        # Found a line with an image
                        image_filenames.add(match.group(1).lower())
                    elif match := re.match(_VIDEO_LINE_REGEX, line):
                        video_filenames.add(match.group(1).lower())
                    elif line.startswith("Mode: "):
                        mode = OSUGameModes(int(line.split(": ")[1].strip()))
        except UnicodeDecodeError as e:
            if encoding_num >= len(OSUParser.possible_encodings) - 1:
                raise e
            return OSUParser.parse_file(file_path, encoding_num + 1)
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
        """Parses a folder containing .osu files."""
        osu_files: list[OSUFile] = []
        audio_filenames: set[str] = set()
        image_filenames: set[str] = set()
        video_filenames: set[str] = set()

        for file in os.listdir(folder_path):
            if not file.endswith('.osu'):
                continue

            file_path = Path(folder_path, file)
            osu_file = OSUParser.parse_file(file_path)
            # Skip files with unwanted game modes
            if osu_file.mode in skip_modes:
                continue
            osu_files.append(osu_file)

            image_filenames.update(osu_file.image_filenames)
            video_filenames.update(osu_file.video_filenames)
            if osu_file.audio_filename:
                audio_filenames.add(osu_file.audio_filename)

        return OSUFilesFolder(
            osu_files,
            set([osu_file.filename for osu_file in osu_files]),
            audio_filenames,
            image_filenames,
            video_filenames
        )
