# Building OBS VirtualCam Tray Controller

This guide explains how to build executable files for distribution.

## Quick Build (Current Platform)

The easiest way to build for your current platform:

```bash
python build.py
```

This will create an executable in the `dist/` folder.

## Platform-Specific Builds

### Windows

```batch
build_windows.bat
```

Creates `dist/windows/OBS-VirtualCam-Tray-Controller.exe`

### macOS

```bash
./build_macos.sh
```

Creates `dist/macos/OBS VirtualCam Tray Controller.app`

### Linux

```bash
./build_linux.sh
```

Creates `dist/linux/obs-virtualcam-tray-controller`

## Requirements

- Python 3.8+
- All dependencies from `requirements.txt`
- PyInstaller (installed automatically by build scripts)

## Build Output

Each platform creates:
- Standalone executable (no Python required)
- README with platform-specific instructions
- All required assets bundled

## GitHub Actions

The project includes automated builds via GitHub Actions:

1. Push a tag starting with 'v' (e.g., `v1.0.0`)
2. GitHub Actions builds for all platforms
3. Creates a release with all executables

## Manual PyInstaller Build

If you prefer manual control:

```bash
pip install pyinstaller
pyinstaller obs-tray.spec --clean
```

## Troubleshooting

### Windows
- Ensure you're using Python from python.org (not Microsoft Store)
- Run as Administrator if permission errors occur

### macOS
- You may need to install Xcode Command Line Tools
- The app must be signed for distribution (or users must right-click → Open)

### Linux
- Install python3-tk if not present: `sudo apt-get install python3-tk`
- The executable requires a desktop environment with system tray support

## Distribution

After building, you can distribute:

### Windows
- Single `.exe` file
- No installation required
- Windows Defender may need exception

### macOS
- `.app` bundle
- Drag to Applications folder
- May require security approval on first run

### Linux
- Single executable file
- Can be placed in `/usr/local/bin` or run from anywhere
- Includes `.desktop` file for menu integration