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
    """
    A worker class responsible for cleaning a single beatmap folder.
    It is instantiated for each folder that needs to be processed.
    """
    folder_path: Path
    params: CleanerParams
    of_folder: OSUFilesFolder

    def __init__(self, folder_path: Path, params: CleanerParams):
        self.folder_path = folder_path
        self.params = params

    def clean(self):
        """
        Executes the full cleaning process for the folder.
        1. Parses the folder to identify all relevant files.
        2. Deletes all junk files based on user settings.
        3. Replaces background images if requested.
        4. Deletes the folder if it becomes empty.
        """
        self.of_folder = OSUParser.parse_folder(
            self.folder_path, self.params['delete_modes']
        )

        # If parsing found no difficulties to keep, the entire folder is junk.
        if not self.of_folder.osu_files:
            shutil.rmtree(self.folder_path)
            return

        self.__delete_trash()
        self.__cleanup_empty_dirs()

        # If, after cleaning, no .osu files remain, the folder is now empty.
        if not list(self.folder_path.glob("*.osu")):
            shutil.rmtree(self.folder_path)
            return

        self.__replace_images()

    def __delete_trash(self):
        """
        Deletes all non-essential files by recursively walking the folder.

        This method works by first building a set of all files that are required
        (osu files, audio, referenced images/videos). It then walks the entire
        directory tree and removes any file whose relative path is not in this
        "keep set".
        """
        # 1. Build the set of files to keep.
        # The paths are normalized to use forward slashes, matching osu!'s format.
        files_to_keep = {
            p.replace(os.path.sep, '/') for p in self.of_folder.osu_filenames
        }
        files_to_keep.update(
            p.replace(os.path.sep, '/') for p in self.of_folder.audio_filenames
        )

        if self.params.get('keep_videos', False):
            files_to_keep.update(
                p.replace(os.path.sep, '/') for p in self.of_folder.video_filenames
            )

        # Images are only kept if no delete/replace option is active.
        if not self.params['delete_images'] and not self.params.get('user_images'):
            files_to_keep.update(
                p.replace(os.path.sep, '/') for p in self.of_folder.image_filenames
            )

        # 2. Walk the directory and delete files not in the keep set.
        for root, _, files in os.walk(self.folder_path):
            for file in files:
                try:
                    full_path = Path(root, file)
                    relative_path = full_path.relative_to(self.folder_path)
                    
                    # Normalize path to use forward slashes for comparison.
                    normalized_relative_path = str(relative_path).replace(os.path.sep, '/')

                    if normalized_relative_path.lower() not in files_to_keep:
                        full_path.unlink()

                except Exception as e:
                    raise CleanError(e, self.folder_path, file)

    def __cleanup_empty_dirs(self):
        """
        Removes any empty subdirectories that may have been left behind after
        deleting junk files. It walks the tree from the bottom up.
        """
        for root, _, _ in os.walk(self.folder_path, topdown=False):
            # Don't attempt to delete the root folder itself in this loop.
            if Path(root) == self.folder_path:
                continue
            try:
                if not os.listdir(root):
                    os.rmdir(root)
            except OSError as e:
                # This can happen if a file is deleted but the handle is not yet released.
                # It's generally safe to ignore.
                print(f"Could not remove empty directory {root}: {e}")
                continue

    def __replace_images(self):
        """
        Replaces background images with user-provided ones.

        This method is robust: it iterates through each difficulty file (.osu) and
        replaces the specific background referenced within it. This ensures that
        even if the image file is missing, a new one (as a symlink) is created
        with the correct name, and it correctly handles mapsets that use different
        backgrounds for different difficulties.
        """
        user_imgs = self.params.get('user_images')
        if not user_imgs:
            return

        # This set prevents trying to create the same symlink multiple times
        # if different difficulties share the same background file.
        replaced_bgs_in_folder = set()

        for osu_file in self.of_folder.osu_files:
            for bg_filename in osu_file.image_filenames:
                if bg_filename in replaced_bgs_in_folder:
                    continue

                try:
                    img_file_path = self.folder_path.joinpath(bg_filename)
                    img_suffix = img_file_path.suffix.lower()

                    if img_suffix not in user_imgs:
                        continue

                    source_image_path = user_imgs[img_suffix]

                    # Ensure the destination directory exists before creating the symlink.
                    # This is crucial if the original file was in a subfolder that got deleted.
                    img_file_path.parent.mkdir(parents=True, exist_ok=True)

                    # Delete the original file (if it exists) and create a symlink.
                    img_file_path.unlink(missing_ok=True)
                    os.symlink(source_image_path, img_file_path)
                    
                    replaced_bgs_in_folder.add(bg_filename)

                except Exception as e:
                    raise CleanError(e, self.folder_path, bg_filename)


class Cleaner:
    """
    The main orchestrator for the cleaning process. It manages the overall
    workflow, including loading the history of processed maps, iterating through
    folders, and handling high-level logic like duplicates and saving progress.
    """
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

        # Load the list of IDs from previous runs, unless "Force Clean" is enabled.
        self.proc_folders_json_path = self.songs_folder / "processed_folders.json"
        if self.params.get('force_clean', False):
            self.processed_folders = []
        else:
            self.processed_folders = self.__load_proc_folders()

    def _prepare_custom_backgrounds(self):
        """
        If custom backgrounds are used, this method copies them to a central
        `_BACKGROUND-DO-NOT-DELETE` directory. This is crucial for symlinking,
        as symlinks need a single, stable source to point to.
        """
        user_imgs = self.params.get('user_images')
        if not user_imgs:
            return

        backgrounds_storage_path = self.songs_folder / "_BACKGROUND-DO-NOT-DELETE"
        backgrounds_storage_path.mkdir(exist_ok=True)

        new_user_images = {}
        for img_type, img_path in user_imgs.items():
            source_path = Path(img_path)
            dest_path = backgrounds_storage_path / source_path.name
            if not dest_path.exists():
                shutil.copy(source_path, dest_path)
            new_user_images[img_type] = dest_path.resolve()

        self.params["user_images"] = new_user_images

    def __load_proc_folders(self) -> list[int]:
        """Loads a list of already processed beatmap IDs from `processed_folders.json`."""
        if not self.proc_folders_json_path.exists():
            return []
        with open(self.proc_folders_json_path, 'r', encoding='utf-8') as json_file:
            return json.load(json_file)

    def __dump_proc_folders(self):
        """Saves the list of processed beatmap IDs to `processed_folders.json`."""
        with open(self.proc_folders_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(self.processed_folders, json_file, indent=4)

    def _get_folder_id(self, folder: Path) -> int | None | Literal[-1]:
        """
        Determines the status of a folder's beatmap ID from its name.

        This is a critical function for routing logic in the main clean loop.
        
        - Returns:
            - `int`: A valid beatmap ID (e.g., 12345).
            - `None`: If the folder name does not start with a number (e.g., "My Song").
            - `-1`: If the name starts with a number but it's in an invalid format,
                    like being too long (e.g., "123456789 My Song") when the ID limit
                    is active, or not being followed by a space.
        """
        if not folder.name[0].isdigit():
            return None  # This folder has no numeric prefix at all.

        # The regex checks for a number followed by an optional space and any characters.
        # The length of the number depends on the "Ignore ID Limit" setting.
        ignore_limit = self.params.get('ignore_id_limit', False)
        regex = r'^(\d+)(?:\s.*)?$' if ignore_limit else r'^(\d{1,8})(?:\s.*)?$'
        
        match = re.match(regex, folder.name)
        if match:
            return int(match.group(1))
        
        # The name starts with a digit but doesn't match the required format.
        return -1

    def start_clean(self, folders: list[Path]):
        """
        Starts the main cleaning loop for all folders found in the Songs directory.
        """
        # This set tracks IDs that are processed *in this specific run*.
        # It's essential for handling duplicates found in the same batch,
        # distinguishing them from duplicates from a *previous* run.
        processed_in_this_run = set()

        for index, folder in enumerate(folders):
            try:
                folder_id = self._get_folder_id(folder)
                self.progress_step(folder_id if folder_id is not None else -1)

                # Case 1: Invalid ID format (e.g., too long). Always skip.
                if folder_id == -1:
                    continue

                # Case 2: No numeric ID prefix. Clean only if "dangerous" mode is on.
                if folder_id is None:
                    if self.params.get('dangerous_clean_no_id', False):
                        _FolderCleaner(folder, self.params).clean()
                    continue # Otherwise, skip.

                # Case 3: Valid ID. Now we handle duplicate and processed logic.

                # If we've already handled this ID in this session, this is a duplicate. Delete it.
                if folder_id in processed_in_this_run:
                    shutil.rmtree(folder)
                    continue

                # If this ID was handled in a *previous* session (and we're not forcing a re-clean),
                # we should skip it. We also add it to the current session's set to ensure
                # any subsequent duplicates in *this* batch are correctly deleted.
                if folder_id in self.processed_folders:
                    processed_in_this_run.add(folder_id)
                    continue

                # If we've reached here, it's a new, valid map. Clean it.
                _FolderCleaner(folder, self.params).clean()
                
                # After cleaning, record the ID as processed for this run and for future runs.
                if folder.exists():
                    self.processed_folders.append(folder_id)
                    processed_in_this_run.add(folder_id)

                # Save progress to the JSON file every 100 folders.
                if (index + 1) % 100 == 0:
                    self.__dump_proc_folders()

            except (CleanError, OSUParsingError) as e:
                raise e
            except Exception as e:
                raise CleanError(e, folder)

        # Final save of all processed IDs at the end of the run.
        self.__dump_proc_folders()
