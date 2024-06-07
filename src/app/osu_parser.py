import os
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# \d+,\d+ на всякий случай, мало ли встретится не 0,0
_IMG_LINE_REGEX = re.compile(r'^\d+,\d+,\"(.+\.(?:jpg|png))\"')
"""Регулярное выражения для строки с изображением"""


class OSUGameModes(Enum):
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3


@dataclass
class OSUFile:
    filename: str
    """Имя файла"""
    audio_filename: str
    """Имя аудио файла"""
    image_filenames: set[str]
    """Имена файлов изображений"""
    mode: OSUGameModes
    """Режим игры"""


@dataclass
class OSUFilesFolder:
    osu_files: list[OSUFile]
    """Объекты файлов osu"""
    osu_filenames: set[str]
    """Имена файлов osu"""
    audio_filenames: set[str]
    """Имена аудио файлов"""
    image_filenames: set[str]
    """Имена файлов изображений"""


class OSUParser:
    @staticmethod
    def parse_file(file_path: Path) -> OSUFile:
        """Парсинг osu-файла."""
        audio_filename: str = ""
        image_filenames: set[str] = set()
        mode: OSUGameModes

        with open(file_path, 'r', encoding='UTF-8') as file:
            for line in file:
                # Пропускаем комментарии
                if line.strip().startswith("//"):
                    continue

                if line.startswith("AudioFilename: "):
                    # Нашли строчку с AudioFilename
                    audio_filename = line.split(": ")[1].strip()
                elif match := re.match(_IMG_LINE_REGEX, line):
                    # Нашли строчку с изображением
                    image_filenames.add(match.group(1))
                elif line.startswith("Mode: "):
                    mode = OSUGameModes(int(line.split(": ")[1].strip()))

        return OSUFile(file_path.name, audio_filename, image_filenames, mode)

    @staticmethod
    def parse_folder(
        folder_path: Path,
        skip_modes: list[OSUGameModes]
    ) -> OSUFilesFolder:
        """Парсинг папки с osu-файлами."""
        osu_files: list[OSUFile] = []
        audio_filenames: set[str] = set()
        image_filenames: set[str] = set()

        for file in os.listdir(folder_path):
            if not file.endswith('.osu'):
                continue

            file_path = Path(folder_path, file)
            osu_file = OSUParser.parse_file(file_path)
            # Пропускаем файл с ненужным режимом
            if osu_file.mode in skip_modes:
                continue
            osu_files.append(osu_file)

            image_filenames.update(osu_file.image_filenames)
            if osu_file.audio_filename:
                audio_filenames.add(osu_file.audio_filename)

        return OSUFilesFolder(
            osu_files,
            set([osu_file.filename for osu_file in osu_files]),
            audio_filenames,
            image_filenames
        )
