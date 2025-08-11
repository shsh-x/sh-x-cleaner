⚠️ **THIS REPO HAS BEEN ARCHIVED AND WILL NO LONGER BE UPDATED** ⚠️

🐾 **Please, check [Paws – our new cross platform toolbox](https://github.com/osupaws/paws), it's better in every way!** 🐾

## What is it?
It's a script that cleans your osu!stable songs folder of junk like hitsounds, videos, storyboards, and skin elements.

## How to use

In the left section you can choose what modes to delete - it will devastate every difficulty with chosen mode.

In the right section you can choose what to do with backgrounds:

• Keep - leaves background images as is

• White (recommended) - replaces all the bgs with 1x1px white image (67 bytes for .png and 153 bytes for .jpg/.jpeg) 

• Custom - lets you choose your own image to replace all the bgs (you must choose both png and jpg/jpeg)

• Delete - removes all the bgs (not recommended, you will see the annoying warning everytime the map starts)

![Window preview](https://i.imgur.com/IxXT8hV.png)

After choosing the desired options press 'Destroy everything' button, then choose your Songs folder (not osu! folder) and custom images if you selected custom backgrounds.

While the script makes its' dirty work you can make some tea. In the progressbar you can see currently processing map's ID.

## How to run

To start doing funny things you can either:

### Run the Executable

1. Download the `.exe` file from the [releases](https://github.com/shsh-x/sh-x-cleaner/releases/latest) section.
2. Run the `.exe` file.

### Build the Executable (Python 3.12 required)

If you prefer to build the executable yourself:

1. Install [PyInstaller](https://www.pyinstaller.org/):

   ```sh
   pip install pyinstaller
   ```

2. (Optional) Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies from `requirements.txt`:

   ```sh
   pip install -r requirements.txt
   ```

4. If using a virtual environment, set the `use_venv` and `venv_path` parameters in `build_exe.py`:

   ```python
   use_venv = True
   venv_path = 'venv'
   ```

5. Run the build script:

   ```sh
   python build_exe.py
   ```

6. Run built `.exe` file (located in the `dist` directory).

### Run the Script Directly (are you scared of .exe?)

1. Ensure Python 3.12 is installed on your system.
2. (Optional) Create and activate a virtual environment:

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install dependencies from `requirements.txt`:

   ```sh
   pip install -r requirements.txt
   ```

4. Run the script directly:

   ```sh
   python main.py
   ```

## Issues and Contributions

If you have any suggestions for optimization or encounter any issues, feel free to open an [issue](https://github.com/shsh-x/sh-x-cleaner/issues) on the project's repository.

---

Enjoy cleaning your osu! songs and enhancing your gaming experience!
