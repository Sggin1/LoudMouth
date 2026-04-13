# v3_PTT/settings_window.py
# Settings window for v3 PTT configuration
# Purpose: GUI for adjusting application settings
# Dependencies: tkinter, ttk

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Callable, Optional


class SettingsWindow:
    """Settings configuration window"""
    
    def __init__(self, parent, settings_manager, audio_handler, hotkey_manager, callback: Optional[Callable] = None):
        self.parent = parent
        self.settings = settings_manager
        self.audio_handler = audio_handler
        self.hotkey_manager = hotkey_manager
        self.callback = callback
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title("Settings")

        # Dark theme for ttk widgets (Combobox, etc.)
        self._style = ttk.Style(self.window)
        try:
            self._style.theme_use('clam')
        except tk.TclError:
            pass
        self._style.configure('Dark.TCombobox',
                              fieldbackground='#2a2a2a',
                              background='#2a2a2a',
                              foreground='white',
                              arrowcolor='white',
                              bordercolor='#333',
                              lightcolor='#333', darkcolor='#333',
                              selectbackground='#404040',
                              selectforeground='white')
        self._style.map('Dark.TCombobox',
                        fieldbackground=[('readonly', '#2a2a2a')],
                        foreground=[('readonly', 'white')])
        # Force listbox popup to dark too
        self.window.option_add('*TCombobox*Listbox.background', '#2a2a2a')
        self.window.option_add('*TCombobox*Listbox.foreground', 'white')
        self.window.option_add('*TCombobox*Listbox.selectBackground', '#404040')
        self.window.option_add('*TCombobox*Listbox.selectForeground', 'white')
        self.window.geometry("640x760")
        self.window.minsize(560, 760)
        self.window.configure(bg='#1a1a1a')
        self.window.attributes('-topmost', True)
        self.window.resizable(True, True)
        
        # Center on parent window
        self._center_on_parent()
        
        # Make modal and force on top of parent
        self.window.transient(parent)
        self.window.grab_set()
        self.window.lift()
        self.window.focus_force()
        self.window.after(100, lambda: self.window.attributes('-topmost', True))
        
        # Create menu bar
        self._create_menu_bar()
        
        # Variables
        self.device_var = tk.StringVar()
        self.delay_var = tk.DoubleVar()
        self.always_on_top_var = tk.BooleanVar()
        self.model_size_var = tk.StringVar()
        self.clear_clipboard_on_close_var = tk.BooleanVar()
        self.copy_clipboard_var = tk.BooleanVar()
        self.english_only_var = tk.BooleanVar()
        self.technical_filter_var = tk.BooleanVar()
        self.voice_commands_var = tk.BooleanVar()
        
        # Create widgets
        self._create_widgets()
        self._load_current_settings()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _center_on_parent(self):
        """Center window on parent"""
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        x = parent_x + (parent_w // 2) - 320  # half of 640
        y = parent_y + (parent_h // 2) - 380  # half of 760

        self.window.geometry(f"640x760+{x}+{y}")
    
    def _create_menu_bar(self):
        """Create menu bar with About dropdown"""
        menubar = tk.Menu(self.window, bg='#2b2b2b', fg='white', 
                         activebackground='#404040', activeforeground='white',
                         bd=0, relief='flat')
        
        # About menu
        about_menu = tk.Menu(menubar, tearoff=0, bg='#2b2b2b', fg='white',
                            activebackground='#404040', activeforeground='white',
                            bd=0, relief='flat')
        about_menu.add_command(label="About LoudMouth", command=self._show_about_dialog)
        about_menu.add_separator()
        about_menu.add_command(label="System Info", command=self._show_system_info)
        about_menu.add_command(label="Whisper Models", command=self._show_model_info)
        
        menubar.add_cascade(label="About", menu=about_menu)
        
        # Configure menu bar
        self.window.config(menu=menubar)
    
    def _create_widgets(self):
        """Create all settings widgets"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Always on top section (moved to top for future expansion)
        self._create_always_on_top_section(main_frame)
        
        # Hotkey section
        self._create_hotkey_section(main_frame)
        
        # Audio device section
        self._create_audio_section(main_frame)
        
        # Post delay section
        self._create_delay_section(main_frame)
        
        # Model size section
        self._create_model_size_section(main_frame)
        
        # Buttons
        self._create_buttons(main_frame)
    
    def _create_hotkey_section(self, parent):
        """Create hotkey configuration section"""
        hotkey_frame = tk.LabelFrame(parent, text="Hotkey", fg='white', bg='#1a1a1a',
                                    font=('Arial', 9, 'bold'),
                                    bd=1, relief='flat', highlightthickness=0)
        hotkey_frame.pack(fill='x', pady=5)
        
        # Current hotkey display
        current_hotkey = self.settings.get_hotkey_display_text()
        self.hotkey_label = tk.Label(hotkey_frame, text=f"Current: {current_hotkey}",
                                    fg='#00ccff', bg='#1a1a1a', font=('Consolas', 10, 'bold'))
        self.hotkey_label.pack(pady=5)
        
        # Change hotkey button
        change_btn = tk.Button(hotkey_frame, text="Change Hotkey",
                              fg='white', bg='#0066cc', font=('Arial', 9),
                              command=self._change_hotkey)
        change_btn.pack(pady=5)
    
    def _create_audio_section(self, parent):
        """Create audio device selection section"""
        audio_frame = tk.LabelFrame(parent, text="Audio Device", fg='white', bg='#1a1a1a',
                                   font=('Arial', 9, 'bold'),
                                   bd=1, relief='flat', highlightthickness=0)
        audio_frame.pack(fill='x', pady=5)
        
        # Device dropdown
        devices = self.audio_handler.get_audio_devices()
        device_names = ["System Default"] + [dev['name'] for dev in devices]
        
        self.device_dropdown = ttk.Combobox(audio_frame, textvariable=self.device_var,
                                           values=device_names, state='readonly',
                                           style='Dark.TCombobox')
        self.device_dropdown.pack(fill='x', padx=10, pady=5)
    
    def _create_delay_section(self, parent):
        """Create post delay section - match hotkey section layout"""
        delay_frame = tk.LabelFrame(parent, text="Post Delay", fg='white', bg='#1a1a1a',
                                   font=('Arial', 9, 'bold'),
                                   bd=1, relief='flat', highlightthickness=0)
        delay_frame.pack(fill='x', pady=5)
        
        # Current delay display (like hotkey section)
        current_delay = f"{self.settings.get_type_delay():.1f} seconds"
        self.delay_display_label = tk.Label(delay_frame, text=f"Current: {current_delay}",
                                           fg='#00ccff', bg='#1a1a1a', font=('Arial', 9))
        self.delay_display_label.pack(pady=5)
        
        # Delay spinbox
        delay_spinbox = tk.Spinbox(delay_frame, from_=0.0, to=5.0, increment=0.1,
                                  textvariable=self.delay_var, width=10,
                                  fg='white', bg='#404040', font=('Arial', 9),
                                  command=self._update_delay_display)
        delay_spinbox.pack(pady=5)
        delay_spinbox.bind('<KeyRelease>', lambda e: self._update_delay_display())
    
    def _create_always_on_top_section(self, parent):
        """Create options section for always on top and future features"""
        options_frame = tk.LabelFrame(parent, text="Options", fg='white', bg='#1a1a1a',
                                     font=('Arial', 9, 'bold'),
                                     bd=1, relief='flat', highlightthickness=0)
        options_frame.pack(fill='x', pady=5)
        
        # Two-column grid of option checkboxes
        checkboxes_container = tk.Frame(options_frame, bg='#1a1a1a')
        checkboxes_container.pack(fill='x', padx=10, pady=5)
        checkboxes_container.columnconfigure(0, weight=1, uniform='opt')
        checkboxes_container.columnconfigure(1, weight=1, uniform='opt')

        def _cb(parent, text, var):
            return tk.Checkbutton(parent, text=text, variable=var,
                                  fg='white', bg='#1a1a1a',
                                  selectcolor='#404040',
                                  activeforeground='white',
                                  activebackground='#1a1a1a',
                                  font=('Arial', 9), anchor='w',
                                  bd=0, highlightthickness=0,
                                  padx=0, pady=0)

        options = [
            ("Always on top",          self.always_on_top_var),
            ("Clear clipboard on exit", self.clear_clipboard_on_close_var),
            ("Copy to clipboard",      self.copy_clipboard_var),
            ("English Only",           self.english_only_var),
            ("Voice Commands",         self.voice_commands_var),
            ("Technical Filter",       self.technical_filter_var),
        ]
        for i, (label, var) in enumerate(options):
            row, col = divmod(i, 2)
            _cb(checkboxes_container, label, var).grid(
                row=row, column=col, sticky='w', padx=(0, 20), pady=2)


    def _create_model_size_section(self, parent):
        """Create model size selection section"""
        model_size_frame = tk.LabelFrame(parent, text="Model Selection", fg='white', bg='#1a1a1a',
                                        font=('Arial', 9, 'bold'),
                                        bd=1, relief='flat', highlightthickness=0)
        model_size_frame.pack(fill='x', pady=5)
        
        # Get available models from model manager (ONLY from models folder, not cache)
        model_manager = self.audio_handler.model_manager
        available_models = model_manager._scan_local_models()  # Only scan local folder
        model_status = model_manager.get_model_status()
        
        # Create model options with sizes (only available models from folder)
        model_options = []
        
        # Show ALL models found in the folder (both standard and custom)
        for model in sorted(available_models):
            model_info = model_manager.model_info.get(model, {})
            size = model_info.get('size', 'Unknown')
            model_options.append(f"{model} ({size})")
        
        # If no models available, show warning
        if not model_options:
            model_options = ["No models available - Use Open Downloader"]
        
        # Create dropdown container with refresh capability
        dropdown_container = tk.Frame(model_size_frame, bg='#1a1a1a')
        dropdown_container.pack(fill='x', padx=10, pady=5)
        
        self.model_size_dropdown = ttk.Combobox(dropdown_container, textvariable=self.model_size_var,
                                               values=model_options, state='readonly',
                                               style='Dark.TCombobox')
        self.model_size_dropdown.pack(side='left', fill='x', expand=True)
        
        # Add refresh button (clearer text)
        refresh_btn = tk.Button(dropdown_container, text="Refresh", fg='white', bg='#404040', 
                               font=('Arial', 8), width=8, height=1,
                               relief='flat', bd=0,
                               command=self._refresh_model_dropdown)
        refresh_btn.pack(side='right', padx=(5, 0))
        
        # Tooltip-like help
        def on_enter(e):
            refresh_btn.config(bg='#007bff')
        def on_leave(e):
            refresh_btn.config(bg='#404040')
            
        refresh_btn.bind("<Enter>", on_enter)
        refresh_btn.bind("<Leave>", on_leave)
        
        # Add helper text
        helper_text = tk.Label(model_size_frame, text="Drop .pt files in models/ folder and click Refresh to detect them",
                              fg='#888888', bg='#1a1a1a', font=('Arial', 8))
        helper_text.pack(pady=(0, 5))
        
        # Load current model size
        current_model_size = self.settings.get_whisper_model_size()
        if current_model_size and model_options and model_options[0] != "No models available - Use Open Downloader":
            # Find the matching option (only among available models)
            for option in model_options:
                if option.startswith(current_model_size) and not option.startswith("---"):
                    self.model_size_dropdown.set(option)
                    break
            else:
                # Current model not available, select first available (skip separator)
                for option in model_options:
                    if not option.startswith("---") and option != "No models available - Use Open Downloader":
                        self.model_size_dropdown.set(option)
                        break
        else:
            # Default to first available model (base should be there for distribution)
            for option in model_options:
                if not option.startswith("---") and option != "No models available - Use Open Downloader":
                    self.model_size_dropdown.set(option)
                    break
    
    def _refresh_model_dropdown(self):
        """Refresh the model dropdown with current available models"""
        if not hasattr(self, 'model_size_dropdown'):
            return
            
        # Get available models from model manager (ONLY from models folder, not cache)
        model_manager = self.audio_handler.model_manager
        available_models = model_manager._scan_local_models()  # Only scan local folder
        model_status = model_manager.get_model_status()
        
        # Create model options with sizes (only available models from folder)
        model_options = []
        
        # Show ALL models found in the folder (both standard and custom)
        for model in sorted(available_models):
            model_info = model_manager.model_info.get(model, {})
            size = model_info.get('size', 'Unknown')
            model_options.append(f"{model} ({size})")
        
        # If no models available, show warning
        if not model_options:
            model_options = ["No models available - Use Open Downloader"]
        
        # Update dropdown values
        self.model_size_dropdown['values'] = model_options
        
        # Update selection if current model is still available
        current_selection = self.model_size_var.get()
        if current_selection not in model_options:
            # Select first available option if current selection is not valid
            for option in model_options:
                if not option.startswith("---") and option != "No models available - Use Open Downloader":
                    self.model_size_dropdown.set(option)
                    break
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg='#1a1a1a')
        button_frame.pack(fill='x', pady=15)  # Increased padding
        
        # Apply button (was Save - more intuitive for model changes)
        apply_btn = tk.Button(button_frame, text="Apply",
                             fg='white', bg='#28a745', font=('Arial', 9),
                             width=8, height=1, relief='flat', bd=0,
                             command=self._save_settings)
        apply_btn.pack(side='left', padx=5)
        
        # Open Downloader button (wider as requested)
        downloader_btn = tk.Button(button_frame, text="Open Downloader",
                                  fg='white', bg='#007bff', font=('Arial', 9),
                                  width=15, height=1, relief='flat', bd=0,
                                  command=self._open_downloader)
        downloader_btn.pack(side='left', padx=5)
        
        # Close button (was Cancel)
        close_btn = tk.Button(button_frame, text="Close",
                             fg='white', bg='#6c757d', font=('Arial', 9),
                             width=8, height=1, relief='flat', bd=0,
                             command=self._on_close)
        close_btn.pack(side='right', padx=5)
    
    def _load_current_settings(self):
        """Load current settings into UI"""
        
        # Audio device
        current_device = self.settings.get_device_index()
        if current_device is None:
            self.device_var.set("System Default")
        else:
            devices = self.audio_handler.get_audio_devices()
            for dev in devices:
                if dev['index'] == current_device:
                    self.device_var.set(dev['name'])
                    break
        
        # Post delay
        self.delay_var.set(self.settings.get_type_delay())
        
        # Always on top
        self.always_on_top_var.set(self.settings.get_always_on_top())
        
        # Clear clipboard on close (default False)
        self.clear_clipboard_on_close_var.set(self.settings.get_clear_clipboard_on_close())
        
        # Copy to clipboard (default False)
        self.copy_clipboard_var.set(self.settings.get_copy_clipboard())
        
        # English Only (default True)
        self.english_only_var.set(self.settings.get_english_only())
        
        # Technical filter (default True)
        self.technical_filter_var.set(self.settings.get_technical_filter())

        # Voice commands (default False)
        self.voice_commands_var.set(self.settings.get_voice_commands())
        
        # Model size
        current_model_size = self.settings.get_whisper_model_size()
        if current_model_size:
            self.model_size_var.set(current_model_size)
        else:
            self.model_size_var.set("base") # Default to base (more stable than small)
    
    def _change_hotkey(self):
        """Change hotkey using dedicated capture module"""
        try:
            from hotkey_capture import show_hotkey_capture
        except ImportError:
            # Fallback import path
            from .hotkey_capture import show_hotkey_capture
        
        def on_hotkey_changed():
            """Callback when hotkey is changed"""
            # Update the display
            current_hotkey = self.settings.get_hotkey_display_text()
            self.hotkey_label.config(text=f"Current: {current_hotkey}")
            
            # Call main callback if provided
            if self.callback:
                self.callback()
        
        # Show the hotkey capture dialog
        show_hotkey_capture(self.window, self.settings, on_hotkey_changed)
    

    
    def _save_settings(self):
        """Apply all settings (but keep window open)"""
        try:
            print("Applying settings...")  # Debug
            
            # Save audio device
            selected_device = self.device_var.get()
            if selected_device == "System Default":
                self.settings.set_device_index(None)
                device_success = True
            else:
                devices = self.audio_handler.get_audio_devices()
                device_found = False
                for dev in devices:
                    if dev['name'] == selected_device:
                        self.settings.set_device_index(dev['index'])
                        device_found = True
                        break
                device_success = device_found
            
            # Save post delay
            self.settings.set_type_delay(self.delay_var.get())
            self._update_delay_display()  # Update display
            delay_success = True
            
            # Save always on top
            self.settings.set_always_on_top(self.always_on_top_var.get())
            ontop_success = True
            
            # Save clear clipboard on close
            self.settings.set_clear_clipboard_on_close(self.clear_clipboard_on_close_var.get())
            clear_clipboard_success = True
            
            # Save copy to clipboard
            self.settings.set_copy_clipboard(self.copy_clipboard_var.get())
            clipboard_success = True
            
            # Save English Only setting
            self.settings.set_english_only(self.english_only_var.get())
            english_only_success = True
            
            # Save technical filter setting
            self.settings.set_technical_filter(self.technical_filter_var.get())
            technical_filter_success = True

            # Save voice commands setting
            self.settings.set_voice_commands(self.voice_commands_var.get())
            
            # Save model size (extract model name from format like "small (967MB)")
            selected_model_display = self.model_size_var.get()
            if (selected_model_display and 
                not selected_model_display.startswith("No models available") and
                not selected_model_display.startswith("---")):
                # Extract model name from display format
                model_name = selected_model_display.split(' ')[0]
                model_success = self.settings.set_whisper_model_size(model_name)
            else:
                model_success = False
            
            print(f"Apply results: device={device_success}, delay={delay_success}, ontop={ontop_success}, clear_clipboard={clear_clipboard_success}, clipboard={clipboard_success}, english_only={english_only_success}, model_size={model_success}")  # Debug
            
            # Notify callback to apply settings
            if self.callback:
                self.callback()
            
            # If model size changed, reload the model
            if model_success:
                self.audio_handler.reload_model()
            
            # Show apply confirmation
            self._show_save_confirmation()
            
        except Exception as e:
            print(f"Apply error: {e}")  # Debug
            # Use status message instead of dialog
            if hasattr(self, 'parent') and hasattr(self.parent, 'master'):
                # Find the main app status update
                pass
    
    def _show_save_confirmation(self):
        """Show apply confirmation on button"""
        # Find apply button more efficiently
        def find_apply_button(widget):
            if isinstance(widget, tk.Button) and widget['text'] == 'Apply':
                return widget
            for child in widget.winfo_children():
                result = find_apply_button(child)
                if result:
                    return result
            return None
        
        apply_btn = find_apply_button(self.window)
        if apply_btn:
            original_text = apply_btn['text']
            original_bg = apply_btn['bg']
            apply_btn.config(text="Applied!", bg='#28a745')
            self.window.after(1500, lambda: apply_btn.config(text=original_text, bg=original_bg))
    
    def _update_delay_display(self):
        """Update the delay display label"""
        try:
            current_delay = f"{self.delay_var.get():.1f} seconds"
            self.delay_display_label.config(text=f"Current: {current_delay}")
        except Exception:
            pass
    
    def _open_downloader(self):
        """Open the model downloader GUI"""
        try:
            from downloader_window import DownloaderWindow
            downloader = DownloaderWindow(self.window)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open downloader: {str(e)}")
    
    def _show_about_dialog(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.window)
        about_window.title("About LoudMouth")
        about_window.geometry("1024x800")
        about_window.minsize(560, 500)
        about_window.configure(bg='#1a1a1a')
        about_window.attributes('-topmost', True)
        about_window.resizable(True, True)

        # Center on settings window
        x = self.window.winfo_x() + 50
        y = self.window.winfo_y() + 50
        about_window.geometry(f"1024x800+{x}+{y}")
        
        # Make modal
        about_window.transient(self.window)
        about_window.grab_set()
        
        # Create scrollable text widget
        text_frame = tk.Frame(about_window, bg='#1a1a1a')
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Text widget with scrollbar
        text_widget = tk.Text(text_frame, bg='#2b2b2b', fg='white', 
                             font=('Courier', 10), wrap=tk.WORD,
                             borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # About content — commands first, details after
        about_text = """🎙️ Voice Commands (enable in Options)
=============================================
Commands are recognized only at the END of what you say,
so "I love enterprise" still types the whole sentence.
Commands can chain — "hello enter enter" types "hello"
and presses Enter twice.

Single-word:
  enter / return / new line ........ Enter
  tab (or cab/tad) ................. Tab
  backspace ........................ Backspace
  escape / esc ..................... Escape
  space ............................ Space
  delete ........................... Delete
  home, end ........................ Home / End
  up, down, left, right ............ Arrow keys
  page up, page down ............... PageUp / PageDown

Modifier combos (say modifier + key):
  control c / control v / control z
  alt tab
  shift tab
  (any of: control, ctrl, alt, shift)

Tip: when Voice Commands is enabled the app biases
Whisper toward these words so short utterances like
"tab" transcribe more reliably.


🎙️ LoudMouth (Push-to-Talk) Application
=============================================
Version: 1.0
Author: Sggin1 with collaboration from Claude

✨ Features:
• Offline speech recognition using OpenAI Whisper
• Multiple model size options (tiny, base, small, medium, large)
• Configurable hotkeys (keyboard & mouse)
• Audio device selection
• Clipboard integration
• Always on top option
• Advanced Whisper optimizations
• English-only mode for better performance
• Technical filter for programming/coding terms
• Persistent settings
• Model management & downloading

🔧 Technical Details:
• Built with Python, Tkinter, PyAudio
• Uses OpenAI Whisper for transcription
• HIPAA-compliant offline processing
• Optimized for short audio clips
• Memory-efficient resource management
• Thread-safe audio handling

⚙️ Whisper Optimizations:
• Temperature control for deterministic results
• Beam search for improved accuracy
• Silence detection & noise filtering
• Word-level timestamps
• Confidence metrics
• Multiple decoding attempts

🚀 Performance Features:
• Persistent audio streams
• Asynchronous model loading
• Efficient memory management
• Resource leak prevention
• Smart caching system

📝 Usage:
1. Select your preferred model size
2. Configure your hotkey
3. Choose audio input device
4. Enable desired options
5. Hold hotkey to record speech
6. Release to transcribe

For best performance, use English-only mode and select
the smallest model that meets your accuracy requirements.

Enjoy efficient, offline speech recognition!"""
        
        text_widget.insert(tk.END, about_text)
        text_widget.configure(state='disabled')
        
        # Close button
        close_btn = tk.Button(about_window, text="Close", 
                             fg='white', bg='#6c757d', font=('Arial', 9),
                             command=about_window.destroy)
        close_btn.pack(pady=10)
    
    def _show_system_info(self):
        """Show system information dialog"""
        import platform
        import sys
        import os
        
        info_window = tk.Toplevel(self.window)
        info_window.title("System Information")
        info_window.geometry("640x560")
        info_window.minsize(520, 420)
        info_window.configure(bg='#1a1a1a')
        info_window.attributes('-topmost', True)
        info_window.resizable(True, True)

        # Center on settings window
        x = self.window.winfo_x() + 60
        y = self.window.winfo_y() + 60
        info_window.geometry(f"640x560+{x}+{y}")
        
        # Make modal
        info_window.transient(self.window)
        info_window.grab_set()
        
        # Create scrollable text widget
        text_frame = tk.Frame(info_window, bg='#1a1a1a')
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, bg='#2b2b2b', fg='white', 
                             font=('Courier', 9), wrap=tk.WORD,
                             borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # System info content
        try:
            # Get audio devices
            devices = self.audio_handler.get_audio_devices()
            device_list = "\n".join([f"  {i}: {dev['name']}" for i, dev in enumerate(devices)])
            
            # Get settings info
            current_model = self.settings.get_whisper_model_size()
            
            system_info = f"""🖥️ System Information
=====================

Platform: {platform.system()} {platform.release()}
Architecture: {platform.machine()}
Python Version: {sys.version.split()[0]}
Working Directory: {os.getcwd()}

🎵 Audio Devices:
{device_list}

🤖 Whisper Configuration:
Current Model: {current_model}
Model Status: {self.audio_handler.get_model_quick_status()}
English Only: {'✅ Enabled' if self.settings.get_english_only() else '❌ Disabled'}

⚙️ Settings:
Always On Top: {'✅' if self.settings.get_always_on_top() else '❌'}
Copy to Clipboard: {'✅' if self.settings.get_copy_clipboard() else '❌'}
Clear Clipboard on Close: {'✅' if self.settings.get_clear_clipboard_on_close() else '❌'}
Technical Filter: {'✅ Enabled' if self.settings.get_technical_filter() else '❌ Disabled'}
Post Delay: {self.settings.get_type_delay()}s
Hotkey: {self.settings.get_hotkey_display_text()}

📁 Paths:
Settings: {self.settings.settings_file}
Models Cache: ~/.cache/whisper/"""
        except Exception as e:
            system_info = f"Error gathering system info: {str(e)}"
        
        text_widget.insert(tk.END, system_info)
        text_widget.configure(state='disabled')
        
        # Close button
        close_btn = tk.Button(info_window, text="Close", 
                             fg='white', bg='#6c757d', font=('Arial', 9),
                             command=info_window.destroy)
        close_btn.pack(pady=10)
    
    def _show_model_info(self):
        """Show Whisper model information"""
        model_window = tk.Toplevel(self.window)
        model_window.title("Whisper Models")
        model_window.geometry("640x560")
        model_window.minsize(520, 420)
        model_window.configure(bg='#1a1a1a')
        model_window.attributes('-topmost', True)
        model_window.resizable(True, True)

        # Center on settings window
        x = self.window.winfo_x() + 70
        y = self.window.winfo_y() + 70
        model_window.geometry(f"640x560+{x}+{y}")
        
        # Make modal
        model_window.transient(self.window)
        model_window.grab_set()
        
        # Create scrollable text widget
        text_frame = tk.Frame(model_window, bg='#1a1a1a')
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, bg='#2b2b2b', fg='white', 
                             font=('Courier', 9), wrap=tk.WORD,
                             borderwidth=0, highlightthickness=0)
        scrollbar = tk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Model info content
        try:
            current_model = self.settings.get_whisper_model_size()
            
            model_info = f"""🤖 Whisper Model Information
============================

Currently Active: {current_model}
Status: {self.audio_handler.get_model_quick_status()}

📊 Available Models:
┌─────────┬────────────┬─────────┬──────────┬────────────┐
│ Model   │ Parameters │ Size    │ Speed    │ Accuracy   │
├─────────┼────────────┼─────────┼──────────┼────────────┤
│ tiny    │ 39M        │ ~150MB  │ ~10x     │ Basic      │
│ base    │ 74M        │ ~290MB  │ ~7x      │ Good       │
│ small   │ 244M       │ ~967MB  │ ~4x      │ Better     │
│ medium  │ 769M       │ ~3.0GB  │ ~2x      │ Very Good  │
│ large   │ 1550M      │ ~6.0GB  │ 1x       │ Best       │
└─────────┴────────────┴─────────┴──────────┴────────────┘

🔧 Current Whisper Settings:
• English Only: {'✅ Enabled' if self.settings.get_english_only() else '❌ Disabled'}
• Technical Filter: {'✅ Enabled' if self.settings.get_technical_filter() else '❌ Disabled'}
• Temperature: {self.settings.get_whisper_temperature()}
• Best Of: {self.settings.get_whisper_best_of()}
• Beam Size: {self.settings.get_whisper_beam_size()}
• No Speech Threshold: {self.settings.get_whisper_no_speech_threshold()}
• Word Timestamps: {'✅' if self.settings.get_whisper_word_timestamps() else '❌'}
• Show Confidence: {'✅' if self.settings.get_whisper_show_confidence() else '❌'}

💡 Recommendations:
• For speed: Use tiny or base models
• For accuracy: Use small or medium models
• For best quality: Use large model (requires more RAM)
• Enable English Only for 20-40% speed boost
• Enable Technical Filter for coding/programming work
• Use temperature=0.0 for deterministic results

🔧 Technical Filter:
Converts speech to programming terms:
• "underscore" → "_"
• "dot py" → ".py"
• "open paren close paren" → "()"
• "equals equals" → "=="
• And 100+ more programming conversions

📁 Model Locations:
• Local bundled: ./models/
• Downloaded cache: ~/.cache/whisper/

Use the Model Downloader to pre-download models
for faster startup times."""
        except Exception as e:
            model_info = f"Error gathering model info: {str(e)}"
        
        text_widget.insert(tk.END, model_info)
        text_widget.configure(state='disabled')
        
        # Close button
        close_btn = tk.Button(model_window, text="Close", 
                             fg='white', bg='#6c757d', font=('Arial', 9),
                             command=model_window.destroy)
        close_btn.pack(pady=10)
    
    def _on_close(self):
        """Close settings window"""
        self.window.grab_release()
        self.window.destroy()
    
    def get_clear_clipboard_on_close_enabled(self) -> bool:
        """Get clear clipboard on close setting"""
        return self.settings.get_clear_clipboard_on_close()
    
    def get_copy_clipboard_enabled(self) -> bool:
        """Get copy to clipboard setting"""
        return self.settings.get_copy_clipboard() 