# OBS VirtualCam Tray Controller

🎥 **OBS VirtualCam Tray Controller** is a lightweight cross-platform system tray application that connects to OBS Studio via its WebSocket API. It allows you to:

✅ Monitor the visibility of a specific source (e.g., your webcam)  
✅ Toggle the source ON/OFF with a simple click on the tray icon  
✅ Automatically update the tray icon based on the webcam state  
✅ Exit cleanly from the tray menu  
✅ Auto-reconnect when OBS restarts or connection drops

This tool is perfect for users who want to control their OBS source visibility dynamically without opening OBS Studio every time.

---

## 🚀 Features

- 📡 Connects to OBS WebSocket (localhost:4455, password supported)
- 🔄 Toggles a specified source visibility in a chosen scene
- 🎨 Dynamic tray icon with custom camera graphics reflecting webcam state
- 🖱️ Intuitive menu system with connect/disconnect and webcam controls
- ⌨️ **Global keyboard shortcuts** for webcam control (configurable)
- ⚙️ **Editable settings dialog** with tabbed interface and validation
- 💪 Auto-reconnects gracefully if OBS restarts (optional)
- 🧵 Multi-threaded design with proper error handling
- 🎯 Professional code structure with modular design
- 🎨 Customizable tray icon colors

---

## ⚙️ Requirements

- OBS Studio 28+ (WebSocket API built-in)
- Python 3.8+
- Operating System: Windows, macOS, or Linux
- Dependencies (automatically installed):
  - `obsws-python==1.7.0` (OBS WebSocket 5.x support)
  - `pystray==0.19.5` (System tray integration)
  - `Pillow==10.1.0` (Icon generation)
  - `pynput==1.7.6` (Global hotkey support)

---

## 🛠 Installation & Setup

### Quick Start

1. **Clone this repository:**
   ```bash
   git clone https://github.com/your-username/OBS-WebCam-SystemTray-Toggle.git
   cd OBS-WebCam-SystemTray-Toggle
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure OBS Studio:**
   - Open OBS Studio
   - Go to Tools → WebSocket Server Settings
   - Enable WebSocket server
   - Set Server Port to `4455` (default)
   - **Authentication is enabled by default in WebSocket 5.x**
   - Copy the generated password or create your own
   - Click "Apply" and "OK"

4. **Configure the application:**
   - **First run**: The application will create a settings file automatically
   - **Set your WebSocket password**: Use the Settings menu in the tray app, or edit the settings file directly
   - Ensure you have a scene named `"ZoomInWebCam"`
   - Ensure you have a source named `"Video Capture Device 2"` in that scene
   - (Settings can be modified through the tray menu or by editing the JSON settings file)

5. **Run the application:**
   ```bash
   # Direct run
   python main.py
   
   # OR use the convenient run scripts from the scripts folder:
   cd scripts
   python run.py    # Cross-platform Python wrapper
   ./run.sh         # Unix/Linux/macOS
   run.bat          # Windows
   ```
   
   **Note**: The application will **NOT** connect to OBS automatically on first run. Use the tray menu to connect manually.

### Alternative Installation (System-wide)

```bash
# Install the package
pip install -e .

# Run from anywhere
obs-tray
```

---

## 📁 Project Structure

```
OBS-WebCam-SystemTray-Toggle/
├── src/                     # Main application source code
│   ├── __init__.py          # Package initialization
│   ├── settings_manager.py  # Persistent settings management
│   ├── obs_client.py        # OBS WebSocket client (5.x support)
│   ├── tray_handler.py      # System tray interface with menus
│   ├── hotkey_handler.py    # Global keyboard shortcuts
│   └── settings_dialog.py   # GUI settings configuration
├── scripts/                 # Build and run scripts
│   ├── build_windows.bat    # Windows build script
│   ├── build_linux.sh       # Linux build script
│   ├── build_macos.sh       # macOS build script
│   ├── build.py             # Python build script
│   ├── run.bat              # Windows run script
│   ├── run.sh               # Unix/Linux run script
│   └── run.py               # Python run wrapper
├── tests/                   # Test scripts
│   ├── test_connection.py   # OBS connection diagnostics
│   └── test_hotkeys.py      # Hotkey testing utility
├── config/                  # Configuration files
│   ├── obs-tray.spec        # PyInstaller specification
│   └── requirements-build.txt # Build dependencies
├── docs/                    # Additional documentation
│   └── BUILD.md             # Build instructions
├── assets/                  # Static tray icons
│   ├── OBS-WebCam-Tray-Logo_Disconnected.png
│   ├── OBS-WebCam-Tray-Logo_Webcam_Turned_Off.png
│   └── OBS-WebCam-Tray-Logo_Webcam_Turned_On.png
├── .github/                 # GitHub specific files
│   └── workflows/
│       └── build-release.yml # Automated build workflow
├── main.py                  # Main application entry point
├── setup.py                 # Package installation
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── CLAUDE.md                # AI assistant guidance
└── .gitignore               # Git ignore rules
```

---

## ⚙️ Configuration

The application uses **persistent JSON settings** stored in platform-appropriate locations:

- **Windows**: `%APPDATA%\OBSTrayController\settings.json`
- **Linux**: `~/.config/obs-tray-controller/settings.json`  
- **macOS**: `~/.obs-tray-controller/settings.json`

### Settings Options:

```json
{
  "obs_host": "localhost",
  "obs_port": 4455,
  "obs_password": "your_websocket_password",
  "scene_name": "ZoomInWebCam",
  "source_name": "Video Capture Device 2",
  "reconnect_delay": 3.0,
  "auto_connect": false,
  "start_minimized": true,
  "camera_on_color": "#4CAF50",
  "camera_off_color": "#F44336"
}
```

### How to Configure:

1. **Via Tray Menu**: Right-click the tray icon → Settings
2. **Direct File Edit**: Edit the JSON settings file directly
3. **First Run**: Application creates default settings automatically

---

## 📷 Tray Icons

The application uses custom-designed tray icons for different states:

| State         | Icon File | Description |
|---------------|-----------|-------------|
| **Disconnected** | `OBS-WebCam-Tray-Logo_Disconnected.png` | Gray webcam with slash - Not connected to OBS |
| **Camera OFF** | `OBS-WebCam-Tray-Logo_Webcam_Turned_Off.png` | Red indicator - Connected but webcam is hidden |
| **Camera ON** | `OBS-WebCam-Tray-Logo_Webcam_Turned_On.png` | Green indicator - Connected and webcam is visible |

Icons update automatically based on connection and webcam state!

## ⌨️ Global Keyboard Shortcuts

**NEW FEATURE:** Control your webcam from anywhere using global hotkeys!

### Default Shortcuts:
- **Turn Webcam ON**: `Ctrl + Alt + 1`
- **Turn Webcam OFF**: `Ctrl + Alt + 2`

### How to Configure:
1. Right-click the tray icon → **Settings**
2. Go to the **Hotkeys** tab
3. Enable/disable global hotkeys
4. Click **Record** to set custom shortcuts
5. Test different combinations like `Ctrl + Shift + F1`

### Features:
- ✅ Work system-wide (even when app is minimized)
- ✅ Customizable key combinations  
- ✅ Visual recording interface
- ✅ Validation to prevent conflicts
- ✅ Enable/disable as needed

---

## 🎯 Usage

1. **Start the application** 
2. **The tray icon appears** in your system tray (initially disconnected)
3. **Left-click** the tray icon to show the **main menu**:
   - **Connect to OBS** / **Disconnect from OBS**
   - **Turn On Webcam** / **Turn Off Webcam** (enabled/disabled based on state)
   - **Refresh State** to update webcam status
4. **Right-click** the tray icon for **settings menu**:
   - **Settings** - view/edit configuration
   - **Test Connection** - run connection diagnostics
   - **About** - application information
5. **The icon color changes** based on camera state:
   - **Green camera** = Connected & Camera is ON
   - **Red camera** = Connected & Camera is OFF  
   - **Gray camera with X** = Disconnected from OBS

### Key Features:
- **Manual Connection**: You control when to connect/disconnect
- **Smart Menus**: Buttons automatically enable/disable based on state
- **Visual Feedback**: Clear status indicators in menus and icons
- **Persistent Settings**: Configuration survives restarts
- **Global Hotkeys**: Press keyboard shortcuts from anywhere to control webcam

---

## 🔧 Troubleshooting

### Connection Issues

- **Ensure OBS WebSocket is enabled** (Tools → WebSocket Server Settings)
- **Check the port** is 4455 (OBS WebSocket 5.x default)
- **Set the correct password** in the settings (authentication required in 5.x)
- **Verify scene and source names** in the settings file or via tray menu
- **Make sure you're using OBS Studio 28+** with WebSocket 5.x

### Common Problems

1. **"Failed to connect to OBS" or "status" errors**
   - Make sure OBS Studio is running with WebSocket 5.x support
   - Copy the WebSocket password from OBS settings to the application settings
   - Use the tray menu "Settings" or edit the JSON settings file
   - Run `python test_connection.py` to diagnose connection issues

2. **"Error checking source visibility"**
   - Verify the scene name "ZoomInWebCam" exists
   - Verify the source name "Video Capture Device 2" exists in that scene
   - Note: In WebSocket 5.x, sources are sometimes referred to as "inputs"

3. **"Unexpected error connecting to OBS: 'status'"**
   - This usually indicates a WebSocket protocol version mismatch
   - Update dependencies: `pip install -r requirements.txt`
   - Ensure you're using the correct obs-websocket version (5.x)

4. **Tray icon doesn't appear**
   - On Linux, ensure you have a system tray (like in GNOME Shell extensions)
   - Try running with `python -v main.py` to see detailed errors

5. **Library compatibility issues**
   - We've updated to use `simpleobsws` which supports WebSocket 5.x
   - If you need 4.x support, you may need to install OBS WebSocket 4.x compatibility plugin

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📜 License

MIT
