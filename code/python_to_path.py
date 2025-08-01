import os
import subprocess
import ctypes
import sys

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def add_to_system_path(directory):
    # Get the current system PATH
    system_path = os.environ['PATH']
    if directory not in system_path:
        # Add the directory to the system PATH
        new_path = system_path + ';' + directory
        os.environ['PATH'] = new_path

        # Update the system PATH permanently
        subprocess.run(['setx', 'PATH', new_path], shell=True)
        print(f"Added '{directory}' to the system PATH.")
    else:
        print(f"'{directory}' is already in the system PATH.")

def main():
    # You may need to change this path according to your Tesseract installation
    tesseract_path = r'C:\Program Files\Tesseract-OCR'

    if is_admin():
        # Add Tesseract to system PATH
        add_to_system_path(tesseract_path)
    else:
        # Re-run the script with admin rights
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

if __name__ == '__main__':
    main()
