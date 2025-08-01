import subprocess
import sys

def check_and_install_package(package_name):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} installed successfully.")
    except subprocess.CalledProcessError:
        print(f"Failed to install {package_name}.")

def check_npm_installed():
    try:
        subprocess.check_call(["npm", "--version"])
        print("npm is already installed.")
    except subprocess.CalledProcessError:
        print("npm is not installed. Please install Node.js and npm from https://nodejs.org/")

if __name__ == "__main__":
    # List of Python packages to be installed
    python_packages = ["click", "gitpython", "invoke", "requests"]

    # Install Python packages
    for package in python_packages:
        check_and_install_package(package)

    # Check if npm is installed
    check_npm_installed()
