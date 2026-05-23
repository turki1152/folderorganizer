# folderorganizer

folderorganizer is a small Python automation script that organizes files into folders.

It previews the moves first, then asks before moving anything.

## Features

- Organize by file type
- Organize by modified date
- Optional recursive mode
- Prevents overwriting by renaming duplicates
- Works on Windows, Linux, and macOS

## Run

Windows:

```powershell
python .\folderorganizer.py
```

Linux/macOS:

```bash
chmod +x folderorganizer
./folderorganizer
```

To install as a command on Linux:

```bash
sudo cp folderorganizer /usr/local/bin/folderorganizer
sudo cp folderorganizer.py /usr/local/bin/folderorganizer.py
folderorganizer
```

## Safety

The tool shows a preview before moving files. If you answer `n` at the final prompt, nothing is moved.
