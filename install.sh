#!/bin/bash

# BERKE0S Ultimate Desktop Environment V2 - Installation Script
# Enhanced installer for Tiny Core Linux with advanced display management
# Author: BreDEVs
# License: MIT

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BERKE0S_VERSION="3.0-v2"
BERKE0S_DIR="/opt/berke0s"
BERKE0S_USER_DIR="$HOME/.berke0s"
GITHUB_REPO="https://github.com/BreDEVs/BERKE0S"
TEMP_DIR="/tmp/berke0s_install"
LOG_FILE="/tmp/berke0s_install.log"

# System information
IS_TINY_CORE=false
OS_NAME=""
ARCH=""
PYTHON_VERSION=""
CURRENT_USER=$(whoami)
IS_ROOT=false

# Installation options
INSTALL_EXTENSIONS=true
SETUP_AUTOSTART=true
CONFIGURE_PERSISTENCE=true
INSTALL_THEMES=true

# Display banner
show_banner() {
    clear
    echo -e "${PURPLE}"
    echo "  ██████╗ ███████╗██████╗ ██╗  ██╗███████╗ ██████╗ ███████╗"
    echo "  ██╔══██╗██╔════╝██╔══██╗██║ ██╔╝██╔════╝██╔═████╗██╔════╝"
    echo "  ██████╔╝█████╗  ██████╔╝█████╔╝ █████╗  ██║██╔██║███████╗"
    echo "  ██╔══██╗██╔══╝  ██╔══██╗██╔═██╗ ██╔══╝  ████╔╝██║╚════██║"
    echo "  ██████╔╝███████╗██║  ██║██║  ██╗███████╗╚██████╔╝███████║"
    echo "  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚══════╝"
    echo -e "${NC}"
    echo -e "${CYAN}  Ultimate Desktop Environment V2 - Enhanced Display Management${NC}"
    echo -e "${BLUE}  Optimized for Tiny Core Linux${NC}"
    echo ""
    echo -e "${GREEN}Version: ${BERKE0S_VERSION}${NC}"
    echo -e "${YELLOW}Installation starting...${NC}"
    echo ""
}

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${GREEN}[INFO]${NC} $message"
            ;;
        "WARN")
            echo -e "${YELLOW}[WARN]${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
        "DEBUG")
            echo -e "${BLUE}[DEBUG]${NC} $message"
            ;;
    esac
    
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Error handler
error_exit() {
    log "ERROR" "$1"
    echo ""
    echo -e "${RED}Installation failed. Check log file: $LOG_FILE${NC}"
    echo -e "${YELLOW}For support, visit: https://github.com/BreDEVs/BERKE0S/issues${NC}"
    exit 1
}

# Detect system information
detect_system() {
    log "INFO" "Detecting system information..."
    
    # Check if root
    if [ "$EUID" -eq 0 ]; then
        IS_ROOT=true
        log "INFO" "Running as root"
    else
        log "INFO" "Running as user: $CURRENT_USER"
    fi
    
    # Detect OS
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME="$ID"
    elif [ -f /etc/tc-release ]; then
        OS_NAME="tinycore"
        IS_TINY_CORE=true
    elif [ -f /etc/tinycore-release ]; then
        OS_NAME="tinycore"
        IS_TINY_CORE=true
    fi
    
    # Additional Tiny Core detection
    if [ -d "/opt/tce" ] || [ -f "/usr/bin/tce-load" ]; then
        IS_TINY_CORE=true
        OS_NAME="tinycore"
    fi
    
    # Detect architecture
    ARCH=$(uname -m)
    
    # Detect Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d" " -f2)
    fi
    
    log "INFO" "System Information:"
    log "INFO" "  OS: $OS_NAME"
    log "INFO" "  Architecture: $ARCH"
    log "INFO" "  Tiny Core: $IS_TINY_CORE"
    log "INFO" "  Python: $PYTHON_VERSION"
    log "INFO" "  User: $CURRENT_USER"
}

# Check prerequisites
check_prerequisites() {
    log "INFO" "Checking prerequisites..."
    
    local missing_deps=()
    
    # Check essential commands
    local required_commands=("curl" "wget" "tar" "unzip")
    
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing_deps+=("$cmd")
        fi
    done
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing_deps+=("python3")
    else
        # Check Python version (minimum 3.6)
        local py_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        if (( $(echo "$py_version < 3.6" | bc -l) )); then
            error_exit "Python 3.6 or higher required. Found: $py_version"
        fi
    fi
    
    # Check Tkinter
    if ! python3 -c "import tkinter" &> /dev/null; then
        missing_deps+=("python3-tkinter")
    fi
    
    # Check git for cloning
    if ! command -v git &> /dev/null; then
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log "WARN" "Missing dependencies: ${missing_deps[*]}"
        
        if [ "$IS_TINY_CORE" = true ]; then
            log "INFO" "Installing Tiny Core extensions..."
            install_tiny_core_dependencies "${missing_deps[@]}"
        else
            log "INFO" "Please install missing dependencies manually"
            log "INFO" "On Debian/Ubuntu: sudo apt-get install ${missing_deps[*]}"
            log "INFO" "On Red Hat/CentOS: sudo yum install ${missing_deps[*]}"
        fi
    else
        log "INFO" "All prerequisites satisfied"
    fi
}

# Install Tiny Core dependencies
install_tiny_core_dependencies() {
    local deps=("$@")
    log "INFO" "Installing Tiny Core Linux extensions..."
    
    # Map dependencies to TC extensions
    declare -A tc_extensions
    tc_extensions["python3"]="python3.tcz"
    tc_extensions["python3-tkinter"]="python3-tkinter.tcz"
    tc_extensions["git"]="git.tcz"
    tc_extensions["curl"]="curl.tcz"
    tc_extensions["wget"]="wget.tcz"
    tc_extensions["tar"]="tar.tcz"
    tc_extensions["unzip"]="unzip.tcz"
    
    # Additional recommended extensions
    local recommended_extensions=(
        "Xorg-7.7.tcz"
        "flwm.tcz"
        "xdpyinfo.tcz"
        "xwininfo.tcz"
        "python3-pillow.tcz"
        "python3-setuptools.tcz"
    )
    
    # Install required extensions
    for dep in "${deps[@]}"; do
        if [ -n "${tc_extensions[$dep]}" ]; then
            log "INFO" "Installing ${tc_extensions[$dep]}..."
            if ! tce-load -wi "${tc_extensions[$dep]}"; then
                log "WARN" "Failed to install ${tc_extensions[$dep]}"
            fi
        fi
    done
    
    # Install recommended extensions
    for ext in "${recommended_extensions[@]}"; do
        log "INFO" "Installing recommended extension: $ext"
        tce-load -wi "$ext" 2>/dev/null || log "WARN" "Could not install $ext"
    done
    
    # Install Python packages
    log "INFO" "Installing Python packages..."
    local python_packages=("psutil" "pillow" "requests")
    
    for package in "${python_packages[@]}"; do
        log "INFO" "Installing Python package: $package"
        python3 -m pip install "$package" --user 2>/dev/null || log "WARN" "Could not install $package"
    done
}

# Setup directories
setup_directories() {
    log "INFO" "Setting up directories..."
    
    # Create main installation directory
    if [ "$IS_ROOT" = true ]; then
        mkdir -p "$BERKE0S_DIR"
        chown "$CURRENT_USER:$CURRENT_USER" "$BERKE0S_DIR" 2>/dev/null || true
    else
        # Use user directory if not root
        BERKE0S_DIR="$HOME/berke0s"
        mkdir -p "$BERKE0S_DIR"
    fi
    
    # Create user configuration directory
    mkdir -p "$BERKE0S_USER_DIR"
    mkdir -p "$BERKE0S_USER_DIR/themes"
    mkdir -p "$BERKE0S_USER_DIR/plugins"
    mkdir -p "$BERKE0S_USER_DIR/wallpapers"
    mkdir -p "$BERKE0S_USER_DIR/applications"
    mkdir -p "$BERKE0S_USER_DIR/backups"
    
    # Create temporary directory
    mkdir -p "$TEMP_DIR"
    
    log "INFO" "Directories created:"
    log "INFO" "  Installation: $BERKE0S_DIR"
    log "INFO" "  User config: $BERKE0S_USER_DIR"
    log "INFO" "  Temporary: $TEMP_DIR"
}

# Download BERKE0S
download_berke0s() {
    log "INFO" "Downloading BERKE0S from GitHub..."
    
    cd "$TEMP_DIR"
    
    # Try git clone first
    if command -v git &> /dev/null; then
        log "INFO" "Cloning repository with git..."
        if git clone "$GITHUB_REPO.git" berke0s-source; then
            log "INFO" "Git clone successful"
            return 0
        else
            log "WARN" "Git clone failed, trying wget..."
        fi
    fi
    
    # Fallback to wget
    log "INFO" "Downloading archive with wget..."
    if wget -O berke0s.zip "$GITHUB_REPO/archive/main.zip"; then
        log "INFO" "Download successful, extracting..."
        if unzip -q berke0s.zip; then
            mv BERKE0S-main berke0s-source
            log "INFO" "Extraction successful"
        else
            error_exit "Failed to extract archive"
        fi
    else
        error_exit "Failed to download BERKE0S"
    fi
}

# Install BERKE0S files
install_files() {
    log "INFO" "Installing BERKE0S files..."
    
    if [ ! -d "$TEMP_DIR/berke0s-source" ]; then
        error_exit "Source directory not found"
    fi
    
    # Copy all files to installation directory
    log "INFO" "Copying files to $BERKE0S_DIR..."
    cp -r "$TEMP_DIR/berke0s-source/"* "$BERKE0S_DIR/"
    
    # Set executable permissions
    find "$BERKE0S_DIR" -name "*.py" -exec chmod +x {} \;
    find "$BERKE0S_DIR" -name "*.sh" -exec chmod +x {} \;
    
    # Create main executable
    cat > "$BERKE0S_DIR/berke0s" << 'EOF'
#!/bin/bash
# BERKE0S Desktop Environment Launcher
cd "$(dirname "$0")"
python3 main.py "$@"
EOF
    chmod +x "$BERKE0S_DIR/berke0s"
    
    log "INFO" "Files installed successfully"
}

# Setup display configuration
setup_display() {
    log "INFO" "Configuring display system..."
    
    # Create display configuration
    cat > "$BERKE0S_USER_DIR/display_config.json" << 'EOF'
{
    "auto_detect": true,
    "force_x11": true,
    "display_server": "auto",
    "resolution": "auto",
    "refresh_rate": 60,
    "color_depth": 24,
    "fallback_resolution": "1024x768",
    "x_arguments": ["-nolisten", "tcp", "-nocursor"],
    "tiny_core_optimized": true
}
EOF
    
    # Create X server test script
    cat > "$BERKE0S_DIR/test_display.sh" << 'EOF'
#!/bin/bash
# Display test script for BERKE0S
echo "Testing display configuration..."

# Test X server availability
if command -v X >/dev/null 2>&1; then
    echo "✓ X server binary found"
else
    echo "✗ X server binary not found"
fi

# Test display environment
if [ -n "$DISPLAY" ]; then
    echo "✓ DISPLAY variable set: $DISPLAY"
    
    # Test X connection
    if xdpyinfo >/dev/null 2>&1; then
        echo "✓ X server connection successful"
    else
        echo "✗ X server connection failed"
    fi
else
    echo "✗ DISPLAY variable not set"
fi

# Test Tkinter
if python3 -c "import tkinter; tkinter.Tk()" >/dev/null 2>&1; then
    echo "✓ Tkinter working"
else
    echo "✗ Tkinter not working"
fi

echo "Display test complete"
EOF
    chmod +x "$BERKE0S_DIR/test_display.sh"
    
    log "INFO" "Display configuration completed"
}

# Configure Tiny Core persistence
configure_persistence() {
    if [ "$IS_TINY_CORE" != true ]; then
        log "INFO" "Skipping persistence configuration (not Tiny Core)"
        return 0
    fi
    
    log "INFO" "Configuring Tiny Core persistence..."
    
    # Add to backup list
    local backup_file="/opt/.filetool.lst"
    if [ -f "$backup_file" ]; then
        # Add BERKE0S directories to backup
        echo "opt/berke0s" >> "$backup_file"
        echo ".berke0s" >> "$backup_file"
        log "INFO" "Added BERKE0S to backup list"
    fi
    
    # Add to onboot (if using TCE)
    local onboot_file
    for tce_dir in "/mnt/sda1/tce" "/mnt/sdb1/tce" "/tmp/tce"; do
        if [ -d "$tce_dir" ]; then
            onboot_file="$tce_dir/onboot.lst"
            break
        fi
    done
    
    if [ -n "$onboot_file" ] && [ -f "$onboot_file" ]; then
        # Add required extensions to onboot
        local required_extensions=("python3.tcz" "python3-tkinter.tcz" "Xorg-7.7.tcz")
        for ext in "${required_extensions[@]}"; do
            if ! grep -q "$ext" "$onboot_file"; then
                echo "$ext" >> "$onboot_file"
                log "INFO" "Added $ext to onboot list"
            fi
        done
    fi
    
    log "INFO" "Persistence configuration completed"
}

# Setup autostart
setup_autostart() {
    log "INFO" "Setting up autostart configuration..."
    
    # Create desktop entry
    local desktop_dir="$HOME/.local/share/applications"
    mkdir -p "$desktop_dir"
    
    cat > "$desktop_dir/berke0s.desktop" << EOF
[Desktop Entry]
Name=BERKE0S Desktop Environment
Comment=Ultimate Desktop Environment for Tiny Core Linux
Exec=$BERKE0S_DIR/berke0s
Icon=$BERKE0S_DIR/themes/berke0s-icon.png
Type=Application
Categories=System;
StartupNotify=true
EOF
    
    # Create autostart script
    local autostart_dir="$HOME/.config/autostart"
    mkdir -p "$autostart_dir"
    
    cat > "$autostart_dir/berke0s.desktop" << EOF
[Desktop Entry]
Type=Application
Name=BERKE0S
Exec=$BERKE0S_DIR/berke0s
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOF
    
    # Tiny Core specific autostart
    if [ "$IS_TINY_CORE" = true ]; then
        # Add to bootlocal.sh
        local bootlocal="/opt/bootlocal.sh"
        if [ -f "$bootlocal" ]; then
            if ! grep -q "berke0s" "$bootlocal"; then
                echo "" >> "$bootlocal"
                echo "# BERKE0S Desktop Environment" >> "$bootlocal"
                echo "$BERKE0S_DIR/berke0s &" >> "$bootlocal"
                log "INFO" "Added BERKE0S to bootlocal.sh"
            fi
        fi
        
        # Create X session script
        cat > "$HOME/.xsession" << EOF
#!/bin/bash
# BERKE0S X Session
export DISPLAY=:0
$BERKE0S_DIR/berke0s
EOF
        chmod +x "$HOME/.xsession"
        
        # Create xinitrc
        cat > "$HOME/.xinitrc" << EOF
#!/bin/bash
# BERKE0S xinitrc
$BERKE0S_DIR/berke0s &
exec flwm
EOF
        chmod +x "$HOME/.xinitrc"
    fi
    
    log "INFO" "Autostart configuration completed"
}

# Create launcher script
create_launcher() {
    log "INFO" "Creating system launcher..."
    
    # Create system-wide launcher
    if [ "$IS_ROOT" = true ]; then
        cat > "/usr/local/bin/berke0s" << EOF
#!/bin/bash
# BERKE0S System Launcher
cd "$BERKE0S_DIR"
exec "$BERKE0S_DIR/berke0s" "\$@"
EOF
        chmod +x "/usr/local/bin/berke0s"
        log "INFO" "System launcher created: /usr/local/bin/berke0s"
    fi
    
    # Create user launcher
    local user_bin="$HOME/.local/bin"
    mkdir -p "$user_bin"
    
    cat > "$user_bin/berke0s" << EOF
#!/bin/bash
# BERKE0S User Launcher
cd "$BERKE0S_DIR"
exec "$BERKE0S_DIR/berke0s" "\$@"
EOF
    chmod +x "$user_bin/berke0s"
    
    # Add to PATH if not already there
    if [[ ":$PATH:" != *":$user_bin:"* ]]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
        log "INFO" "Added $user_bin to PATH"
    fi
    
    log "INFO" "User launcher created: $user_bin/berke0s"
}

# Install themes
install_themes() {
    if [ "$INSTALL_THEMES" != true ]; then
        return 0
    fi
    
    log "INFO" "Installing themes..."
    
    # Copy themes from installation
    if [ -d "$BERKE0S_DIR/themes" ]; then
        cp -r "$BERKE0S_DIR/themes/"* "$BERKE0S_USER_DIR/themes/" 2>/dev/null || true
    fi
    
    # Download additional wallpapers
    local wallpapers_url="https://raw.githubusercontent.com/BreDEVs/BERKE0S/main/wallpapers"
    local wallpapers=(
        "berke0s-default.png"
        "tinycore-classic.png"
        "abstract-blue.png"
        "nature-green.png"
    )
    
    for wallpaper in "${wallpapers[@]}"; do
        log "INFO" "Downloading wallpaper: $wallpaper"
        wget -q -O "$BERKE0S_USER_DIR/wallpapers/$wallpaper" "$wallpapers_url/$wallpaper" || true
    done
    
    log "INFO" "Themes installation completed"
}

# Run post-installation tests
run_tests() {
    log "INFO" "Running post-installation tests..."
    
    # Test Python imports
    log "INFO" "Testing Python imports..."
    if python3 -c "
import sys
import tkinter
import json
import os
import subprocess
import threading
print('✓ All required modules imported successfully')
"; then
        log "INFO" "Python imports test passed"
    else
        log "WARN" "Python imports test failed"
    fi
    
    # Test BERKE0S import
    if python3 -c "
import sys
sys.path.insert(0, '$BERKE0S_DIR')
try:
    import main
    print('✓ BERKE0S module imported successfully')
except Exception as e:
    print(f'✗ BERKE0S import failed: {e}')
"; then
        log "INFO" "BERKE0S import test passed"
    else
        log "WARN" "BERKE0S import test failed"
    fi
    
    # Test display configuration
    if [ -x "$BERKE0S_DIR/test_display.sh" ]; then
        log "INFO" "Running display test..."
        bash "$BERKE0S_DIR/test_display.sh" >> "$LOG_FILE" 2>&1
    fi
    
    log "INFO" "Post-installation tests completed"
}

# Cleanup temporary files
cleanup() {
    log "INFO" "Cleaning up temporary files..."
    
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        log "INFO" "Temporary directory cleaned up"
    fi
}

# Show completion message
show_completion() {
    clear
    echo -e "${GREEN}"
    echo "  ███████╗██╗   ██╗ ██████╗ ██████╗███████╗███████╗███████╗"
    echo "  ██╔════╝██║   ██║██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝"
    echo "  ███████╗██║   ██║██║     ██║     █████╗  ███████╗███████╗"
    echo "  ╚════██║██║   ██║██║     ██║     ██╔══╝  ╚════██║╚════██║"
    echo "  ███████║╚██████╔╝╚██████╗╚██████╗███████╗███████║███████║"
    echo "  ╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}🎉 BERKE0S V2 installation completed successfully! 🎉${NC}"
    echo ""
    echo -e "${YELLOW}Installation Summary:${NC}"
    echo -e "  Installation Directory: ${GREEN}$BERKE0S_DIR${NC}"
    echo -e "  Configuration Directory: ${GREEN}$BERKE0S_USER_DIR${NC}"
    echo -e "  Log File: ${GREEN}$LOG_FILE${NC}"
    echo ""
    echo -e "${YELLOW}Getting Started:${NC}"
    echo -e "  1. Start BERKE0S: ${GREEN}berke0s${NC}"
    echo -e "  2. Or run directly: ${GREEN}$BERKE0S_DIR/berke0s${NC}"
    echo -e "  3. For help: ${GREEN}berke0s --help${NC}"
    echo ""
    if [ "$IS_TINY_CORE" = true ]; then
        echo -e "${YELLOW}Tiny Core Linux:${NC}"
        echo -e "  • BERKE0S will start automatically on next boot"
        echo -e "  • To backup settings: ${GREEN}filetool.sh -b${NC}"
        echo -e "  • Configuration persisted in ~/.berke0s/"
        echo ""
    fi
    echo -e "${YELLOW}Features:${NC}"
    echo -e "  • Enhanced Display Management"
    echo -e "  • Advanced File Manager"
    echo -e "  • Integrated Applications"
    echo -e "  • Multiple Themes"
    echo -e "  • System Monitoring"
    echo -e "  • Plugin Support"
    echo ""
    echo -e "${BLUE}For documentation and support:${NC}"
    echo -e "  GitHub: ${GREEN}$GITHUB_REPO${NC}"
    echo -e "  Issues: ${GREEN}$GITHUB_REPO/issues${NC}"
    echo ""
    echo -e "${PURPLE}Thank you for choosing BERKE0S! 🚀${NC}"
    echo ""
}

# Handle interruption
trap 'echo -e "\n${RED}Installation interrupted by user${NC}"; cleanup; exit 1' INT TERM

# Main installation function
main() {
    # Initialize log file
    echo "BERKE0S Installation Log - $(date)" > "$LOG_FILE"
    
    show_banner
    
    # Run installation steps
    log "INFO" "Starting BERKE0S V2 installation..."
    
    detect_system
    check_prerequisites
    setup_directories
    download_berke0s
    install_files
    setup_display
    
    if [ "$IS_TINY_CORE" = true ] && [ "$CONFIGURE_PERSISTENCE" = true ]; then
        configure_persistence
    fi
    
    if [ "$SETUP_AUTOSTART" = true ]; then
        setup_autostart
    fi
    
    create_launcher
    install_themes
    run_tests
    cleanup
    
    show_completion
    
    # Ask to start BERKE0S
    echo -e "${YELLOW}Would you like to start BERKE0S now? [y/N]:${NC} "
    read -r start_now
    
    if [[ "$start_now" =~ ^[Yy]$ ]]; then
        log "INFO" "Starting BERKE0S..."
        cd "$BERKE0S_DIR"
        exec ./berke0s
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --no-extensions)
            INSTALL_EXTENSIONS=false
            shift
            ;;
        --no-autostart)
            SETUP_AUTOSTART=false
            shift
            ;;
        --no-persistence)
            CONFIGURE_PERSISTENCE=false
            shift
            ;;
        --no-themes)
            INSTALL_THEMES=false
            shift
            ;;
        --help)
            echo "BERKE0S Installation Script"
            echo ""
            echo "Options:"
            echo "  --no-extensions     Skip installing system extensions"
            echo "  --no-autostart      Skip autostart configuration"
            echo "  --no-persistence    Skip Tiny Core persistence setup"
            echo "  --no-themes         Skip theme installation"
            echo "  --help              Show this help message"
            echo ""
            exit 0
            ;;
        *)
            log "WARN" "Unknown option: $1"
            shift
            ;;
    esac
done

# Run main installation
main "$@"