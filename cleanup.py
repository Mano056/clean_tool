from pathlib import Path
from datetime import datetime
import shutil
import argparse
import logging
import sys

# =====================
# ARGUMENT PARSER
# =====================

parser = argparse.ArgumentParser(
    description='File cleanup utility: organize files, archive old files, and manage trash.'
)

subparsers = parser.add_subparsers(dest='command')

# =====================
# RUN COMMAND (MAIN TOOL)
# =====================

run_parser = subparsers.add_parser('run', help='Run cleanup and organization')

run_parser.add_argument(
    '--path',
    type=str,
    default=str(Path.home() / 'OneDrive' / 'Desktop'),
    help='Target directory to organize'
)

run_parser.add_argument(
    '--cutoff-year',
    type=int,
    default=2023,
    help='Files older than this year go to Trash(new folder)'
)

run_parser.add_argument(
    '--execute',
    action='store_true',
    help='Actually move files (default is dry-run)'
)

run_parser.add_argument(
    '--recursive',
    action='store_true',
    help='Scan folders recursively'
)

run_parser.add_argument(
    '--exclude-extension',
    nargs='*',
    default=[],
    help='Additional extensions to exclude (example: .zip  .iso  .mp4)'
)

run_parser.add_argument(
    '--exclude-folder',
    nargs='*',
    default=[],
    help='Folder names to exclude from scanning'
)

# =====================
# EMPTY TRASH COMMAND
# =====================

trash_parser = subparsers.add_parser(
    'empty-trash', 
    help='Permanently delete files in Trash'
    )

trash_parser.add_argument(
    '--path',
    type=str,
    default=str(Path.home() / 'OneDrive' / 'Desktop'),
    help='Base directory containing Trash folder'
)

args = parser.parse_args()

# =====================
# HELP: NO COMMAND
# =====================

if args.command is None:
    parser.print_help()
    sys.exit()

# =====================
# CONFIG
# =====================

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

home = Path(args.path).expanduser().resolve()
trash = home / 'Trash'
organized = home / 'organized'

# =====================
# HELPERS
# =====================

def normalize_extension(ext):
    ext = ext.lower()
    return ext if ext.startswith('.') else f'.{ext}'

def ensure_folder(path, dry_run=False):
    if path.exists():
        return
    
    logging.info(f'Creating folder: {path}')
    if not dry_run:
        path.mkdir(parents=True, exist_ok=True)

def is_old(file_path, cutoff):
    '''
    Check if file is older than cutoff date.
    '''
    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
    return modified_time < cutoff

def get_extension_folder(file_path, dry_run):
    '''
    Return target folder based on file extension.
    '''
    extension = file_path.suffix[1:].lower() or 'no_extension'
    target_folder = organized / extension
    ensure_folder(target_folder, dry_run)
    return target_folder

def get_unique_destination(target_folder, file_path):
    '''
    Prevent filename collisions.
    '''
    destination = target_folder / file_path.name

    if not destination.exists():
        return destination
    
    num = 1
    while True:
        new_name = f'{file_path.stem}_{num}{file_path.suffix}'
        new_destination = target_folder / new_name

        if not new_destination.exist():
            return new_destination
        
        num += 1

def move_file(source, destination, dry_run):
    '''
    Move file safely.
    '''
    logging.info(f'Moving: {source} --> {destination}')

    if not dry_run:
        shutil.move(str(source), str(destination))

def should_skip(file_path, excluded_roots, protected_extensions):
    '''
    Determine whether file should be skipped.
    '''
    if not file_path.is_file():
        return True
    
    if file_path.suffix.lower() in protected_extensions:
        logging.warning(f'Skipping protected file: {file_path}')
        return True
    
    for excluded_root in excluded_roots:
        if file_path == excluded_root or excluded_root in file_path.parents:
            return True
        
    return False

# =====================
# EMPTY TRASH LOGIC
# =====================

if args.command == 'empty-trash':
    if not trash.exists():
        print('Trash folder does not exists.')
        sys.exit()
    
    print(f'This will permanently delete everything inside: {trash}')
    confirm = input('Type YES to continue: ')

    if confirm != 'YES':
        print('Cancelled.')
        sys.exit()

    for item in list(trash.iterdir()):
        try:
            if item.is_dir():
                logging.info(f'Deleting folder: {item}')
                shutil.rmtree(item)
            else:
                logging.info(f'Deleting file: {item}')
                item.unlink()
        except Exception as e:
            logging.error(f'Error deleting {item}: {e}')
        
    print('Trash emptied.')
    sys.exit()

# =====================
# RUN MODE SETUP
# =====================

if args.command == 'run':
    cutoff = datetime(args.cutoff_year, 1, 1)
    dry_run = not args.execute

    protected_extensions = {
        '.exe',
        '.dll',
        '.sys',
        '.bat',
        '.cmd'
    }

    protected_extensions.update(
        normalize_extension(ext) for ext in args.exclude_extension
    )

    excluded_roots = {organized, trash}
    excluded_names = {name.casefold() for name in args.exclude_folder}

    ensure_folder(trash, dry_run)
    ensure_folder(organized, dry_run)

    files = list(home.rglob('*')) if args.recursive else list(home.glob('*'))

    moved_to_organized = 0
    moved_to_trash = 0
    skipped_entries = 0

    logging.info("Starting cleanup...")
    logging.info(f'DRY RUN = {dry_run}')

    for file_path in files:
        try:
            # Skip anything inside excluded folder names.
            if any(
                parent.name.casefold() in excluded_names
                for parent in file_path.parents
                if parent != home
            ):
                skipped_entries += 1
                continue

            # Skip the excluded folder entries themselves.
            if file_path.is_dir() and file_path.name.casefold() in excluded_names:
                skipped_entries += 1
                continue

            if should_skip(file_path, excluded_roots, protected_extensions):
                skipped_entries += 1
                continue

            # OLD FILES -> TRASH
            if is_old(file_path, cutoff):
                destination = get_unique_destination(trash, file_path)
                move_file(file_path, destination, dry_run)
                moved_to_trash += 1
            
            # ORGANIZE BY EXTENSION
            else:
                target_folder = get_extension_folder(file_path, dry_run)
                destination = get_unique_destination(target_folder, file_path)
                move_file(file_path, destination, dry_run)
                moved_to_organized += 1
        
        except Exception as error:
            logging.error(f'Error processing {file_path}: {error}')
    
    # =====================
    # SUMMARY
    # =====================

    print('\n========== SUMMARY ==========')
    print(f'Moved to organized : {moved_to_organized}')
    print(f'Moved to Trash     : {moved_to_trash}')
    print(f'Skipped entries    : {skipped_entries}')
    print(f'Dry run mode       : {dry_run}')
    print('===============================')