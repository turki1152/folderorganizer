import shutil
import sys
from datetime import datetime
from pathlib import Path


APP_NAME = "folderorganizer"
APP_BANNER = r"""
  __       _     _                                      _
 / _| ___ | | __| | ___ _ __ ___  _ __ __ _  __ _ _ __ (_)_______ _ __
| |_ / _ \| |/ _` |/ _ \ '__/ _ \| '__/ _` |/ _` | '_ \| |_  / _ \ '__|
|  _| (_) | | (_| |  __/ | | (_) | | | (_| | (_| | | | | |/ /  __/ |
|_|  \___/|_|\__,_|\___|_|  \___/|_|  \__, |\__,_|_| |_|_/___\___|_|
                                      |___/
"""

CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".heic"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm", ".wmv"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".odp"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"},
    "Code": {
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".java",
        ".c",
        ".cpp",
        ".cs",
        ".php",
        ".rb",
        ".go",
        ".rs",
        ".sh",
        ".ps1",
        ".json",
        ".xml",
        ".yml",
        ".yaml",
    },
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".appimage"},
}

SKIP_NAMES = {
    "desktop.ini",
    ".ds_store",
    "thumbs.db",
}


def configure_output_encoding():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def ask_required(prompt):
    while True:
        value = input(prompt).strip().strip('"')
        if value:
            return value
        print("Please enter a value.")


def ask_yes_no(prompt, default=False):
    hint = "Y/n" if default else "y/N"
    answer = input(f"{prompt} ({hint}): ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def choose_folder():
    print("\nWhich folder do you want to organize?")
    print("Tip: paste a full path, for example C:\\Users\\you\\Downloads")

    while True:
        folder = Path(ask_required("Folder path: ")).expanduser()
        if folder.exists() and folder.is_dir():
            return folder.resolve()
        print("That folder does not exist. Try again.")


def choose_mode():
    print("\nHow do you want to organize?")
    print("  1. By file type - Images, Documents, Videos, Archives, and more.")
    print("  2. By date      - Year-Month folders based on modified time.")

    while True:
        choice = input("\nChoose 1-2: ").strip()
        if choice == "1":
            return "type"
        if choice == "2":
            return "date"
        print("Please choose 1 or 2.")


def category_for_file(path):
    suffix = path.suffix.lower()
    for category, extensions in CATEGORIES.items():
        if suffix in extensions:
            return category
    return "Other"


def destination_for_file(path, root, mode):
    if mode == "date":
        modified = datetime.fromtimestamp(path.stat().st_mtime)
        return root / modified.strftime("%Y-%m") / path.name

    return root / category_for_file(path) / path.name


def unique_destination(destination):
    if not destination.exists():
        return destination

    stem = destination.stem
    suffix = destination.suffix
    parent = destination.parent
    counter = 1

    while True:
        candidate = parent / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def find_files(root, recursive):
    iterator = root.rglob("*") if recursive else root.iterdir()
    files = []

    for path in iterator:
        if not path.is_file():
            continue
        if path.name.lower() in SKIP_NAMES:
            continue
        if any(part in CATEGORIES or part == "Other" for part in path.relative_to(root).parts[:-1]):
            continue
        files.append(path)

    return files


def build_plan(root, mode, recursive):
    plan = []
    for source in find_files(root, recursive):
        destination = unique_destination(destination_for_file(source, root, mode))
        if source == destination:
            continue
        plan.append((source, destination))
    return plan


def format_plan_preview(plan, root, max_lines=30):
    lines = []
    for source, destination in plan[:max_lines]:
        lines.append(f"{source.relative_to(root)} -> {destination.relative_to(root)}")
    return lines, len(plan) > max_lines


def print_plan(plan, root):
    if not plan:
        print("\nNothing to organize.")
        return

    print(f"\nPreview: {len(plan)} file(s) will move\n")
    lines, truncated = format_plan_preview(plan, root, max_lines=30)
    for line in lines:
        print(line)

    if truncated:
        print(f"... and {len(plan) - 30} more")


def apply_plan(plan, on_progress=None):
    total = len(plan)
    for index, (source, destination) in enumerate(plan, start=1):
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        if on_progress is not None:
            on_progress(index, total)


def main():
    configure_output_encoding()
    print(APP_BANNER)
    print(f"{APP_NAME} - folder automation tool")
    print("Organizes files into clean folders. Preview first, move only when you confirm.\n")

    root = choose_folder()
    mode = choose_mode()
    recursive = ask_yes_no("\nInclude files inside subfolders?", default=False)

    plan = build_plan(root, mode, recursive)
    print_plan(plan, root)

    if not plan:
        return

    if not ask_yes_no("\nOrganize now?"):
        print("Canceled. No files were moved.")
        return

    apply_plan(plan)
    print(f"\nDone. Moved {len(plan)} file(s).")


if __name__ == "__main__":
    main()
