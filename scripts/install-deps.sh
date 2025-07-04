#!/bin/bash

# Dependency installation script for BERKE0S
# Supports multiple Linux distributions

set -e

echo "Installing BERKE0S dependencies..."

# Detect package manager
if command -v apt-get >/dev/null 2>&1; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y python3 python3-tk python3-pip git curl wget
    sudo apt-get install -y xorg xinit xserver-xorg-core
    
elif command -v yum >/dev/null 2>&1; then
    # Red Hat/CentOS
    sudo yum install -y python3 python3-tkinter python3-pip git curl wget
    sudo yum install -y xorg-x11-server-Xorg xinit
    
elif command -v pacman >/dev/null 2>&1; then
    # Arch Linux
    sudo pacman -S --noconfirm python python-pip git curl wget
    sudo pacman -S --noconfirm xorg-server xinit
    
elif command -v tce-load >/dev/null 2>&1; then
    # Tiny Core Linux
    tce-load -wi python3.tcz
    tce-load -wi python3-tkinter.tcz
    tce-load -wi git.tcz
    tce-load -wi curl.tcz
    tce-load -wi Xorg-7.7.tcz
    tce-load -wi flwm.tcz
    
else
    echo "Unsupported package manager. Please install dependencies manually."
    exit 1
fi

# Install Python packages
pip3 install --user -r requirements.txt

echo "Dependencies installed successfully!"