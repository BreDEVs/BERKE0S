# BERKE0S Ultimate Desktop Environment V2

🚀 **Advanced Desktop Environment for Tiny Core Linux with Enhanced Display Management**

## Features

### Core Features
- **Enhanced Display Management System** - Advanced X server detection and configuration
- **Comprehensive Window Manager** - Multi-desktop support with modern UI
- **Advanced File Manager** - Full-featured file operations with previews
- **Integrated Applications** - Text editor, calculator, image viewer, and more
- **Plugin System** - Extensible architecture for custom applications
- **Theme Support** - Multiple built-in themes with customization options
- **Notification System** - Rich notifications with actions and history
- **System Monitoring** - Real-time performance and resource monitoring

### Display Management V2
- **Automatic Display Detection** - Intelligent X server configuration
- **Tiny Core Linux Optimization** - Specialized support for TC Linux
- **Multiple Display Methods** - X11, Xvfb, nested X support
- **Robust Fallback System** - Headless mode when display unavailable
- **Advanced Troubleshooting** - Built-in diagnostic tools
- **Configuration Management** - Easy display settings management

## Installation

### Quick Install (Recommended)
```bash
curl -fsSL https://raw.githubusercontent.com/BreDEVs/BERKE0S/main/install.sh | bash
```

### Manual Installation
1. Download the installer:
```bash
wget https://raw.githubusercontent.com/BreDEVs/BERKE0S/main/install.sh
chmod +x install.sh
```

2. Run the installer:
```bash
./install.sh
```

### Tiny Core Linux Integration
For automatic startup, the installer will:
- Add BERKE0S to bootlocal.sh
- Configure X server settings
- Set up persistent storage
- Install required extensions

## Usage

### Starting BERKE0S
```bash
python3 /opt/berke0s/main.py
```

### Command Line Options
- `--install` - Force installation wizard
- `--headless` - Start in headless mode
- `--debug` - Enable debug logging
- `--display-info` - Show display information

### Configuration
Configuration files are stored in `~/.berke0s/`:
- `config.json` - Main configuration
- `themes/` - Custom themes
- `plugins/` - User plugins
- `applications/` - Application data

## Applications

### Built-in Applications
- **File Manager** - Advanced file operations with sidebar and multiple views
- **Text Editor** - Syntax highlighting, find/replace, multiple themes
- **Calculator** - Scientific calculator with history and memory functions
- **Image Viewer** - Support for multiple image formats with zoom
- **Music Player** - Audio playback with playlist support
- **Web Browser** - Basic web browsing capabilities
- **Terminal** - Integrated terminal emulator
- **System Monitor** - Resource usage and process management
- **Display Settings** - Advanced display configuration (V2 Feature)

### System Tools
- **Settings Manager** - System-wide configuration
- **Network Manager** - WiFi and network configuration
- **Archive Manager** - Compression and extraction tools
- **Screen Recorder** - Desktop recording capabilities
- **Backup Manager** - System backup and restore

## Themes

### Built-in Themes
- **Berke Dark V2** - Modern dark theme (default)
- **Berke Light V2** - Clean light theme
- **Ocean Blue V2** - Blue gradient theme
- **Forest Green V2** - Nature-inspired theme
- **Tiny Core Classic** - TC Linux traditional look

### Custom Themes
Create custom themes by adding JSON files to `~/.berke0s/themes/`:
```json
{
  "name": "My Theme",
  "version": "1.0",
  "colors": {
    "bg": "#1a1a1a",
    "fg": "#ffffff",
    "accent": "#00ff88"
  }
}
```

## Development

### Requirements
- Python 3.6+
- Tkinter (python3-tk)
- PIL/Pillow (recommended)
- psutil (recommended)
- X server (Xorg or compatible)

### Project Structure
```
berke0s/
├── src/
│   ├── core/           # Core system components
│   ├── display/        # Display management
│   ├── applications/   # Built-in applications
│   ├── ui/            # User interface components
│   └── utils/         # Utility functions
├── themes/            # Theme definitions
├── plugins/           # Plugin system
├── scripts/           # Installation and utility scripts
└── docs/              # Documentation
```

### Building from Source
1. Clone the repository:
```bash
git clone https://github.com/BreDEVs/BERKE0S.git
cd BERKE0S
```

2. Install dependencies:
```bash
./scripts/install-deps.sh
```

3. Run BERKE0S:
```bash
python3 main.py
```

## Tiny Core Linux Specific

### Extensions Required
The installer will automatically install:
- python3.tcz
- python3-tkinter.tcz
- Xorg-7.7.tcz (if not present)
- flwm.tcz (window manager)

### Persistence
For persistence across reboots:
1. Add to backup: `echo "opt/berke0s" >> /opt/.filetool.lst`
2. Add to onboot: `echo "berke0s.tcz" >> /mnt/sda1/tce/onboot.lst`

### Performance Tips
- Use RAM-based operation for better performance
- Configure backup for configuration persistence
- Use TCE directory for extension storage

## Support

### Troubleshooting
1. **Display Issues**: Run with `--debug` flag and check logs
2. **Performance**: Monitor system resources in System Monitor
3. **Installation**: Use the built-in installation wizard

### Logs
- Main log: `~/.berke0s/berke0s.log`
- Display log: `~/.berke0s/display.log`
- Installation log: `/tmp/berke0s_install.log`

### Community
- GitHub Issues: Report bugs and feature requests
- Documentation: See docs/ directory
- Examples: Check examples/ directory

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on Tiny Core Linux
5. Submit a pull request

## Changelog

### V2.0 (Current)
- Enhanced display management system
- Improved Tiny Core Linux support
- Advanced troubleshooting tools
- Better error handling and logging
- New display settings application
- Robust fallback systems

### V1.0
- Initial release
- Basic desktop environment
- Core applications
- Theme system