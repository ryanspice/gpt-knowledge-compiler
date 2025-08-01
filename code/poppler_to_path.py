import os
import subprocess
import sys

def add_to_system_path(new_path):
    # Get the current system PATH
    current_path = os.environ['PATH']

    # Check if the new path is already in PATH
    if new_path in current_path.split(os.pathsep):
        print("Path already exists in the system PATH.")
        return

    # Append the new path to the system PATH
    updated_path = current_path + os.pathsep + new_path

    # Set the new PATH
    try:
        # Using 'setx' command to modify the system PATH permanently
        subprocess.run(['setx', 'PATH', f'"{updated_path}"'], check=True)
        print(f"Successfully added {new_path} to system PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error updating system PATH: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Replace this with the path where Poppler's bin directory is located
    poppler_path = r"C:\poppler-23.11.0\Library\bin"

    add_to_system_path(poppler_path)
