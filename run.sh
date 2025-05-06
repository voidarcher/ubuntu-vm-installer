#!/bin/bash

# Define the relative path from the script to the target file
ISO_DIR="$(pwd)/src"
ISO_FILENAME="ubuntu-24.04.2-live-server-amd64.iso"

# Define the full path to the ISO file 
FULL_PATH="$ISO_DIR/$ISO_FILENAME"

# URL to download the ISO file from
URL="https://releases.ubuntu.com/24.04.2/ubuntu-24.04.2-live-server-amd64.iso"

# Check for dependencies
if ! command -v genisoimage &> /dev/null; then
    echo "Dependency genisoimage is not installed"
    echo "If you're on Linux, install genisoimage"
    echo "If you're on Mac, install mkisofs"
    exit 1
fi

if ! command -v VBoxManage &> /dev/null; then
    echo "Dependency VirtualBox is not installed, or"
    echo "VBoxManage is not in your PATH."
    exit 1
fi

# Check and download
if [ ! -f "$FULL_PATH" ]; then
    echo "File not found at $FULL_PATH. Downloading..."
    wget -P $ISO_DIR $URL
else
    echo "File already exists at $FULL_PATH. No download needed."
fi

# Once ISO file is in place, run main.py
python -u "./src/main.py"