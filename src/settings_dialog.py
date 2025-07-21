"""
Settings dialog for OBS VirtualCam Tray Controller.
Provides a GUI interface for editing application settings.
"""

import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Callable
from pathlib import Path

from .settings_manager import SettingsManager


class SettingsDialog:
    """Settings dialog window with editable configuration fields."""
    
    def __init__(self, settings_manager: SettingsManager, on_settings_changed: Optional[Callable] = None):
        """
        Initialize settings dialog.
        
        Args:
            settings_manager: Settings manager instance
            on_settings_changed: Callback when settings are changed
        """
        self.settings_manager = settings_manager
        self.on_settings_changed = on_settings_changed
        self.logger = logging.getLogger(__name__)
        
        # Dialog window
        self.root: Optional[tk.Tk] = None
        self.result = False  # True if settings were saved
        
        # Form variables
        self.vars = {}
        
    def show(self) -> bool:
        """
        Show the settings dialog.
        
        Returns:
            bool: True if settings were saved, False if cancelled
        """
        try:
            self._create_dialog()
            self._populate_fields()
            self._center_window()
            
            # Show dialog and wait for result
            self.root.wait_window()
            
            return self.result
            
        except Exception as e:
            self.logger.error(f"Error showing settings dialog: {e}")
            if self.root:
                self.root.destroy()
            return False
    
    def _create_dialog(self):
        """Create the dialog window and widgets."""
        self.root = tk.Tk()
        self.root.title("OBS Tray Controller - Settings")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # Make it a modal dialog
        self.root.transient()
        self.root.grab_set()
        
        # Create main frame with scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for organized settings
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Connection settings tab
        conn_frame = ttk.Frame(notebook)
        notebook.add(conn_frame, text="Connection")
        self._create_connection_tab(conn_frame)
        
        # OBS settings tab
        obs_frame = ttk.Frame(notebook)
        notebook.add(obs_frame, text="OBS Settings")
        self._create_obs_tab(obs_frame)
        
        # Application settings tab
        app_frame = ttk.Frame(notebook)
        notebook.add(app_frame, text="Application")
        self._create_app_tab(app_frame)
        
        # Appearance settings tab
        appearance_frame = ttk.Frame(notebook)
        notebook.add(appearance_frame, text="Appearance")
        self._create_appearance_tab(appearance_frame)
        
        # Hotkeys settings tab
        hotkeys_frame = ttk.Frame(notebook)
        notebook.add(hotkeys_frame, text="Hotkeys")
        self._create_hotkeys_tab(hotkeys_frame)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        ttk.Button(button_frame, text="Save", command=self._save_settings, width=15).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self._cancel, width=15).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset_defaults, width=15).pack(side=tk.LEFT)
        
        # File location info
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(info_frame, text=f"Settings file: {self.settings_manager.config_file}", 
                 font=('TkDefaultFont', 8), foreground='gray').pack()
    
    def _create_connection_tab(self, parent):
        """Create connection settings tab."""
        # OBS WebSocket section
        group = ttk.LabelFrame(parent, text="OBS WebSocket Connection", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # Host
        ttk.Label(group, text="Host:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.vars['obs_host'] = tk.StringVar()
        ttk.Entry(group, textvariable=self.vars['obs_host'], width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Port
        ttk.Label(group, text="Port:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.vars['obs_port'] = tk.StringVar()
        ttk.Entry(group, textvariable=self.vars['obs_port'], width=30).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Password
        ttk.Label(group, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.vars['obs_password'] = tk.StringVar()
        password_entry = ttk.Entry(group, textvariable=self.vars['obs_password'], show="*", width=30)
        password_entry.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Show password checkbox
        self.vars['show_password'] = tk.BooleanVar()
        show_cb = ttk.Checkbutton(group, text="Show password", variable=self.vars['show_password'],
                                 command=lambda: password_entry.configure(show="" if self.vars['show_password'].get() else "*"))
        show_cb.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Help text
        help_text = "Get the password from OBS → Tools → WebSocket Server Settings"
        ttk.Label(group, text=help_text, font=('TkDefaultFont', 8), foreground='gray').grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def _create_obs_tab(self, parent):
        """Create OBS settings tab."""
        # Scene and Source section
        group = ttk.LabelFrame(parent, text="Scene and Source Configuration", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # Scene name
        ttk.Label(group, text="Scene Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.vars['scene_name'] = tk.StringVar()
        ttk.Entry(group, textvariable=self.vars['scene_name'], width=30).grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Source name
        ttk.Label(group, text="Source Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.vars['source_name'] = tk.StringVar()
        ttk.Entry(group, textvariable=self.vars['source_name'], width=30).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        
        # Help text
        help_text = "These must match exactly with your OBS scene and source names"
        ttk.Label(group, text=help_text, font=('TkDefaultFont', 8), foreground='gray').grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Connection behavior section
        conn_group = ttk.LabelFrame(parent, text="Connection Behavior", padding=10)
        conn_group.pack(fill=tk.X, padx=10, pady=5)
        
        # Auto connect
        self.vars['auto_connect'] = tk.BooleanVar()
        ttk.Checkbutton(conn_group, text="Connect to OBS automatically on startup", 
                       variable=self.vars['auto_connect']).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Reconnect delay
        ttk.Label(conn_group, text="Reconnect Delay (seconds):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.vars['reconnect_delay'] = tk.StringVar()
        ttk.Entry(conn_group, textvariable=self.vars['reconnect_delay'], width=10).grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
    
    def _create_app_tab(self, parent):
        """Create application settings tab."""
        # Application behavior
        group = ttk.LabelFrame(parent, text="Application Behavior", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # Start minimized
        self.vars['start_minimized'] = tk.BooleanVar()
        ttk.Checkbutton(group, text="Start minimized to system tray", 
                       variable=self.vars['start_minimized']).grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Settings file section
        file_group = ttk.LabelFrame(parent, text="Settings File", padding=10)
        file_group.pack(fill=tk.X, padx=10, pady=5)
        
        # Current file location
        file_location = str(self.settings_manager.config_file)
        ttk.Label(file_group, text="Current location:", font=('TkDefaultFont', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=2)
        location_label = ttk.Label(file_group, text=file_location, font=('TkDefaultFont', 8), foreground='blue')
        location_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Buttons for file operations
        button_frame = ttk.Frame(file_group)
        button_frame.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
        
        ttk.Button(button_frame, text="Open Settings Folder", command=self._open_settings_folder, width=20).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Export Settings", command=self._export_settings, width=20).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Import Settings", command=self._import_settings, width=20).pack(side=tk.LEFT)
    
    def _create_appearance_tab(self, parent):
        """Create appearance settings tab."""
        # Icon colors section
        group = ttk.LabelFrame(parent, text="Tray Icon Colors", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # Camera on color
        ttk.Label(group, text="Camera ON Color:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.vars['camera_on_color'] = tk.StringVar()
        color_frame1 = ttk.Frame(group)
        color_frame1.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        ttk.Entry(color_frame1, textvariable=self.vars['camera_on_color'], width=10).pack(side=tk.LEFT)
        ttk.Button(color_frame1, text="Choose", command=lambda: self._choose_color('camera_on_color'), width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Camera off color
        ttk.Label(group, text="Camera OFF Color:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.vars['camera_off_color'] = tk.StringVar()
        color_frame2 = ttk.Frame(group)
        color_frame2.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        ttk.Entry(color_frame2, textvariable=self.vars['camera_off_color'], width=10).pack(side=tk.LEFT)
        ttk.Button(color_frame2, text="Choose", command=lambda: self._choose_color('camera_off_color'), width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Color help
        help_text = "Use hex color codes (e.g., #4CAF50 for green, #F44336 for red)"
        ttk.Label(group, text=help_text, font=('TkDefaultFont', 8), foreground='gray').grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
    
    def _create_hotkeys_tab(self, parent):
        """Create hotkeys settings tab."""
        # Enable hotkeys section
        group = ttk.LabelFrame(parent, text="Global Keyboard Shortcuts", padding=10)
        group.pack(fill=tk.X, padx=10, pady=5)
        
        # Enable hotkeys checkbox
        self.vars['enable_hotkeys'] = tk.BooleanVar()
        ttk.Checkbutton(group, text="Enable global hotkeys", variable=self.vars['enable_hotkeys']).pack(anchor=tk.W, pady=2)
        
        # Help text
        help_text = "When enabled, these keyboard shortcuts work globally (even when OBS Tray Controller is not focused)"
        ttk.Label(group, text=help_text, font=('TkDefaultFont', 8), foreground='gray').pack(anchor=tk.W, pady=(2, 8))
        
        # Hotkey settings
        hotkey_frame = ttk.Frame(group)
        hotkey_frame.pack(fill=tk.X, pady=5)
        
        # Webcam ON hotkey
        ttk.Label(hotkey_frame, text="Turn Webcam ON:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.vars['hotkey_webcam_on'] = tk.StringVar()
        on_frame = ttk.Frame(hotkey_frame)
        on_frame.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        self.hotkey_on_entry = ttk.Entry(on_frame, textvariable=self.vars['hotkey_webcam_on'], width=20)
        self.hotkey_on_entry.pack(side=tk.LEFT)
        ttk.Button(on_frame, text="Record", command=lambda: self._record_hotkey('hotkey_webcam_on'), width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Webcam OFF hotkey  
        ttk.Label(hotkey_frame, text="Turn Webcam OFF:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.vars['hotkey_webcam_off'] = tk.StringVar()
        off_frame = ttk.Frame(hotkey_frame)
        off_frame.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=2)
        self.hotkey_off_entry = ttk.Entry(off_frame, textvariable=self.vars['hotkey_webcam_off'], width=20)
        self.hotkey_off_entry.pack(side=tk.LEFT)
        ttk.Button(off_frame, text="Record", command=lambda: self._record_hotkey('hotkey_webcam_off'), width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Hotkey format help
        format_help = "Format: <ctrl>+<alt>+1 or <ctrl>+<shift>+f1\nSupported keys: ctrl, alt, shift, win, a-z, 0-9, f1-f12"
        ttk.Label(group, text=format_help, font=('TkDefaultFont', 8), foreground='gray').pack(anchor=tk.W, pady=(8, 0))
    
    def _populate_fields(self):
        """Populate form fields with current settings."""
        settings = self.settings_manager.settings
        
        # Populate all fields
        self.vars['obs_host'].set(settings.obs_host)
        self.vars['obs_port'].set(str(settings.obs_port))
        self.vars['obs_password'].set(settings.obs_password or "")
        self.vars['scene_name'].set(settings.scene_name)
        self.vars['source_name'].set(settings.source_name)
        self.vars['reconnect_delay'].set(str(settings.reconnect_delay))
        self.vars['auto_connect'].set(settings.auto_connect)
        self.vars['start_minimized'].set(settings.start_minimized)
        self.vars['camera_on_color'].set(settings.camera_on_color)
        self.vars['camera_off_color'].set(settings.camera_off_color)
        self.vars['enable_hotkeys'].set(settings.enable_hotkeys)
        self.vars['hotkey_webcam_on'].set(settings.hotkey_webcam_on)
        self.vars['hotkey_webcam_off'].set(settings.hotkey_webcam_off)
    
    def _center_window(self):
        """Center the dialog window on screen."""
        if self.root:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _choose_color(self, var_name: str):
        """Open color chooser dialog."""
        try:
            from tkinter import colorchooser
            current_color = self.vars[var_name].get()
            color = colorchooser.askcolor(color=current_color, title="Choose Color")
            if color[1]:  # color[1] is the hex value
                self.vars[var_name].set(color[1])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open color chooser: {e}")
    
    def _validate_settings(self) -> bool:
        """Validate all settings before saving."""
        try:
            # Validate port
            port = int(self.vars['obs_port'].get())
            if not (1 <= port <= 65535):
                messagebox.showerror("Validation Error", "Port must be between 1 and 65535")
                return False
            
            # Validate reconnect delay
            delay = float(self.vars['reconnect_delay'].get())
            if delay < 0:
                messagebox.showerror("Validation Error", "Reconnect delay cannot be negative")
                return False
            
            # Validate required fields
            if not self.vars['obs_host'].get().strip():
                messagebox.showerror("Validation Error", "Host cannot be empty")
                return False
            
            if not self.vars['scene_name'].get().strip():
                messagebox.showerror("Validation Error", "Scene name cannot be empty")
                return False
            
            if not self.vars['source_name'].get().strip():
                messagebox.showerror("Validation Error", "Source name cannot be empty")
                return False
            
            # Validate color codes
            for color_var in ['camera_on_color', 'camera_off_color']:
                color = self.vars[color_var].get().strip()
                if color and not (color.startswith('#') and len(color) == 7):
                    messagebox.showerror("Validation Error", f"Invalid color format for {color_var.replace('_', ' ').title()}")
                    return False
            
            # Validate hotkeys if enabled
            if self.vars['enable_hotkeys'].get():
                from .hotkey_handler import HotkeyHandler
                hotkey_handler = HotkeyHandler(self.settings_manager)
                
                hotkey_on = self.vars['hotkey_webcam_on'].get().strip()
                hotkey_off = self.vars['hotkey_webcam_off'].get().strip()
                
                if hotkey_on and not hotkey_handler.is_hotkey_valid(hotkey_on):
                    messagebox.showerror("Validation Error", f"Invalid hotkey format for webcam ON: {hotkey_on}")
                    return False
                
                if hotkey_off and not hotkey_handler.is_hotkey_valid(hotkey_off):
                    messagebox.showerror("Validation Error", f"Invalid hotkey format for webcam OFF: {hotkey_off}")
                    return False
                
                if hotkey_on and hotkey_off and hotkey_on == hotkey_off:
                    messagebox.showerror("Validation Error", "Webcam ON and OFF hotkeys cannot be the same")
                    return False
            
            return True
            
        except ValueError as e:
            messagebox.showerror("Validation Error", f"Invalid numeric value: {e}")
            return False
    
    def _save_settings(self):
        """Save settings and close dialog."""
        if not self._validate_settings():
            return
        
        try:
            # Update settings
            password = self.vars['obs_password'].get().strip()
            self.settings_manager.update_settings(
                obs_host=self.vars['obs_host'].get().strip(),
                obs_port=int(self.vars['obs_port'].get()),
                obs_password=password if password else None,
                scene_name=self.vars['scene_name'].get().strip(),
                source_name=self.vars['source_name'].get().strip(),
                reconnect_delay=float(self.vars['reconnect_delay'].get()),
                auto_connect=self.vars['auto_connect'].get(),
                start_minimized=self.vars['start_minimized'].get(),
                camera_on_color=self.vars['camera_on_color'].get().strip(),
                camera_off_color=self.vars['camera_off_color'].get().strip(),
                enable_hotkeys=self.vars['enable_hotkeys'].get(),
                hotkey_webcam_on=self.vars['hotkey_webcam_on'].get().strip(),
                hotkey_webcam_off=self.vars['hotkey_webcam_off'].get().strip()
            )
            
            self.result = True
            messagebox.showinfo("Success", "Settings saved successfully!")
            
            # Notify callback
            if self.on_settings_changed:
                self.on_settings_changed()
            
            self.root.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def _cancel(self):
        """Cancel and close dialog."""
        self.result = False
        self.root.destroy()
    
    def _reset_defaults(self):
        """Reset all settings to defaults."""
        if messagebox.askyesno("Reset Settings", "Reset all settings to default values?"):
            try:
                self.settings_manager.reset_to_defaults()
                self._populate_fields()  # Refresh form with defaults
                messagebox.showinfo("Success", "Settings reset to defaults!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reset settings: {e}")
    
    def _open_settings_folder(self):
        """Open the settings folder in file explorer."""
        try:
            import subprocess
            import platform
            
            folder_path = self.settings_manager.config_dir
            
            if platform.system() == "Windows":
                subprocess.Popen(['explorer', str(folder_path)])
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', str(folder_path)])
            else:  # Linux
                subprocess.Popen(['xdg-open', str(folder_path)])
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open settings folder: {e}")
    
    def _export_settings(self):
        """Export settings to a file."""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Settings",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                if self.settings_manager.export_settings(Path(filename)):
                    messagebox.showinfo("Success", f"Settings exported to {filename}")
                else:
                    messagebox.showerror("Error", "Failed to export settings")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def _import_settings(self):
        """Import settings from a file."""
        try:
            filename = filedialog.askopenfilename(
                title="Import Settings",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if filename:
                if messagebox.askyesno("Import Settings", "This will overwrite current settings. Continue?"):
                    if self.settings_manager.import_settings(Path(filename)):
                        self._populate_fields()  # Refresh form with imported settings
                        messagebox.showinfo("Success", f"Settings imported from {filename}")
                    else:
                        messagebox.showerror("Error", "Failed to import settings")
        except Exception as e:
            messagebox.showerror("Error", f"Import failed: {e}")
    
    def _record_hotkey(self, var_name: str):
        """Record a hotkey by capturing user input."""
        try:
            # Show recording dialog
            self._show_hotkey_recording_dialog(var_name)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record hotkey: {e}")
    
    def _show_hotkey_recording_dialog(self, var_name: str):
        """Show dialog to record a hotkey."""
        # Create recording dialog
        recording_window = tk.Toplevel(self.root)
        recording_window.title("Record Hotkey")
        recording_window.geometry("400x200")
        recording_window.transient(self.root)
        recording_window.grab_set()
        
        # Center the recording window
        recording_window.update_idletasks()
        x = (recording_window.winfo_screenwidth() // 2) - 200
        y = (recording_window.winfo_screenheight() // 2) - 100
        recording_window.geometry(f"400x200+{x}+{y}")
        
        # Instructions
        instruction_text = f"Recording hotkey for: {var_name.replace('hotkey_', '').replace('_', ' ').title()}"
        ttk.Label(recording_window, text=instruction_text, font=('TkDefaultFont', 10, 'bold')).pack(pady=10)
        ttk.Label(recording_window, text="Press the desired key combination:", font=('TkDefaultFont', 9)).pack(pady=5)
        
        # Current keys display
        keys_var = tk.StringVar()
        keys_var.set("Waiting for input...")
        keys_label = ttk.Label(recording_window, textvariable=keys_var, font=('TkDefaultFont', 12, 'bold'), foreground='blue')
        keys_label.pack(pady=10)
        
        # Buttons
        button_frame = ttk.Frame(recording_window)
        button_frame.pack(pady=20)
        
        recorded_hotkey = ""
        
        def on_key_press(event):
            nonlocal recorded_hotkey
            
            # Build hotkey string
            modifiers = []
            if event.state & 0x4:  # Control
                modifiers.append("<ctrl>")
            if event.state & 0x8:  # Alt
                modifiers.append("<alt>")
            if event.state & 0x1:  # Shift
                modifiers.append("<shift>")
            if event.state & 0x40000:  # Windows key (varies by system)
                modifiers.append("<win>")
            
            # Get the key
            key = event.keysym.lower()
            
            # Special key mappings
            key_mappings = {
                'control_l': 'ctrl', 'control_r': 'ctrl',
                'alt_l': 'alt', 'alt_r': 'alt',
                'shift_l': 'shift', 'shift_r': 'shift',
                'super_l': 'win', 'super_r': 'win',
                'return': 'enter', 'backspace': 'backspace',
                'delete': 'delete', 'escape': 'escape',
                'tab': 'tab', 'space': 'space'
            }
            
            if key in key_mappings:
                key = key_mappings[key]
            elif key.startswith('f') and key[1:].isdigit():
                # Function keys
                pass
            elif len(key) == 1 and (key.isalnum()):
                # Regular alphanumeric keys
                pass
            elif key in ['up', 'down', 'left', 'right', 'home', 'end', 'pageup', 'pagedown', 'insert']:
                # Arrow and navigation keys
                pass
            else:
                # Skip modifier-only presses
                if key in ['ctrl', 'alt', 'shift', 'win']:
                    return
            
            # Only proceed if we have modifiers and a non-modifier key
            if modifiers and key not in ['ctrl', 'alt', 'shift', 'win']:
                if len(key) == 1:
                    recorded_hotkey = "+".join(modifiers + [key])
                else:
                    recorded_hotkey = "+".join(modifiers + [f"<{key}>"])
                keys_var.set(recorded_hotkey)
        
        def save_hotkey():
            if recorded_hotkey:
                self.vars[var_name].set(recorded_hotkey)
                recording_window.destroy()
            else:
                messagebox.showwarning("No Hotkey", "Please press a key combination first")
        
        def cancel_recording():
            recording_window.destroy()
        
        # Bind key events
        recording_window.bind('<KeyPress>', on_key_press)
        recording_window.focus_set()
        
        # Buttons
        ttk.Button(button_frame, text="Save", command=save_hotkey).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=lambda: self.vars[var_name].set("")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_recording).pack(side=tk.LEFT, padx=5)
        
        # Instructions at bottom
        ttk.Label(recording_window, text="Note: Use Ctrl, Alt, Shift with other keys", font=('TkDefaultFont', 8), foreground='gray').pack(pady=(10, 0)) 