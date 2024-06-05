import os
import re
import json
import shutil
from tkinter import Tk, filedialog, messagebox, Button, Label
from tkinter.ttk import Progressbar

def parse_osu_file(osu_file_path):
    audio_filename = ""
    image_filenames = set()
    with open(osu_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("AudioFilename: "):
                audio_filename = line.split(": ")[1].strip()
            elif re.match(r'^\d+,\d+,".+\.(jpg|png)"', line):
                match = re.search(r'"(.+)"', line)
                if match:
                    image_filenames.add(match.group(1))
    return audio_filename, image_filenames

def process_folder(folder_path, user_images, processed_folders, delete_images):
    osu_files = [f for f in os.listdir(folder_path) if f.endswith('.osu')]
    audio_files = set()
    image_files = set()
    
    for osu_file in osu_files:
        osu_path = os.path.join(folder_path, osu_file)
        audio, images = parse_osu_file(osu_path)
        if audio:
            audio_files.add(audio)
        image_files.update(images)
    
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

def start_cleaning():
    root.withdraw()
    
    songs_folder = filedialog.askdirectory(title="Select Songs Folder")
    if not songs_folder:
        messagebox.showerror("Fatal error", "Why you...")
        root.deiconify()
        return
    
    change_bgs = messagebox.askyesno("Wanna change bgs?", "If not, I would just delete them")
    
    if change_bgs:
        png_image = filedialog.askopenfilename(title="Select PNG Image", filetypes=[("PNG files", "*.png")])
        jpg_image = filedialog.askopenfilename(title="Select JPG Image", filetypes=[("JPG files", "*.jpg")])
        if not png_image or not jpg_image:
            messagebox.showerror("Fatal error", "That won't work. Why you pressed yes tho?")
            root.deiconify()
            return
        user_images = {'.png': png_image, '.jpg': jpg_image}
        delete_images = False
    else:
        user_images = None
        delete_images = True
    
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
    
    for folder in all_folders:
        folder_name = os.path.basename(folder)
        folder_id_match = re.match(r'^(\d+)', folder_name)
        if folder_id_match:
            folder_id = int(folder_id_match.group(1))
            if folder_id in processed_folders:
                continue
            process_folder(folder, user_images, processed_folders, delete_images)
            progress.step()
            progress_label.config(text=f"Cleaning {folder_id}...")
            root.update_idletasks()
    
    with open(json_file_path, 'w') as json_file:
        json.dump(processed_folders, json_file)
    
    messagebox.showinfo("Info", "Everything's clean. Check the size of your songs folder lol")
    root.destroy()

root = Tk()
root.title("sh(x)cleaner")

progress_label = Label(root, text="Progress:")
progress_label.pack(pady=10)

progress = Progressbar(root, length=400, mode='determinate')
progress.pack(pady=10)

start_button = Button(root, text="Destroy everything", command=start_cleaning)
start_button.pack(pady=20)

root.mainloop()
