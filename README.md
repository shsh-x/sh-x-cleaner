# Hello there

This is a rough coded python script for cleaning osu! songs from junk.
It basically removes everything except the difficulty files and the song itself.
Optionally, you can choose a custom bg to replace in every song.

## Requirements

- Python 3.12

## How to use

To start doing funny things you can either:

### Run the Executable

1. Download the `.exe` file from the [releases](https://github.com/shsh-x/sh-x-cleaner/releases/latest) section.
2. Run the `.exe` file.

### Build the Executable

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
