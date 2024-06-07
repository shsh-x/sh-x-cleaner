import os
import re
import json
import shutil
from tkinter import Tk, filedialog, messagebox, Button, Label, Checkbutton, IntVar, StringVar, OptionMenu, Frame
from tkinter.ttk import Progressbar

def parse_osu_file(osu_file_path):
    audio_filename = ""
    image_filenames = set()
    mode = 0
    with open(osu_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("AudioFilename: "):
                audio_filename = line.split(": ")[1].strip()
            elif re.match(r'^\d+,\d+,".+\.(jpg|png)"', line):
                match = re.search(r'"(.+)"', line)
                if match:
                    image_filenames.add(match.group(1))
            elif line.startswith("Mode: "):
                mode = int(line.split(": ")[1].strip())
    return audio_filename, image_filenames, mode

def process_folder(folder_path, user_images, processed_folders, delete_images, delete_modes):
    osu_files = [f for f in os.listdir(folder_path) if f.endswith('.osu')]
    audio_files = set()
    image_files = set()
    
    for osu_file in osu_files:
        osu_path = os.path.join(folder_path, osu_file)
        audio, images, mode = parse_osu_file(osu_path)
        if mode in delete_modes:
            os.remove(osu_path)
            continue
        if audio:
            audio_files.add(audio)
        image_files.update(images)
    
    osu_files = [f for f in os.listdir(folder_path) if f.endswith('.osu')]
    if not osu_files:
        shutil.rmtree(folder_path)
        return
    
    for item in os.listdir(folder_path):
        item_path = os.path.join(folder_path, item)
        if item not in osu_files and item not in audio_files and (delete_images or item not in image_files):
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    
    if user_images:
        for img_type, img_path in user_images.items():
            for img_file in image_files:
                if img_file.endswith(img_type):
                    img_file_path = os.path.join(folder_path, img_file)
                    img_file_dir = os.path.dirname(img_file_path)
                    if not os.path.exists(img_file_dir):
                        os.makedirs(img_file_dir)
                    shutil.copy(img_path, img_file_path)
    
    folder_name = os.path.basename(folder_path)
    folder_id_match = re.match(r'^(\d+)', folder_name)
    if folder_id_match:
        folder_id = int(folder_id_match.group(1))
        processed_folders.append(folder_id)

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def start_cleaning():
    root.withdraw()
    
    songs_folder = filedialog.askdirectory(title="Select Songs Folder")
    if not songs_folder:
        messagebox.showerror("Fatal error", "Why you...")
        root.deiconify()
        return
    
    bgs_option = bgs_var.get()

    if bgs_option == "keep":
        user_images = None
        delete_images = False
    elif bgs_option == "white":
        user_images = {'.png': 'white.png', '.jpg': 'white.jpg'}
        delete_images = False
    elif bgs_option == "delete":
        user_images = None
        delete_images = True
    elif bgs_option == "custom":
        user_images = {}
        delete_images = False
        png_file = filedialog.askopenfilename(title="Select PNG Image", filetypes=[("PNG Files", "*.png")])
        if png_file:
            user_images['.png'] = png_file
        jpg_file = filedialog.askopenfilename(title="Select JPG Image", filetypes=[("JPG Files", "*.jpg")])
        if jpg_file:
            user_images['.jpg'] = jpg_file
    
    
    delete_modes = []
    if osu_var.get() == 1:
        delete_modes.append(0)
    if taiko_var.get() == 1:
        delete_modes.append(1)
    if catch_var.get() == 1:
        delete_modes.append(2)
    if mania_var.get() == 1:
        delete_modes.append(3)
    
    json_file_path = os.path.join(songs_folder, "processed_folders.json")
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as json_file:
            processed_folders = json.load(json_file)
    else:
        processed_folders = []
    
    all_folders = [os.path.join(songs_folder, f) for f in os.listdir(songs_folder) if os.path.isdir(os.path.join(songs_folder, f))]
    
    progress['maximum'] = len(all_folders)
    progress['value'] = 0
    root.deiconify()
    center_window(root, 320, 250)
    
    for index, folder in enumerate(all_folders):
        folder_name = os.path.basename(folder)
        folder_id_match = re.match(r'^(\d+)', folder_name)
        if folder_id_match:
            folder_id = int(folder_id_match.group(1))
            if folder_id in processed_folders:
                continue
            process_folder(folder, user_images, processed_folders, delete_images, delete_modes)
            progress.step()
            progress_label.config(text=f"Cleaning {folder_id}...")
            root.update_idletasks()
            if (index + 1) % 100 == 0:
                with open(json_file_path, 'w') as json_file:
                    json.dump(processed_folders, json_file)
    
    with open(json_file_path, 'w') as json_file:
        json.dump(processed_folders, json_file)
    
    messagebox.showinfo("Info", "Everything's clean. Check the size of your songs folder lol")
    root.destroy()

root = Tk()
root.title("sh(x)cleaner")

frame = Frame(root)
frame.pack(pady=10)

left_frame = Frame(frame)
left_frame.pack(side="left", padx=40)

osu_var = IntVar()
taiko_var = IntVar()
catch_var = IntVar()
mania_var = IntVar()
osu_check = Checkbutton(left_frame, text="Osu!", variable=osu_var)
taiko_check = Checkbutton(left_frame, text="Taiko", variable=taiko_var)
catch_check = Checkbutton(left_frame, text="Catch", variable=catch_var)
mania_check = Checkbutton(left_frame, text="Mania", variable=mania_var)
osu_check.pack(anchor='w')
taiko_check.pack(anchor='w')
catch_check.pack(anchor='w')
mania_check.pack(anchor='w')

right_frame = Frame(frame)
right_frame.pack(side="right", padx=40)

bgs_var = StringVar(value="keep")
bgs_label = Label(right_frame, text="BGs:")
bgs_label.pack(anchor='w')
bgs_options = ["keep", "white", "delete", "custom"]
bgs_menu = OptionMenu(right_frame, bgs_var, *bgs_options)
bgs_menu.pack(anchor='w')

progress_label = Label(root, text="Progress:")
progress_label.pack(pady=10)

progress = Progressbar(root, length=300, mode='determinate')
progress.pack(padx=10)

start_button = Button(root, text="Destroy everything", command=start_cleaning)
start_button.pack(pady=20)

center_window(root, 320, 250)

root.mainloop()
