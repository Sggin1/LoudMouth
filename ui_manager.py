# v3_PTT/ui_manager.py  
# Clean Tkinter GUI for PTT application
# Purpose: Minimal, responsive UI for voice-to-text
# Dependencies: tkinter

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class UIManager:
    """Manages the main UI window and user interactions"""
    
    def __init__(self, 
                 on_start_recording: Optional[Callable] = None,
                 on_stop_recording: Optional[Callable] = None,
                 on_open_settings: Optional[Callable] = None,
                 on_mic_mute_toggle: Optional[Callable] = None):
        self.on_start_recording = on_start_recording
        self.on_stop_recording = on_stop_recording
        self.on_open_settings = on_open_settings
        self.on_mic_mute_toggle = on_mic_mute_toggle
        
        self.root = tk.Tk()
        self.is_recording = False
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.is_minimized = False
        self.normal_geometry = None
        self.normal_widgets = []
        
        # UI variables
        self.status_var = tk.StringVar(value="Ready")
        self.hotkey_var = tk.StringVar(value="Space")
        self.mic_mute_callback = None
        
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self):
        """Configure main window properties"""
        self.root.title("v3 PTT")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a1a')
        
        # Calculate center position immediately
        width, height = 250, 300
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        # Set geometry with position in one call - prevents wrong positioning
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configure window properties
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        
        # Make window draggable
        self.root.bind('<Button-1>', self._start_drag)
        self.root.bind('<B1-Motion>', self._drag_window)
    
    def _center_window(self):
        """Center window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg='#1a1a1a', relief='raised', bd=1)
        self.main_frame.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Create sections
        self._create_header(self.main_frame)
        self._create_status_section(self.main_frame)
        self._create_control_section(self.main_frame)
        self._create_transcript_section(self.main_frame)
        self._create_settings_section(self.main_frame)
    
    def _create_header(self, parent):
        """Create header with title and window controls"""
        self.header_frame = tk.Frame(parent, bg='#2d2d2d', height=30)
        self.header_frame.pack(fill='x', padx=2, pady=2)
        self.header_frame.pack_propagate(False)
        
        # Title
        self.title_label = tk.Label(self.header_frame, text="🎤 v3 PTT", 
                              fg='white', bg='#2d2d2d', 
                              font=('Arial', 9, 'bold'))
        self.title_label.pack(side='left', padx=5, pady=5)
        
        # Window controls
        self.controls_frame = tk.Frame(self.header_frame, bg='#2d2d2d')
        self.controls_frame.pack(side='right', padx=5)
        
        self.minimize_btn = tk.Button(self.controls_frame, text="−", 
                               fg='white', bg='#404040',
                               command=self._minimize_window, 
                               relief='flat', width=2, font=('Arial', 8))
        self.minimize_btn.pack(side='left', padx=1)
        
        self.close_btn = tk.Button(self.controls_frame, text="×", 
                            fg='white', bg='#d63384',
                            command=self.root.quit, 
                            relief='flat', width=2, font=('Arial', 8))
        self.close_btn.pack(side='left', padx=1)
    
    def _create_status_section(self, parent):
        """Create status display section"""
        self.status_frame = tk.Frame(parent, bg='#2d2d2d', relief='sunken', bd=1)
        self.status_frame.pack(fill='x', padx=5, pady=2)
        
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var,
                                   fg='#00ff00', bg='#2d2d2d', 
                                   font=('Arial', 9))
        self.status_label.pack(pady=5)
    
    def _create_control_section(self, parent):
        """Create control buttons section"""
        self.control_frame = tk.Frame(parent, bg='#1a1a1a')
        self.control_frame.pack(fill='x', padx=5, pady=5)
        
        # Manual control button
        self.talk_button = tk.Button(self.control_frame, text="Hold to Talk",
                                   fg='white', bg='#0066cc', 
                                   font=('Arial', 9), relief='raised', bd=2)
        self.talk_button.pack(fill='x', pady=2)
        self.talk_button.bind('<ButtonPress-1>', self._on_manual_start)
        self.talk_button.bind('<ButtonRelease-1>', self._on_manual_stop)
        
        # Hotkey display
        self.hotkey_frame = tk.Frame(self.control_frame, bg='#1a1a1a')
        self.hotkey_frame.pack(fill='x', pady=2)
        
        tk.Label(self.hotkey_frame, text="Hotkey:", fg='#cccccc', 
                bg='#1a1a1a', font=('Arial', 8)).pack(side='left')
        
        self.hotkey_label = tk.Label(self.hotkey_frame, textvariable=self.hotkey_var,
                                   fg='#00ccff', bg='#1a1a1a', 
                                   font=('Courier', 8, 'bold'))
        self.hotkey_label.pack(side='right')
        

        

    
    def _create_transcript_section(self, parent):
        """Create transcript display section"""
        self.transcript_frame = tk.Frame(parent, bg='#2d2d2d', relief='sunken', bd=1)
        self.transcript_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.transcript_text = tk.Text(self.transcript_frame, height=4, wrap='word',
                                     fg='white', bg='#2d2d2d', 
                                     font=('Arial', 8), relief='flat', bd=0)
        self.transcript_text.pack(fill='both', expand=True, padx=3, pady=3)
    
    def _create_settings_section(self, parent):
        """Create settings and info section"""
        self.settings_frame = tk.Frame(parent, bg='#1a1a1a')
        self.settings_frame.pack(fill='x', padx=5, pady=2)
        
        # Model status and mic mute row
        self.status_row_frame = tk.Frame(self.settings_frame, bg='#1a1a1a')
        self.status_row_frame.pack(fill='x', pady=1)
        
        # Model status display
        self.model_status_var = tk.StringVar(value="⚠️ Checking models...")
        self.model_status_label = tk.Label(self.status_row_frame, 
                                          textvariable=self.model_status_var,
                                          fg='#ffcc00', bg='#1a1a1a', 
                                          font=('Arial', 7))
        self.model_status_label.pack(side='left')
        
        # Mic mute checkbox
        self.mic_mute_var = tk.BooleanVar(value=False)
        self.mic_mute_checkbox = tk.Checkbutton(self.status_row_frame, 
                                              text="Mic Mute", 
                                              variable=self.mic_mute_var,
                                              fg='#cccccc', bg='#1a1a1a',
                                              font=('Arial', 7),
                                              selectcolor='#2d2d2d',
                                              activeforeground='#ffffff',
                                              activebackground='#1a1a1a',
                                              command=self._toggle_mic_mute)
        self.mic_mute_checkbox.pack(side='right')
        
        # Audio level indicator (compact version)
        self.audio_level_frame = tk.Frame(self.settings_frame, bg='#1a1a1a')
        self.audio_level_frame.pack(fill='x', pady=1)
        
        tk.Label(self.audio_level_frame, text="Audio Level:", fg='#cccccc', 
                bg='#1a1a1a', font=('Arial', 7)).pack(side='left')
        
        self.level_bar = tk.Frame(self.audio_level_frame, bg='#2d2d2d', height=8, 
                                 relief='sunken', bd=1)
        self.level_bar.pack(side='right', fill='x', expand=True, padx=5)
        
        self.level_indicator = tk.Frame(self.level_bar, bg='#333333', height=6)
        self.level_indicator.pack(side='left', fill='y')
        
        # Settings button
        self.settings_btn = tk.Button(self.settings_frame, text="Settings",
                               fg='white', bg='#404040', 
                               font=('Arial', 8),
                               command=self._on_open_settings)
        self.settings_btn.pack(fill='x', pady=2)
        
        # Instructions
        self.instructions = tk.Label(self.settings_frame, 
                              text="Hold hotkey to speak • Drag icon, double-click to restore",
                              fg='#888888', bg='#1a1a1a', 
                              font=('Arial', 7))
        self.instructions.pack(pady=2)
    
    def _on_manual_start(self, event):
        """Handle manual button press"""
        if not self.is_recording:
            self._start_recording()
    
    def _on_manual_stop(self, event):
        """Handle manual button release"""
        if self.is_recording:
            self._stop_recording()
    
    def _on_open_settings(self):
        """Handle settings button click"""
        if self.on_open_settings:
            self.on_open_settings()
    
    def _toggle_mic_mute(self):
        """Handle mic mute checkbox toggle"""
        if self.on_mic_mute_toggle:
            self.on_mic_mute_toggle(self.mic_mute_var.get())
    
    def set_mic_mute_state(self, muted: bool):
        """Set the mic mute checkbox state programmatically"""
        try:
            self.mic_mute_var.set(muted)
        except Exception as e:
            print(f"Error setting mic mute state: {e}")
    
    def _start_recording(self):
        """Start recording UI state"""
        self.is_recording = True
        self.talk_button.config(text="Release to Stop", bg='#cc0000')
        if self.on_start_recording:
            self.on_start_recording()
    
    def _stop_recording(self):
        """Stop recording UI state"""
        self.is_recording = False
        self.talk_button.config(text="Hold to Talk", bg='#0066cc')
        if self.on_stop_recording:
            self.on_stop_recording()
    
    def _minimize_window(self):
        """Minimize window to small icon at current location"""
        if self.is_minimized:
            self._restore_window()
        else:
            self._minimize_to_icon()
    
    def _minimize_to_icon(self):
        """Minimize to small icon"""
        # Store current geometry and position
        self.normal_geometry = self.root.geometry()
        
        # Get current position
        current_x = self.root.winfo_x()
        current_y = self.root.winfo_y()
        
        # Hide all widgets except header
        for widget in self.main_frame.winfo_children():
            if widget != self.header_frame:
                widget.pack_forget()
        
        # Resize to slightly larger icon size for better double-click target
        icon_size = 36  # Slightly larger for easier double-clicking
        self.root.geometry(f"{icon_size}x{icon_size}+{current_x}+{current_y}")
        
        # Hide title and close button
        self.title_label.pack_forget()
        self.close_btn.pack_forget()
        
        # Configure header frame for icon mode
        self.header_frame.configure(height=icon_size, bg='#2d2d2d')
        
        # Keep drag events enabled for moving the icon
        self.header_frame.bind('<Button-1>', self._start_drag)
        self.header_frame.bind('<B1-Motion>', self._drag_window)
        
        # Create a frame container for the icon (better event handling)
        icon_frame = tk.Frame(self.header_frame, bg='#2d2d2d', cursor='hand2')
        icon_frame.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Create the icon label inside the frame
        # Use simple text that works on all Windows systems
        self.icon_button = tk.Label(
            icon_frame,
            text="MIC",
            font=('Arial', 11, 'bold'),  # Slightly larger font
            bg='#2d2d2d',
            fg='#00ccff',
            cursor='hand2'
        )
        self.icon_button.pack(fill='both', expand=True)
        print(f"Created icon with text: 'MIC'")
        
        # Create simple double-click restore functionality
        def on_double_click(e):
            print(f"Double-click detected - restoring window")
            self._restore_window()
            return "break"
        
        # Bind double-click to restore window (simpler, more reliable)
        clickable_widgets = [icon_frame, self.icon_button, self.header_frame, self.root]
        for widget in clickable_widgets:
            widget.bind('<Double-Button-1>', on_double_click)
            print(f"Bound double-click restore to {widget}")
        
        # Remove problematic hover effects (they cause errors)
        # Just keep the simple functionality
        
        # Add keyboard shortcut as backup (Escape key)
        self.root.bind('<Escape>', lambda e: self._restore_window())
        self.root.focus_set()  # Ensure window can receive key events
        
        # Hide the minimize button temporarily
        self.minimize_btn.pack_forget()
        
        # Remove the box-like border
        self.root.configure(bg='#2d2d2d')
        self.main_frame.configure(relief='flat', bd=0)
        
        self.is_minimized = True
    
    def _restore_window(self):
        """Restore window from minimized state"""
        print("Restoring window from minimized state...")  # Debug
        
        # Restore geometry
        if self.normal_geometry:
            self.root.geometry(self.normal_geometry)
            print(f"Restored geometry: {self.normal_geometry}")  # Debug
        
        # Restore window styling
        self.root.configure(bg='#1a1a1a')
        self.main_frame.configure(relief='raised', bd=1)
        self.header_frame.configure(height=30, bg='#2d2d2d')
        
        # Remove the temporary icon button
        if hasattr(self, 'icon_button'):
            self.icon_button.destroy()
            delattr(self, 'icon_button')
            print("Removed temporary icon button")  # Debug
        
        # Remove escape key binding
        self.root.unbind('<Escape>')
        
        # Restore title
        self.title_label.pack(side='left', padx=5, pady=5)
        
        # Restore controls frame position
        self.controls_frame.pack(side='right', padx=5)
        
        # Restore minimize button to normal style
        self.minimize_btn.config(
            text="−", 
            command=self._minimize_window,
            font=('Arial', 8),
            bg='#404040',
            fg='white',
            width=2,
            height=1,
            relief='flat',
            bd=0
        )
        self.minimize_btn.pack(side='left', padx=1)
        
        # Restore close button to normal style
        self.close_btn.config(
            text="×",
            font=('Arial', 8),
            bg='#d63384',
            fg='white',
            width=2,
            height=1,
            relief='flat',
            bd=0
        )
        self.close_btn.pack(side='left', padx=1)
        
        # Show all widgets again
        self.status_frame.pack(fill='x', padx=5, pady=2)
        self.control_frame.pack(fill='x', padx=5, pady=5)
        self.transcript_frame.pack(fill='both', expand=True, padx=5, pady=5)
        self.settings_frame.pack(fill='x', padx=5, pady=2)
        
        self.is_minimized = False
        print("Window restored successfully!")  # Debug
    
    def _start_drag(self, event):
        """Start window drag"""
        if event is None:
            return
        try:
            self.drag_start_x = event.x
            self.drag_start_y = event.y
        except AttributeError:
            # Handle case where event doesn't have x/y attributes
            self.drag_start_x = 0
            self.drag_start_y = 0

    def _drag_window(self, event):
        """Drag window to new position"""
        if event is None:
            return
        try:
            x = self.root.winfo_x() + event.x - self.drag_start_x
            y = self.root.winfo_y() + event.y - self.drag_start_y
            self.root.geometry(f"+{x}+{y}")
        except (AttributeError, tk.TclError):
            # Handle invalid event or window state
            pass
    
    def update_status(self, status: str):
        """Update status display"""
        self.status_var.set(status)
        self._update_status_color(status)
    
    def _update_status_color(self, status: str):
        """Update status color based on content"""
        if "Recording" in status or "Listening" in status:
            self.status_label.config(fg='#ff6600')
        elif "Processing" in status:
            self.status_label.config(fg='#ffff00')
        elif "ready" in status.lower() or "loaded" in status.lower():
            self.status_label.config(fg='#00ff00')
        elif "error" in status.lower():
            self.status_label.config(fg='#ff0000')
        else:
            self.status_label.config(fg='#cccccc')
    
    def update_transcript(self, text: str):
        """Update transcript display"""
        self.transcript_text.delete(1.0, tk.END)
        self.transcript_text.insert(1.0, text)
    
    def update_hotkey_display(self, hotkey_text: str):
        """Update hotkey display"""
        self.hotkey_var.set(hotkey_text)
    
    def set_always_on_top(self, on_top: bool):
        """Set window always on top"""
        self.root.attributes('-topmost', on_top)
    
    def update_model_status(self, status: str):
        """Update model status display"""
        self.model_status_var.set(status)
        # Update color based on status
        if "✅" in status:
            self.model_status_label.config(fg='#00ff00')
        elif "❌" in status:
            self.model_status_label.config(fg='#ff4444')
        else:
            self.model_status_label.config(fg='#ffcc00')
    
    def update_audio_level(self, level: float):
        """Update audio level indicator (0-100)"""
        try:
            # Get maximum available width for the level bar
            self.level_bar.update_idletasks()
            max_width = self.level_bar.winfo_width()
            
            if max_width > 0:
                # Calculate indicator width based on audio level
                level_width = int((level / 100) * max_width)
                level_width = max(0, min(level_width, max_width))
                
                # Update indicator width
                self.level_indicator.config(width=level_width)
                
                # Update color based on level
                if level > 30:
                    self.level_indicator.config(bg='#00ff00')  # Green - good level
                elif level > 10:
                    self.level_indicator.config(bg='#ffcc00')  # Yellow - low level
                else:
                    self.level_indicator.config(bg='#333333')  # Dark gray - very low/no signal
                    
        except (tk.TclError, AttributeError) as e:
            # Handle Tkinter errors during UI updates
            print(f"UI update error: {e}")
    
    def run(self):
        """Start the UI main loop"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"UI mainloop error: {e}")
            raise
    
    def destroy(self):
        """Clean up and close window"""
        print("Cleaning up UI...")
        try:
            # Cancel any pending after() calls
            if hasattr(self, 'root') and self.root:
                try:
                    # Cancel all pending after() calls
                    # Note: after_cancel('all') doesn't exist in standard Tkinter
                    # We'll just destroy the window which cancels pending calls
                    pass
                except tk.TclError:
                    pass
                
                # Unbind all events to prevent callbacks during destruction
                try:
                    self.root.unbind('<Button-1>')
                    self.root.unbind('<B1-Motion>')
                    self.root.unbind('<Double-Button-1>')
                    self.root.unbind('<Escape>')
                    
                    # Clear any widget-specific bindings
                    if hasattr(self, 'talk_button'):
                        self.talk_button.unbind('<ButtonPress-1>')
                        self.talk_button.unbind('<ButtonRelease-1>')
                        
                except tk.TclError:
                    pass  # Window already destroyed
                
                # Destroy the window
                self.root.destroy()
                print("UI destroyed successfully")
                
        except tk.TclError as e:
            print(f"Tkinter error during UI cleanup: {e}")
        except Exception as e:
            print(f"Error during UI cleanup: {e}")
            # Force quit if normal cleanup fails
            try:
                if hasattr(self, 'root') and self.root:
                    self.root.quit()
            except (tk.TclError, AttributeError):
                pass  # Window already destroyed or doesn't exist 