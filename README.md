<div align="center">
<strong>English</strong> | <a href="README_RU.md">Русский</a>
</div>

<br>

<h1 align="center">sh(x)cleaner</h1>

<p align="center">
  Clean up your osu! <code>Songs</code> folder from junk in just a few clicks.
</p>

<p align="center">
  <img src="preview.png" alt="sh(x)cleaner screenshot" width="320"/>
</p>

---

## How to use

1.  **Download:** the latest version is available on the [releases page](https://github.com/shsh-x/sh-x-cleaner/releases/latest)
2.  **Run the .exe:** the cleaner is fully portable
3.  **Select `osu!.exe`:** when starting the cleaning process, you need to provide the path to `osu!.exe` to automatically locate the `Songs` folder and avoid deleting anything important
4.  **Choose modes to delete:** for example, if you only play `Osu!`, check `Taiko`, `Catch`, and `Mania`
5.  **Choose a background option:**
    *   **Keep:** leaves the original backgrounds
    *   **White:** replaces all backgrounds with a simple white image
    *   **Custom:** replaces all backgrounds with your own image (you'll need to select two images: a png and a jpg/jpeg)
    *   **Delete:** deletes all backgrounds (not recommended)
6.  **Press "Clean it up!"** and wait for the process to finish
7.  **Press F5 in the song selector** to refresh the state of all beatmaps

---
## Advanced options (for power users)

These options are available via the context menu (right-click on the title):

*   **Force Clean:** re-scans and cleans all folders, even if they were previously cleaned
*   **Keep Videos:** keeps background videos
*   **Dangerous Clean:** removes junk files from folders that do not have a numeric ID in their name **(use with caution!)**
*   **Ignore ID Limit:** processes folders with an ID of 9 characters or more

---
## Running and Building from Source

The executable file is not digitally signed, so some antivirus software may flag it - this is a false positive. If you don't trust the `.exe` file, you can easily run it from source or build the application yourself.

1.  **Install Python:** [Python 3.12+](https://www.python.org/downloads/) is recommended
2.  **Download the code:** download and unzip the [source code archive](https://github.com/shsh-x/sh-x-cleaner/archive/refs/heads/main.zip)
3.  **Create a virtual environment:** in a terminal in the project folder, run
    ```shell
    python -m venv venv
    ```
4.  **Activate the environment:**
    *   On **Windows**:
        ```shell
        .\venv\Scripts\activate
        ```
    *   On **Linux/macOS**:
        ```shell
        source venv/bin/activate
        ```
5.  **Install dependencies:** with the environment activated, run
    ```shell
    pip install -r requirements.txt
    ```
6.  **Run or Build:**
    *   To **run** the cleaner, execute
        ```shell
        python main.py
        ```
    *   To **build** your own `.exe` file, execute
        ```shell
        python build_exe.py
        ```
        The finished file will appear in the `dist` folder.

---

## How does it work?

*   **From the beatmap folder, the following are removed:**
    - Selected game modes
    - All beatmap skins
    - All hitsounds
    - All videos (.mp4, .avi, .flv)
    - All storyboards (.osb)
    - and all files unrelated to the beatmap
*   **A beatmap folder is deleted** if no `.osu` files remain in it after cleaning
*   **Backgrounds are optimized** by replacing all images with symbolic links, with each original image stored once in a separate folder inside `Songs`
*   **Duplicates are removed** if folders with the same beatmap ID are found, leaving only one (usually the most recently imported one).