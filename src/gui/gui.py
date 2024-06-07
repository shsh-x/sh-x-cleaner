import os
import tkinter
from enum import Enum
from pathlib import Path
from tkinter import (Button, Checkbutton, Frame, IntVar, Label, OptionMenu,
                     StringVar, Tk, filedialog, messagebox)
from tkinter.ttk import Progressbar

from ..app.cleaner import Cleaner, CleanerParams
from ..app.osu_parser import OSUGameModes
from ..utils import get_resource_path


class BackgroundModes(Enum):
    KEEP = "keep"
    WHITE = "white"
    DELETE = "delete"
    CUSTOM = "custom"


class SHXCleanerApp:
    def start_gui(self):
        self.__init_components()
        self.__center_window(320, 250)
        self.root.mainloop()

    def __init_components(self):
        self.root = Tk()
        self.root.title("sh(x)cleaner")

        # Фреймы
        self.frame = Frame(self.root)
        self.frame.pack(pady=10)
        self.left_frame = Frame(self.frame)
        self.left_frame.pack(side="left", padx=40)
        self.right_frame = Frame(self.frame)
        self.right_frame.pack(side="right", padx=40)

        # Режимы игры
        self.osu_var = IntVar()
        self.taiko_var = IntVar()
        self.catch_var = IntVar()
        self.mania_var = IntVar()
        self.osu_check = Checkbutton(
            self.left_frame, text="Osu!", variable=self.osu_var
        )
        self.taiko_check = Checkbutton(
            self.left_frame, text="Taiko", variable=self.taiko_var
        )
        self.catch_check = Checkbutton(
            self.left_frame, text="Catch", variable=self.catch_var
        )
        self.mania_check = Checkbutton(
            self.left_frame, text="Mania", variable=self.mania_var
        )
        self.osu_check.pack(anchor='w')
        self.taiko_check.pack(anchor='w')
        self.catch_check.pack(anchor='w')
        self.mania_check.pack(anchor='w')

        # Параметры работы с фонами
        self.bgs_var = StringVar(value=BackgroundModes.KEEP.value)
        self.bgs_label = Label(self.right_frame, text="BGs:")
        self.bgs_label.pack(anchor='w')
        self.bgs_menu = OptionMenu(
            self.right_frame,
            self.bgs_var,
            *[mode.value for mode in BackgroundModes]
        )
        self.bgs_menu.pack(anchor='w')

        # Прогресс бар
        self.progress_label = Label(self.root, text="Progress:")
        self.progress_label.pack(pady=10)
        self.progress = Progressbar(self.root, length=300, mode='determinate')
        self.progress.pack(padx=10)

        # D e s t r o y   e v e r y t h i n g
        self.start_button = Button(
            self.root,
            text="Destroy everything",
            command=self.__start_cleaning
        )
        self.start_button.pack(pady=20)

    def __center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def __pick_params(self) -> CleanerParams:
        user_images: dict[str, str] | None = None
        delete_images: bool = False
        delete_modes: list[OSUGameModes] = []

        bgs_option = BackgroundModes(self.bgs_var.get())
        if bgs_option == BackgroundModes.KEEP:
            user_images = None
            delete_images = False
        elif bgs_option == BackgroundModes.WHITE:
            user_images = {
                ".png": get_resource_path("white.png"),
                ".jpg": get_resource_path("white.jpg")
            }
            delete_images = False
        elif bgs_option == BackgroundModes.DELETE:
            user_images = None
            delete_images = True
        elif bgs_option == BackgroundModes.CUSTOM:
            user_images = {}
            delete_images = False

            if png_file := filedialog.askopenfilename(
                title="Select PNG Image",
                filetypes=[("PNG Files", "*.png")]
            ):
                user_images['.png'] = png_file
            if jpg_file := filedialog.askopenfilename(
                    title="Select JPG Image",
                    filetypes=[("JPG Files", "*.jpg")]
            ):
                user_images['.jpg'] = jpg_file

            if not user_images:
                user_images = None

        if self.osu_var.get() == 1:
            delete_modes.append(OSUGameModes.OSU)
        if self.taiko_var.get() == 1:
            delete_modes.append(OSUGameModes.TAIKO)
        if self.catch_var.get() == 1:
            delete_modes.append(OSUGameModes.CATCH)
        if self.mania_var.get() == 1:
            delete_modes.append(OSUGameModes.MANIA)

        return {
            "user_images": user_images,
            "delete_images": delete_images,
            "delete_modes": delete_modes
        }

    def __start_cleaning(self):
        self.root.withdraw()

        songs_folder = filedialog.askdirectory(title="Select Songs Folder")
        if not songs_folder:
            messagebox.showerror("Fatal error", "Why you...")
            self.root.deiconify()
            return

        folders = [
            Path(f) for f in os.listdir(songs_folder)
            if Path(songs_folder, f).is_dir()
        ]
        self.progress["maximum"] = len(folders)
        self.progress["value"] = 0

        self.root.deiconify()
        self.__center_window(320, 250)

        self.start_button.config(state=tkinter.DISABLED)
        cleaner = Cleaner(
            Path(songs_folder),
            self.__pick_params(),
            self.__progress_step
        )

        def on_end():
            messagebox.showinfo(
                "Info",
                "Everything's clean. Check the size of your songs folder lol"
            )
            self.root.withdraw()
            self.root.quit()
        cleaner.start_clean_thread(folders, on_end)

    def __progress_step(self, folder_id: int):
        self.progress.step()
        self.progress_label.config(text=f"Cleaning {folder_id}...")
        self.root.update_idletasks()
