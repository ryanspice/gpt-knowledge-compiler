import subprocess
import platform
import os

def run_script(script_path):
    if platform.system() == "Windows":
        subprocess.call(["powershell.exe", script_path], shell=True)
    else:
        subprocess.call(["bash", script_path])

def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if platform.system() == "Windows":
        script_path = os.path.join(current_dir, "install.ps1")
    else:
        script_path = os.path.join(current_dir, "install.sh")

    if os.path.exists(script_path):
        run_script(script_path)
    else:
        print(f"Installation script not found: {script_path}")

if __name__ == "__main__":
    main()
