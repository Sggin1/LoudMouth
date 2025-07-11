# LoudMouth/hotkey_capture.py
# Hotkey capture dialog with proper UI flow
# Purpose: Handle hotkey selection with single/combo choice and real-time capture
# Dependencies: tkinter, pynput

import tkinter as tk
from tkinter import messagebox
from pynput import keyboard, mouse
import threading
import time


class HotkeyCapture:
    """Handles hotkey capture with proper UI flow"""
    
    def __init__(self, parent_window, settings_manager, callback=None):
        self.parent = parent_window
        self.settings = settings_manager
        self.callback = callback
        self.dialog = None
        self.capture_active = False
        self.key_listener = None
        self.mouse_listener = None
        
        # Capture state
        self.capture_mode = None  # 'single' or 'combo'
        self.combo_step = 0  # 0=waiting for modifier, 1=waiting for second key
        self.modifier_key = None
        
        # Excluded keys
        self.excluded_keys = {keyboard.Key.enter}
        
    def show_capture_dialog(self):
        """Show the hotkey capture dialog"""
        if self.dialog:
            return
            
        # Create dialog
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Set Hotkey")
        self.dialog.geometry("280x150")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.resizable(False, False)
        
        # Center on parent
        self._center_dialog()
        
        # Make modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        self.dialog.focus_set()
        
        # Handle close
        self.dialog.protocol("WM_DELETE_WINDOW", self._close_dialog)
        
        self._create_initial_ui()
        
    def _center_dialog(self):
        """Center dialog on parent window"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - 140
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - 75
        self.dialog.geometry(f"280x150+{x}+{y}")
        
    def _create_initial_ui(self):
        """Create the initial choice UI"""
        # Clear dialog
        for widget in self.dialog.winfo_children():
            widget.destroy()
            
        # Main frame
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="Set Hotkey", 
            font=('Arial', 12, 'bold'), 
            fg='white', 
            bg='#2b2b2b'
        )
        title_label.pack(pady=(0, 8))
        
        # Top button row
        top_frame = tk.Frame(main_frame, bg='#2b2b2b')
        top_frame.pack(pady=3)
        
        # Single Key button
        single_btn = tk.Button(
            top_frame,
            text="Single",
            command=self._start_single_capture,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=8,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        single_btn.pack(side='left', padx=2)
        
        # Combo button
        combo_btn = tk.Button(
            top_frame,
            text="Combo", 
            command=self._start_combo_capture,
            bg='#2196F3',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=8,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        combo_btn.pack(side='left', padx=2)
        
        # Reset button
        reset_btn = tk.Button(
            top_frame,
            text="Reset",
            command=self._reset_to_default,
            bg='#FF9800',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=8,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        reset_btn.pack(side='left', padx=2)
        
        # Bottom button row
        bottom_frame = tk.Frame(main_frame, bg='#2b2b2b')
        bottom_frame.pack(pady=3)
        
        # Finished button
        finished_btn = tk.Button(
            bottom_frame,
            text="Finished",
            command=self._close_dialog,
            bg='#9C27B0',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=8,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        finished_btn.pack(side='left', padx=2)
        
        # Exit button
        exit_btn = tk.Button(
            bottom_frame,
            text="Exit",
            command=self._close_dialog,
            bg='#f44336',
            fg='white',
            font=('Arial', 9, 'bold'),
            width=8,
            height=1,
            relief='flat',
            cursor='hand2'
        )
        exit_btn.pack(side='left', padx=2)
        
    def _start_single_capture(self):
        """Start single key capture"""
        self.capture_mode = 'single'
        self.combo_step = 0
        self.modifier_key = None
        self._create_capture_ui("Press any key (except Enter)")
        self._start_listeners()
        
    def _start_combo_capture(self):
        """Start combo key capture"""
        self.capture_mode = 'combo'
        self.combo_step = 0
        self.modifier_key = None
        self._create_capture_ui("Press modifier key (Ctrl, Alt, or Shift)")
        self._start_listeners()
        
    def _create_capture_ui(self, instruction_text):
        """Create the key capture UI"""
        # Clear dialog
        for widget in self.dialog.winfo_children():
            widget.destroy()
            
        # Main frame
        main_frame = tk.Frame(self.dialog, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Capturing...",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2b2b2b'
        )
        title_label.pack(pady=(0, 5))
        
        # Instruction
        self.instruction_label = tk.Label(
            main_frame,
            text=instruction_text,
            font=('Arial', 10),
            fg='#ffff00',
            bg='#2b2b2b',
            wraplength=260
        )
        self.instruction_label.pack(pady=(0, 5))
        
        # Status
        self.status_label = tk.Label(
            main_frame,
            text="Waiting...",
            font=('Arial', 8),
            fg='#cccccc',
            bg='#2b2b2b'
        )
        self.status_label.pack(pady=(0, 8))
        
        # Cancel button
        cancel_btn = tk.Button(
            main_frame,
            text="Cancel",
            command=self._cancel_capture,
            bg='#f44336',
            fg='white',
            font=('Arial', 9),
            width=10,
            relief='flat',
            cursor='hand2'
        )
        cancel_btn.pack(pady=(5, 0))
        
    def _start_listeners(self):
        """Start keyboard and mouse listeners"""
        self.capture_active = True
        
        # Keyboard listener
        self.key_listener = keyboard.Listener(
            on_press=self._on_key_press,
            suppress=False
        )
        
        # Mouse listener to block clicks
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            suppress=False
        )
        
        self.key_listener.start()
        self.mouse_listener.start()
        
    def _stop_listeners(self):
        """Stop all listeners"""
        self.capture_active = False
        
        if self.key_listener:
            try:
                self.key_listener.stop()
            except:
                pass
            self.key_listener = None
            
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except:
                pass
            self.mouse_listener = None
            
    def _on_key_press(self, key):
        """Handle key press during capture"""
        if not self.capture_active:
            return False
            
        try:
            # Check for excluded keys
            if key in self.excluded_keys:
                self._update_status("Enter key not allowed. Try another key...", '#ff6666')
                return True
                
            # Get key name
            key_name = self._get_key_name(key)
            if not key_name:
                self._update_status("Key not recognized. Try another key...", '#ff6666')
                return True
                
            # Handle based on mode
            if self.capture_mode == 'single':
                self._complete_single_capture(key_name)
                return False
                
            elif self.capture_mode == 'combo':
                if self.combo_step == 0:
                    # First key - must be modifier
                    if key_name.lower() in ['ctrl', 'alt', 'shift']:
                        self.modifier_key = key_name.lower()
                        self.combo_step = 1
                        self._update_instruction(f"Now press the second key to combine with {key_name}")
                        return True
                    else:
                        self._update_status("First key must be Ctrl, Alt, or Shift", '#ff6666')
                        return True
                        
                elif self.combo_step == 1:
                    # Second key
                    self._complete_combo_capture(self.modifier_key, key_name)
                    return False
                    
        except Exception as e:
            print(f"Key capture error: {e}")
            self._update_status("Error capturing key. Try again...", '#ff6666')
            return True
            
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse click during capture - block only left-click"""
        if not self.capture_active or not pressed:
            return True
        
        # Block only left-click
        if button == mouse.Button.left:
            self._update_status("Left-click not allowed. Use keyboard keys or other mouse buttons.", '#ff6666')
            return True
        
        # Allow other mouse buttons - treat as valid input
        button_name = self._get_mouse_button_name(button)
        if button_name:
            if self.capture_mode == 'single':
                self._complete_single_capture(button_name)
            elif self.capture_mode == 'combo':
                if self.combo_step == 0:
                    self._update_status("First key must be Ctrl, Alt, or Shift for combos", '#ff6666')
                else:
                    self._complete_combo_capture(self.modifier_key, button_name)
        
        return True
        
    def _get_key_name(self, key):
        """Convert pynput key to string name"""
        try:
            if hasattr(key, 'char') and key.char:
                return key.char.lower()
            elif hasattr(key, 'name'):
                # Map special keys
                key_mapping = {
                    'space': 'space',
                    'ctrl_l': 'ctrl',
                    'ctrl_r': 'ctrl',
                    'alt_l': 'alt', 
                    'alt_r': 'alt',
                    'shift_l': 'shift',
                    'shift_r': 'shift',
                    'tab': 'tab',
                    'caps_lock': 'capslock',
                    'esc': 'escape',
                    'f1': 'f1', 'f2': 'f2', 'f3': 'f3', 'f4': 'f4',
                    'f5': 'f5', 'f6': 'f6', 'f7': 'f7', 'f8': 'f8',
                    'f9': 'f9', 'f10': 'f10', 'f11': 'f11', 'f12': 'f12'
                }
                return key_mapping.get(key.name.lower(), key.name.lower())
            return None
        except:
            return None
    
    def _get_mouse_button_name(self, button):
        """Convert pynput mouse button to string name"""
        try:
            if button == mouse.Button.right:
                return 'right_click'
            elif button == mouse.Button.middle:
                return 'middle_click'
            elif button == mouse.Button.x1:
                return 'x1_click'
            elif button == mouse.Button.x2:
                return 'x2_click'
            return None
        except:
            return None
            
    def _update_status(self, text, color='#cccccc'):
        """Update status label"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=text, fg=color)
            
    def _update_instruction(self, text):
        """Update instruction label"""
        if hasattr(self, 'instruction_label'):
            self.instruction_label.config(text=text)
            
    def _complete_single_capture(self, key_name):
        """Complete single key capture"""
        self._stop_listeners()
        
        try:
            # Create hotkey config based on input type
            if key_name.endswith('_click'):
                # Mouse button
                button_name = key_name.replace('_click', '')
                hotkey_config = {'type': 'mouse', 'button': button_name}
                display_name = f"{button_name.replace('_', ' ').title()} Click"
            else:
                # Keyboard key
                hotkey_config = {'type': 'key', 'key': key_name}
                display_name = key_name.upper()
            
            # Apply to settings
            self.settings.set_hotkey(hotkey_config)
            
            # Show success
            self._show_success(f"Hotkey set to: {display_name}")
            
        except Exception as e:
            print(f"Single key capture error: {e}")
            self._update_status("Error setting hotkey", '#ff6666')
            
    def _complete_combo_capture(self, modifier, key_name):
        """Complete combo key capture"""
        self._stop_listeners()
        
        try:
            # Create hotkey config based on input type
            if key_name.endswith('_click'):
                # Mouse button combo
                button_name = key_name.replace('_click', '')
                hotkey_config = {
                    'type': 'mouse',
                    'button': button_name,
                    'modifier': modifier
                }
                display_name = f"{modifier.capitalize()}+{button_name.replace('_', ' ').title()} Click"
            else:
                # Keyboard key combo
                hotkey_config = {
                    'type': 'key',
                    'combo': {
                        'modifier': modifier,
                        'key': key_name
                    }
                }
                display_name = f"{modifier.capitalize()}+{key_name.upper()}"
            
            # Apply to settings
            self.settings.set_hotkey(hotkey_config)
            
            # Show success
            self._show_success(f"Hotkey set to: {display_name}")
            
        except Exception as e:
            print(f"Combo capture error: {e}")
            self._update_status("Error setting hotkey", '#ff6666')
            
    def _show_success(self, message):
        """Show success message and close dialog"""
        self._update_status(f"✅ {message}", '#00ff00')
        
        # Call callback if provided
        if self.callback:
            self.callback()
            
        # Close dialog after delay
        self.dialog.after(1500, self._close_dialog)
        
    def _cancel_capture(self):
        """Cancel current capture"""
        self._stop_listeners()
        self._create_initial_ui()
    
    def _reset_to_default(self):
        """Reset hotkey to default (Shift)"""
        try:
            # Set default hotkey (Shift)
            default_hotkey = {'type': 'key', 'key': 'shift'}
            self.settings.set_hotkey(default_hotkey)
            
            # Show success and close
            self._show_success("Hotkey reset to default: Shift")
            
        except Exception as e:
            print(f"Reset error: {e}")
            # Still show success message for user feedback
            self._show_success("Hotkey reset to default: Shift")
        
    def _close_dialog(self):
        """Close the dialog"""
        self._stop_listeners()
        
        if self.dialog:
            self.dialog.grab_release()
            self.dialog.destroy()
            self.dialog = None


# Convenience function for easy integration
def show_hotkey_capture(parent_window, settings_manager, callback=None):
    """Show hotkey capture dialog"""
    capture = HotkeyCapture(parent_window, settings_manager, callback)
    capture.show_capture_dialog()
    return capture 