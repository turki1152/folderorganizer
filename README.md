# Folder Organizer

A small Python tool that sorts messy folders into clean structure by **file type** (Images, Documents, Videos, etc.) or by **modified date** (Year-Month folders).

Use the **desktop app** for a colorful, easy UI, or the **terminal** if you prefer the command line. Every run shows a **preview first**; nothing moves until you confirm.

## Features

- Colorful desktop GUI built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
- Dark, light, or system theme
- Organize by file type or by modified date
- Optional recursive scan (include subfolders)
- Scrollable preview of planned moves (up to 500 lines shown)
- Progress bar while scanning and organizing
- Duplicate-safe moves (renames instead of overwriting)
- Cross-platform: Windows, Linux, macOS

### File type categories

Images, Videos, Audio, Documents, Spreadsheets, Presentations, Archives, Code, Installers, and Other.

## Requirements

- Python 3.10+ recommended
- GUI: `customtkinter` (see install below)
- CLI: standard library only

## Install

Clone the repo:

```bash
git clone https://github.com/turki1152/folderorganizer.git
cd folderorganizer
```

Install GUI dependency:

```powershell
pip install -r requirements.txt
```

## Run

### Desktop app (recommended)

**Windows:**

```powershell
python .\gui.py
```

**Linux / macOS:**

```bash
python3 gui.py
```

### Terminal

**Windows:**

```powershell
python .\folderorganizer.py
```

**Linux / macOS:**

```bash
chmod +x folderorganizer
./folderorganizer
```

Optional: install the CLI on Linux:

```bash
sudo cp folderorganizer /usr/local/bin/folderorganizer
sudo cp folderorganizer.py /usr/local/bin/folderorganizer.py
folderorganizer
```

## How to use (GUI)

1. Click **Browse** and pick the folder to organize.
2. Choose **file type** or **date** mode.
3. Toggle **Include files in subfolders** if needed.
4. Click **Preview moves** and review the list.
5. Click **Organize now** and confirm.

## Safety

- The GUI always previews moves before organizing.
- The CLI asks for confirmation at the end; answering `n` cancels with no changes.
- Already-organized files (inside category folders) are skipped on the next run.

## Project layout

| File | Purpose |
|------|---------|
| `gui.py` | Desktop application |
| `folderorganizer.py` | Core logic and CLI |
| `folderorganizer` | Shell launcher (Linux/macOS) |
| `requirements.txt` | GUI dependencies |

## Author

[turki1152](https://github.com/turki1152)

## License

Use and modify freely for personal projects.
