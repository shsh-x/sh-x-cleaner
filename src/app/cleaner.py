import json
import os
import re
import shutil
from pathlib import Path
from typing import Callable, TypedDict

from ..exceptions import CleanError, OSUParsingError
from .osu_parser import OSUFilesFolder, OSUGameModes, OSUParser


class CleanerParams(TypedDict):
    user_images: dict[str, str] | None
    delete_images: bool
    delete_modes: list[OSUGameModes]


class _FolderCleaner:
    folder_path: Path
    params: CleanerParams

    of_folder: OSUFilesFolder

    def __init__(self, folder_path: Path, params: CleanerParams):
        self.folder_path = folder_path
        self.params = params

    def clean(self):
        """Очистка папки с OSU файлами"""

        self.of_folder = OSUParser.parse_folder(
            self.folder_path, self.params['delete_modes']
        )

        # Если в папке нет osu файлов - удаляем
        if not self.of_folder.osu_files:
            shutil.rmtree(self.folder_path)
            return

        self.__delete_trash()
        # Удаляем папку, если были удалены все .osu
        if not [f for f in os.listdir(self.folder_path) if f.endswith(".osu")]:
            shutil.rmtree(self.folder_path)
            return

        self.__replace_images()

    def __delete_trash(self):
        """Удаление мусора (ненужных файлов)"""
        for file in os.listdir(self.folder_path):
            try:
                file_path = Path(self.folder_path, file)
                filename = file_path.name.lower()

                # Пропускаем, если файл в известных osu файлах
                if filename in self.of_folder.osu_filenames:
                    continue
                # Пропускаем, если файл в известных аудио файлах
                if filename in self.of_folder.audio_filenames:
                    continue
                # Пропускаем, если файл в известных изображениях файлах
                # И не стоит параметра на удаление изображений
                if (
                    not self.params['delete_images']
                    and filename in self.of_folder.image_filenames
                ):
                    continue

                # Удаляем
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                raise CleanError(e, self.folder_path, file)

    def __replace_images(self):
        """Замена изображений на пользовательские"""
        # Если не заданы пользовательские img - выходим
        user_imgs = self.params['user_images']
        if not user_imgs:
            return

        for img_file in self.of_folder.image_filenames:
            try:
                img_file_path = Path(self.folder_path, img_file)

                # Пропускаем если нет такого расширения в пользовательских img
                img_type = img_file_path.suffix
                if img_type not in user_imgs:
                    continue

                img_file_dir = img_file_path.parent
                # Если по какой-то причине папки изображения нет, то создаём
                if not img_file_dir.exists():
                    os.makedirs(img_file_dir)
                # Копируем пользовательское изображение, заменяя текущее
                shutil.copy(user_imgs[img_type], img_file_path)
            except Exception as e:
                raise CleanError(e, self.folder_path, img_file)


class Cleaner:
    proc_folders_json_path: Path
    processed_folders: list[int]

    songs_folder: Path
    params: CleanerParams
    progress_step: Callable[[int], None]

    def __init__(
        self,
        songs_folder: Path,
        params: CleanerParams,
        progress_step: Callable[[int], None]
    ):
        self.songs_folder = songs_folder
        self.params = params
        self.progress_step = progress_step

        # Подгружаем обработанные карты из json
        self.proc_folders_json_path = Path(
            songs_folder,
            "processed_folders.json"
        )
        self.processed_folders = self.__load_proc_folders()

    def __load_proc_folders(self) -> list[int]:
        """Загружает уже обработанные карты из json файла"""
        if not self.proc_folders_json_path.exists():
            return []

        with open(self.proc_folders_json_path, 'r') as json_file:
            return json.load(json_file)

    def __dump_proc_folders(self):
        """Сохраняет уже обработанные карты в json файл"""
        with open(self.proc_folders_json_path, 'w') as json_file:
            json.dump(self.processed_folders, json_file)

    def start_clean(self, folders: list[Path]):
        """Запускает очистку карт OSU"""
        folders_ids = self._map_folders_ids(folders)

        for index, folder in enumerate(folders):
            try:
                folder_id = folders_ids.get(folder)
                # Пропускаем папку, если не удалось получить id карты
                if folder_id is None:
                    # Выполняем коллбек на увеличение прогресса выполнения
                    # Передаём -1 в качестве id карты
                    self.progress_step(-1)
                    continue

                # Выполняем коллбек на увеличение прогресса выполнения
                self.progress_step(folder_id)

                # Если этот id карты уже обработан
                if folder_id in self.processed_folders:
                    # Если этот id - дубликат, то удаляем папку
                    if self._is_id_duplicate(folders_ids, folder_id):
                        shutil.rmtree(folder)
                        del folders_ids[folder]
                    # Пропускаем папку
                    continue

                # Запускаем очистку папки карты
                _FolderCleaner(folder, self.params).clean()
                if folder.exists():
                    self.processed_folders.append(folder_id)

                # Выполняем дамп обработанных карт каждые 100 итераций
                if (index + 1) % 100 == 0:
                    self.__dump_proc_folders()
            except (CleanError, OSUParsingError) as e:
                raise e
            except Exception as e:
                raise CleanError(e, folder)

        self.__dump_proc_folders()

    def _map_folders_ids(self, folders: list[Path]) -> dict[Path, int]:
        result: dict[Path, int] = {}
        for folder in folders:
            result[folder] = self._get_folder_id(folder)
        return result

    def _get_folder_id(self, folder: Path) -> int:
        """Получает ID карты из её названия"""
        folder_id_match = re.match(r'^(\d+)', folder.name)
        if not folder_id_match:
            return -1
        return int(folder_id_match.group(1))

    def _is_id_duplicate(
        self, folders_ids: dict[Path, int], folder_id: int
    ) -> bool:
        id_count = sum(1 for id in folders_ids.values() if id == folder_id)
        return id_count > 1
