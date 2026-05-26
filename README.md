# File Cleanup Utility

Short description of what the tool does.

## Features

- Creates a `Trash` folder for old files
- Creates an `organized` folder for sorted files
- Moves older files to `Trash` for manual review
- Sorts remaining files by extension into subfolders
- Supports dry-run mode
- Supports recursive scanning
- Can permanently empty the `Trash` folder

## How It Works

Explain the intended workflow in plain language:
1. The tool scans a target directory
2. Files older than the cutoff year go to `Trash`
3. Other files go into `organized/<extension>`
4. The user reviews `Trash`
5. The user can run `empty-trash` to permanently delete those files

## Requirements

- Python 3.x

## Usage

### Dry run
```bash
python file_cleanup.py run --path "YOUR_PATH" --recursive