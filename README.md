# File Cleanup Utility

A Python script that helps organize files in a directory.

Files older than a selected cutoff year are moved into a `Trash` folder for manual review. All other files are sorted into an `organized` folder by file extension.

## Features

- Creates a `Trash` folder for older files
- Creates an `organized` folder for sorted files
- Moves older files to `Trash` instead of deleting them immediately
- Sorts remaining files into subfolders based on extension
- Supports dry-run mode by default
- Supports recursive scanning
- Can permanently empty the `Trash` folder after review

## How It Works

1. The script scans the selected directory.
2. Files older than the cutoff year are moved into `Trash`.
3. Remaining files are moved into `organized/<extension>`.
4. The user can review the contents of `Trash`.
5. If the files are no longer needed, the user can run `empty-trash` to permanently delete them.

## Requirements

- Python 3.x

## Usage

### Dry run

Preview what the script will do without moving any files:

```bash
python cleanup.py run --path "YOUR_PATH" --recursive
```

### Execute changes

Actually, move the files after reviewing the dry run:

```bash
python cleanup.py run --path "C:\Users\YourName\Desktop" --recursive --execute
```

### Empty Trash

**Warning:** `empty-trash` does not support dry-run mode. Once confirmed, deletion is permanent.

Permanently delete everything inside the `Trash` folder:

```bash
python cleanup.py empty-trash --path "YOUR_PATH"
```

## Command Options

`run`
* `--path`: target directory to organize

* `--cutoff-year`: files older than this year are moved to `Trash`

* `--execute`: applies the file moves instead of running in dry run mode

* `--recursive`: scans subfolders recursively

* `--exclude-extension`: skips selected file extensions

* `--exclude-folder`: skips selected folder names

`empty-trash`
* `--path`: base directory containing the `Trash` folder

## Notes

* Dry-run mode is enabled by default
* `Trash` is used as a review folder before permanent deletion
* `empty-trash` permanently deletes all contents inside `Trash` and does not support dry-run mode
* Files without an extension can be placed into a `no_extension` folder
