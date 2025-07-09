# v3_PTT/hotkey_manager.py
# Global hotkey listener manager
# Purpose: Handle keyboard and mouse hotkey detection
# Dependencies: pynput

from pynput import keyboard, mouse
from pynput.keyboard import Key, Listener as KeyboardListener
from pynput.mouse import Button, Listener as MouseListener
from typing import Callable, Optional, Dict, Any
import threading


class HotkeyManager:
    """Manages global hotkey listeners for keyboard and mouse"""
    
    def __init__(self, 
                 on_hotkey_press: Optional[Callable] = None,
                 on_hotkey_release: Optional[Callable] = None):
        self.on_hotkey_press = on_hotkey_press
        self.on_hotkey_release = on_hotkey_release
        
        self.current_hotkey = {'type': 'key', 'key': 'space'}
        self.keyboard_listener = None
        self.mouse_listener = None
        self.is_setting_hotkey = False
        self.is_pressed = False
        
        # Start listeners
        self.start_listeners()
    
    def start_listeners(self):
        """Start global hotkey listeners"""
        self.stop_listeners()
        
        # Keyboard listener
        self.keyboard_listener = KeyboardListener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
            suppress=False
        )
        
        # Mouse listener
        self.mouse_listener = MouseListener(
            on_click=self._on_mouse_click,
            suppress=False
        )
        
        self.keyboard_listener.start()
        self.mouse_listener.start()
    
    def stop_listeners(self):
        """Stop all listeners"""
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            try:
                self.keyboard_listener.join(timeout=1.0)
                if self.keyboard_listener.is_alive():
                    print("Warning: Keyboard listener did not stop cleanly")
            except (RuntimeError, OSError) as e:
                print(f"Error stopping keyboard listener: {e}")
        if self.mouse_listener:
            self.mouse_listener.stop()
            try:
                self.mouse_listener.join(timeout=1.0)
                if self.mouse_listener.is_alive():
                    print("Warning: Mouse listener did not stop cleanly")
            except (RuntimeError, OSError) as e:
                print(f"Error stopping mouse listener: {e}")
    
    def set_hotkey(self, hotkey_config: Dict[str, Any]):
        """Set new hotkey configuration"""
        self.current_hotkey = hotkey_config
        self.is_pressed = False
        # Restart listeners to apply new hotkey
        self.start_listeners()
    
    def _on_key_press(self, key):
        """Handle keyboard key press"""
        if self.is_setting_hotkey:
            return True
        
        if self.current_hotkey['type'] == 'key' and self._matches_key(key):
            if not self.is_pressed:
                self.is_pressed = True
                if self.on_hotkey_press:
                    self.on_hotkey_press()
        return True
    
    def _on_key_release(self, key):
        """Handle keyboard key release"""
        if self.is_setting_hotkey:
            return True
        
        if self.current_hotkey['type'] == 'key' and self._matches_key(key):
            if self.is_pressed:
                self.is_pressed = False
                if self.on_hotkey_release:
                    self.on_hotkey_release()
        return True
    
    def _on_mouse_click(self, x, y, button, pressed):
        """Handle mouse button click"""
        if self.is_setting_hotkey:
            return True
        
        if self.current_hotkey['type'] == 'mouse' and self._matches_mouse_button(button):
            if pressed and not self.is_pressed:
                self.is_pressed = True
                if self.on_hotkey_press:
                    self.on_hotkey_press()
            elif not pressed and self.is_pressed:
                self.is_pressed = False
                if self.on_hotkey_release:
                    self.on_hotkey_release()
        return True
    
    def _matches_key(self, key) -> bool:
        """Check if key matches current hotkey"""
        try:
            hotkey_key = self.current_hotkey.get('key', 'space')
            
            if hotkey_key == 'space':
                return key == Key.space
            elif hotkey_key == 'ctrl':
                return key == Key.ctrl_l or key == Key.ctrl_r
            elif hotkey_key == 'alt':
                return key == Key.alt_l or key == Key.alt_r
            elif hotkey_key == 'shift':
                return key == Key.shift_l or key == Key.shift_r
            elif hasattr(key, 'char') and key.char:
                return key.char.lower() == hotkey_key.lower()
            
            return False
        except (AttributeError, TypeError) as e:
            print(f"Key matching error: {e}")
            return False
    
    def _matches_mouse_button(self, button) -> bool:
        """Check if mouse button matches current hotkey"""
        try:
            hotkey_button = self.current_hotkey.get('button', 'left')
            
            if hotkey_button == 'left':
                return button == Button.left
            elif hotkey_button == 'right':
                return button == Button.right
            elif hotkey_button == 'middle':
                return button == Button.middle
            elif hotkey_button == 'x1':
                return button == Button.x1
            elif hotkey_button == 'x2':
                return button == Button.x2
            
            return False
        except (AttributeError, TypeError) as e:
            print(f"Mouse button matching error: {e}")
            return False
    
    def capture_new_hotkey(self, callback: Callable):
        """Capture a new hotkey from user input"""
        self.is_setting_hotkey = True
        
        def on_key_capture(key):
            try:
                if key == Key.space:
                    hotkey_config = {'type': 'key', 'key': 'space'}
                    display_name = "Space"
                elif key == Key.ctrl_l or key == Key.ctrl_r:
                    hotkey_config = {'type': 'key', 'key': 'ctrl'}
                    display_name = "Ctrl"
                elif key == Key.alt_l or key == Key.alt_r:
                    hotkey_config = {'type': 'key', 'key': 'alt'}
                    display_name = "Alt"
                elif key == Key.shift_l or key == Key.shift_r:
                    hotkey_config = {'type': 'key', 'key': 'shift'}
                    display_name = "Shift"
                elif hasattr(key, 'char') and key.char:
                    hotkey_config = {'type': 'key', 'key': key.char.lower()}
                    display_name = key.char.upper()
                else:
                    return True
                
                self.is_setting_hotkey = False
                callback(hotkey_config, display_name)
                return False
            except (AttributeError, TypeError) as e:
                print(f"Key capture error: {e}")
                return True
        
        def on_mouse_capture(x, y, button, pressed):
            if pressed:
                try:
                    button_mappings = {
                        Button.left: ('left', 'Left Click'),
                        Button.right: ('right', 'Right Click'),
                        Button.middle: ('middle', 'Middle Click'),
                        Button.x1: ('x1', 'Side Button 1'),
                        Button.x2: ('x2', 'Side Button 2')
                    }
                    
                    if button in button_mappings:
                        button_key, display_name = button_mappings[button]
                        hotkey_config = {'type': 'mouse', 'button': button_key}
                        
                        self.is_setting_hotkey = False
                        callback(hotkey_config, display_name)
                        return False
                except (AttributeError, TypeError) as e:
                    print(f"Mouse capture error: {e}")
            return True
        
        # Start temporary listeners for capture
        capture_keyboard = KeyboardListener(on_press=on_key_capture)
        capture_mouse = MouseListener(on_click=on_mouse_capture)
        
        capture_keyboard.start()
        capture_mouse.start()
        
        # Return stop function
        def stop_capture():
            try:
                capture_keyboard.stop()
                capture_mouse.stop()
                
                # Wait for capture threads to finish
                capture_keyboard.join(timeout=1.0)
                capture_mouse.join(timeout=1.0)
                
            except (RuntimeError, OSError) as e:
                print(f"Error stopping capture listeners: {e}")
            finally:
                self.is_setting_hotkey = False
        
        return stop_capture
    
    def cleanup(self):
        """Clean up listeners"""
        print("Cleaning up hotkey manager...")
        self.is_setting_hotkey = False
        self.stop_listeners()
        print("Hotkey manager cleanup complete") 