import os
import json
import keyboard
import subprocess

CACHE_FILE = '.file_selection_cache'
LIBRARY_PATH = './source'

def get_terminal_size():
    try:
        rows, columns = os.get_terminal_size(0)
    except OSError:
        try:
            rows, columns = subprocess.check_output(['stty', 'size']).split()
        except Exception:
            rows, columns = 24, 80  # Fallback size
    return int(rows), int(columns)

def get_file_size(file_path):
    size_bytes = os.path.getsize(file_path)
    return size_bytes

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f}GB"

def load_cache():
    try:
        with open(CACHE_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_cache(selected_files):
    with open(CACHE_FILE, 'w') as file:
        json.dump(selected_files, file)

def print_files(files, selected_files, index, total_size):
    _, columns = get_terminal_size()
    os.system('cls' if os.name == 'nt' else 'clear')
    for i, (file, size) in enumerate(files):
        prefix = '[X]' if file in selected_files else '[ ]'
        selection_marker = '\033[93m>\033[0m' if i == index else ' '
        selected_color = '\033[92m' if file in selected_files else ''
        size_formatted = format_size(size)
        print(f"{selection_marker} {prefix} {selected_color}{file.ljust(columns - len(size_formatted) - 6)}{size_formatted}\033[0m")
    warning = '\033[93mWarning: Total selected size exceeds 40MB\033[0m' if total_size > 40 * 1024 * 1024 else ''
    print(f"\nTotal selected size: {format_size(total_size)} {warning}")

def navigate_files(files, selected_files):
    index = 0
    total_size = sum(size for file, size in files if file in selected_files)
    print_files(files, selected_files, index, total_size)

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'down':
                index = min(index + 1, len(files) - 1)
            elif event.name == 'up':
                index = max(index - 1, 0)
            elif event.name == 'space' or event.name == 'enter':
                file, size = files[index]
                if file in selected_files:
                    selected_files.remove(file)
                    total_size -= size
                else:
                    selected_files.append(file)
                    total_size += size
            elif event.name == 'c':
                break
            elif event.name == 'r':
                selected_files = load_cache()
                total_size = sum(size for file, size in files if file in selected_files)
            print_files(files, selected_files, index, total_size)

    save_cache(selected_files)
    return selected_files

def get_files():
    all_files = []
    for root, dirs, files in os.walk(LIBRARY_PATH):
        for name in files:
            file_path = os.path.join(root, name)
            relative_path = os.path.relpath(file_path, LIBRARY_PATH)
            all_files.append((relative_path, get_file_size(file_path)))
    return all_files

def save_selection(selected_files):
    # Remaining function body unchanged
    pass

def main():
    files = get_files()
    selected_files = load_cache()
    selected_files = navigate_files(files, selected_files)
    # Remaining main function logic unchanged

if __name__ == "__main__":
    main()
