import os
import platform

# Define the path to the library folder
library_path = 'source'
cache_file_path = '.file_selection_cache'

# Cross-platform getch implementation
class _Getch:
    """Gets a single character from standard input. Does not echo to the screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys, termios

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()

def get_file_size(file_path):
    """Return the file size in bytes."""
    return os.path.getsize(file_path)

def save_selection_cache(selected_files):
    """Save the selected files to the cache file."""
    with open(cache_file_path, 'w') as cache_file:
        for file_index in selected_files:
            cache_file.write(f"{file_index}\n")

def load_selection_cache():
    """Load the selected files from the cache file."""
    selected_files = set()
    if os.path.exists(cache_file_path):
        with open(cache_file_path, 'r') as cache_file:
            for line in cache_file:
                selected_files.add(int(line.strip()))
    return selected_files

def draw_menu(directory, selected_row_idx, selected_files):
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the console window
    print(f"Current directory: {directory}\n")
    files = os.listdir(directory)
    total_size = 0

    print("{:<50} {:>10}".format("File", "Size"))
    for idx, file in enumerate(files):
        size = get_file_size(os.path.join(directory, file))
        is_selected = idx in selected_files
        is_current = idx == selected_row_idx
        color_start = "\033[42m\033[30m" if is_selected else "\033[47m\033[30m" if is_current else ""
        color_end = "\033[0m"
        print(f"{color_start}{'X' if is_selected else ' '} {file:<48} {size:>10} bytes{color_end}")
        if is_selected:
            total_size += size

    print(f"\nTotal selected size: {total_size} bytes")
    print("\nUse W and S to move, Space to select, Enter to confirm, Q to quit.")

def main():
    current_row = 0
    selected_files = load_selection_cache()
    current_directory = library_path

    try:
        draw_menu(current_directory, current_row, selected_files)

        while True:
            key = getch()

            if platform.system() == 'Windows':
                if key == b'H':  # Arrow up
                    current_row = max(current_row - 1, 0)
                elif key == b'P':  # Arrow down
                    current_row = min(current_row + 1, len(os.listdir(current_directory)) - 1)
            else:
                if key == '\x1b':  # Escape sequence for arrow keys
                    getch()  # Skip the '[' character
                    arrow = getch()
                    if arrow == 'A':  # Arrow up
                        current_row = max(current_row - 1, 0)
                    elif arrow == 'B':  # Arrow down
                        current_row = min(current_row + 1, len(os.listdir(current_directory)) - 1)

            if key in [' ', b' ']:  # Space key for selection
                if current_row in selected_files:
                    selected_files.remove(current_row)
                else:
                    selected_files.add(current_row)
                save_selection_cache(selected_files)  # Update the cache file on every selection change
            elif key in ['\r', '\n', b'\r', b'\n']:  # Enter key
                break
            elif key in ['q', 'Q', b'q', b'Q']:  # Quit
                break

            draw_menu(current_directory, current_row, selected_files)
    except KeyboardInterrupt:
        print("\nExiting...")  # Optional: print a message indicating exit
        pass  # Perform any cleanup here if necessary

if __name__ == "__main__":
    main()
