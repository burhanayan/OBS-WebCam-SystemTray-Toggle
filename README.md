# OBS VirtualCam Tray Controller

🎥 **OBS VirtualCam Tray Controller** is a lightweight Windows system tray application that connects to OBS Studio via its WebSocket API. It allows you to:

✅ Monitor the visibility of a specific source (e.g., your webcam)  
✅ Toggle the source ON/OFF with a simple click on the tray icon  
✅ Automatically update the tray icon based on the webcam state  
✅ Exit cleanly from the tray menu

This tool is perfect for users who want to control their OBS VirtualCam behavior dynamically without opening OBS Studio every time.

---

## 🚀 Features

- 📡 Connects to OBS WebSocket (no password required)
- 🔄 Toggles a specified source visibility in a chosen scene
- 🎨 Dynamic tray icon reflecting webcam state (ON/OFF)
- 🖱️ Left-click to toggle webcam
- 📋 Right-click menu with “Exit” option
- 💪 Auto-reconnects if OBS restarts

---

## ⚙️ Requirements

- OBS Studio 28+ (WebSocket API built-in)
- Python 3.8+
- Dependencies:
  - `obs-websocket-py`
  - `pystray`
  - `Pillow`

---

## 🛠 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/obs-virtualcam-tray.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python tray_app.py
   ```

---

## 📷 Tray Icons

| State         | Icon   |
|---------------|--------|
| Camera ON     | 🟢     |
| Camera OFF    | 🔴     |

---

## 📜 License

MIT
