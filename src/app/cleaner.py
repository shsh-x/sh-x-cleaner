import json
import os
import re
import shutil
from pathlib import Path
from typing import Callable, Literal

from ..exceptions import CleanError, OSUParsingError
from .osu_parser import OSUFilesFolder, OSUParser
from .types import CleanerParams, OSUGameModes


class _FolderCleaner:
    folder_path: Path
    params: CleanerParams

    of_folder: OSUFilesFolder

    def __init__(self, folder_path: Path, params: CleanerParams):
        self.folder_path = folder_path
        self.params = params

    def clean(self):
        """Cleans a single beatmap folder."""

        self.of_folder = OSUParser.parse_folder(
            self.folder_path, self.params['delete_modes']
        )

        # If there are no .osu files in the folder, delete it.
        if not self.of_folder.osu_files:
            shutil.rmtree(self.folder_path)
            return

        self.__delete_trash()
        # If all .osu files were deleted, delete the folder.
        if not [f for f in os.listdir(self.folder_path) if f.endswith(".osu")]:
            shutil.rmtree(self.folder_path)
            return

        self.__replace_images()

    def __delete_trash(self):
        """Deletes junk files from the beatmap folder."""
        for file in os.listdir(self.folder_path):
            try:
                file_path = Path(self.folder_path, file)
                filename = file_path.name.lower()

                # Skip known .osu files
                if filename in self.of_folder.osu_filenames:
                    continue
                # Skip known audio files
                if filename in self.of_folder.audio_filenames:
                    continue
                # Skip known video files if the user wants to keep them
                if self.params.get('keep_videos', False) and filename in self.of_folder.video_filenames:
                    continue
                # Skip known image files if the user doesn't want to delete them
                if (
                    not self.params['delete_images']
                    and filename in self.of_folder.image_filenames
                ):
                    continue

                # Delete the file/folder
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
            except Exception as e:
                raise CleanError(e, self.folder_path, file)

    def __replace_images(self):
        """
        Replaces background images with user-provided ones by reading each .osu file directly.
        This ensures replacement works even if the original image file is missing.
        """
        user_imgs = self.params.get('user_images')
        if not user_imgs:
            return

        replaced_bgs_in_folder = set()

        # Iterate through each parsed .osu file object
        for osu_file in self.of_folder.osu_files:
            # Iterate through the backgrounds referenced in this specific .osu file
            for bg_filename in osu_file.image_filenames:
                if bg_filename in replaced_bgs_in_folder:
                    continue

                try:
                    img_file_path = self.folder_path.joinpath(bg_filename)
                    img_suffix = img_file_path.suffix.lower()

                    if img_suffix not in user_imgs:
                        continue

                    source_image_path = user_imgs[img_suffix]

                    # Delete the original file (if it exists) and create a symlink
                    img_file_path.unlink(missing_ok=True)
                    os.symlink(source_image_path, img_file_path)
                    
                    replaced_bgs_in_folder.add(bg_filename)

                except Exception as e:
                    raise CleanError(e, self.folder_path, bg_filename)


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

        self._prepare_custom_backgrounds()

        # Load processed beatmaps from json
        self.proc_folders_json_path = Path(
            songs_folder,
            "processed_folders.json"
        )
        if self.params.get('force_clean', False):
            self.processed_folders = []
        else:
            self.processed_folders = self.__load_proc_folders()

    def _prepare_custom_backgrounds(self):
        """Prepares custom background images by copying them to a central directory."""
        user_imgs = self.params.get('user_images')
        if not user_imgs:
            return

        backgrounds_storage_path = self.songs_folder.joinpath("_BACKGROUND-DO-NOT-DELETE")
        backgrounds_storage_path.mkdir(exist_ok=True)

        new_user_images = {}
        for img_type, img_path in user_imgs.items():
            source_path = Path(img_path)
            dest_path = backgrounds_storage_path.joinpath(source_path.name)
            if not dest_path.exists():
                shutil.copy(source_path, dest_path)
            new_user_images[img_type] = dest_path.resolve()

        self.params["user_images"] = new_user_images

    def __load_proc_folders(self) -> list[int]:
        """Loads a list of already processed beatmap IDs from a json file."""
        if not self.proc_folders_json_path.exists():
            return []

        with open(self.proc_folders_json_path, 'r') as json_file:
            return json.load(json_file)

    def __dump_proc_folders(self):
        """Saves the list of processed beatmap IDs to a json file."""
        with open(self.proc_folders_json_path, 'w') as json_file:
            json.dump(self.processed_folders, json_file)

    def _get_folder_id(self, folder: Path) -> int | None | Literal[-1]:
        """
        Gets the beatmap ID from the folder name.
        - Returns the integer ID if valid.
        - Returns None if the folder name does not start with a number and a space.
        - Returns -1 if it starts with a number but it's not a valid ID format (e.g., too long).
        """
        # First, check if the folder name starts with a digit at all.
        if not folder.name[0].isdigit():
            return None  # Truly no ID

        ignore_limit = self.params.get('ignore_id_limit', False)
        regex = r'^(\d+)\s' if ignore_limit else r'^(\d{1,8})\s'
        
        match = re.match(regex, folder.name)
        if match:
            return int(match.group(1))
        
        # It starts with a digit, but didn't match the format (e.g. too long, no space).
        return -1

    def start_clean(self, folders: list[Path]):
        """Starts the cleaning process for all beatmap folders."""
        
        # Keep track of IDs processed in *this run* to handle duplicates within the same run.
        processed_in_this_run = set()

        for index, folder in enumerate(folders):
            try:
                folder_id = self._get_folder_id(folder)

                # Case 1: Invalid ID format (e.g., '123456789 '). Always skip.
                if folder_id == -1:
                    self.progress_step(-1)
                    continue

                # Case 2: No numeric ID prefix (e.g., 'My Song').
                if folder_id is None:
                    if self.params.get('dangerous_clean_no_id', False):
                        self.progress_step(-1)
                        _FolderCleaner(folder, self.params).clean()
                    else:
                        self.progress_step(-1) # Skip
                    continue

                # Case 3: Valid ID found.
                self.progress_step(folder_id)

                # Is this ID a duplicate of one we've already cleaned *in this session*?
                if folder_id in processed_in_this_run:
                    shutil.rmtree(folder)
                    continue

                # Is this ID from a previous session (and not being force-cleaned)?
                if folder_id in self.processed_folders:
                    # Mark as "seen" for this run to handle duplicates, then skip.
                    processed_in_this_run.add(folder_id)
                    continue

                # First time seeing this ID. Clean it and record it.
                _FolderCleaner(folder, self.params).clean()
                if folder.exists():
                    self.processed_folders.append(folder_id)
                    processed_in_this_run.add(folder_id)

                # Dump progress periodically
                if (index + 1) % 100 == 0:
                    self.__dump_proc_folders()

            except (CleanError, OSUParsingError) as e:
                raise e
            except Exception as e:
                raise CleanError(e, folder)

        self.__dump_proc_folders()
