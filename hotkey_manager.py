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
        self.pressed_keys = set()  # Track currently pressed keys for combinations
        
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
        
        # Track pressed keys for combinations
        self.pressed_keys.add(key)
        
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
        
        # Remove from pressed keys
        self.pressed_keys.discard(key)
        
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
            # Handle combination keys
            if 'combo' in self.current_hotkey:
                combo = self.current_hotkey['combo']
                modifier = combo.get('modifier')
                main_key = combo.get('key')
                
                # Check if this is the main key and modifier is pressed
                if self._key_matches(key, main_key):
                    return self._is_modifier_pressed(modifier)
                
                return False
            
            # Handle single keys (legacy support)
            hotkey_key = self.current_hotkey.get('key', 'space')
            return self._key_matches(key, hotkey_key)
            
        except (AttributeError, TypeError) as e:
            print(f"Key matching error: {e}")
            return False
    
    def _key_matches(self, key, target_key):
        """Check if a key matches the target key string"""
        if target_key == 'space':
            return key == Key.space
        elif target_key == 'ctrl':
            return key == Key.ctrl_l or key == Key.ctrl_r
        elif target_key == 'alt':
            return key == Key.alt_l or key == Key.alt_r
        elif target_key == 'shift':
            return key == Key.shift_l or key == Key.shift_r
        elif target_key == 'enter':
            return key == Key.enter
        elif hasattr(key, 'char') and key.char:
            return key.char.lower() == target_key.lower()
        return False
    
    def _is_modifier_pressed(self, modifier):
        """Check if the specified modifier key is currently pressed"""
        if modifier == 'ctrl':
            return Key.ctrl_l in self.pressed_keys or Key.ctrl_r in self.pressed_keys
        elif modifier == 'alt':
            return Key.alt_l in self.pressed_keys or Key.alt_r in self.pressed_keys
        elif modifier == 'shift':
            return Key.shift_l in self.pressed_keys or Key.shift_r in self.pressed_keys
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
        
        # Temporarily stop main listeners to avoid conflicts
        print("Stopping main listeners for capture...")
        self.stop_listeners()
        
        # No delay needed - left-click is now enter key
        
        # Track keys for combination detection
        capture_pressed_keys = set()
        
        def on_key_capture_press(key):
            print(f"Key pressed: {key}")
            capture_pressed_keys.add(key)
            # Also update the main pressed_keys for mouse capture
            self.pressed_keys.add(key)
            return True
        
        def on_key_capture_release(key):
            print(f"Key released: {key}")
            try:
                # Check if this is a combination (modifier + key)
                modifiers = [Key.ctrl_l, Key.ctrl_r, Key.alt_l, Key.alt_r, Key.shift_l, Key.shift_r]
                pressed_modifiers = [k for k in capture_pressed_keys if k in modifiers]
                
                if pressed_modifiers and key not in modifiers:
                    # This is a combination key
                    modifier_key = pressed_modifiers[0]
                    
                    # Determine modifier name - with error handling
                    modifier_name = 'ctrl'
                    modifier_display = 'Ctrl'
                    try:
                        if modifier_key in [Key.ctrl_l, Key.ctrl_r]:
                            modifier_name = 'ctrl'
                            modifier_display = 'Ctrl'
                        elif modifier_key in [Key.alt_l, Key.alt_r]:
                            modifier_name = 'alt'
                            modifier_display = 'Alt'
                        elif modifier_key in [Key.shift_l, Key.shift_r]:
                            modifier_name = 'shift'
                            modifier_display = 'Shift'
                    except Exception as e:
                        print(f"Modifier key error: {e}")
                    
                    # Determine main key - with error handling
                    main_key = 'unknown'
                    main_display = 'Unknown'
                    try:
                        if key == Key.space:
                            main_key = 'space'
                            main_display = 'Space'
                        elif key == Key.enter:
                            main_key = 'enter'
                            main_display = 'Enter'
                        elif hasattr(key, 'char') and key.char and len(key.char) == 1 and key.char.isprintable():
                            main_key = key.char.lower()
                            main_display = key.char.upper()
                        else:
                            print(f"Unsupported key: {key}")
                            capture_pressed_keys.discard(key)
                            self.pressed_keys.discard(key)
                            return True
                    except Exception as e:
                        print(f"Main key error: {e}")
                        capture_pressed_keys.discard(key)
                        self.pressed_keys.discard(key)
                        return True
                    
                    hotkey_config = {
                        'type': 'key',
                        'combo': {
                            'modifier': modifier_name,
                            'key': main_key
                        }
                    }
                    display_name = f"{modifier_display}+{main_display}"
                    
                    print(f"Combo captured: {hotkey_config} -> {display_name}")
                    self.is_setting_hotkey = False
                    callback(hotkey_config, display_name)
                    return False
                
                # Single key (no modifier)
                elif key not in modifiers:
                    # Block problematic single keys
                    blocked_keys = [Key.enter, Key.tab, Key.esc, Key.backspace, Key.delete]
                    if key in blocked_keys:
                        print(f"Single {key.name} blocked - use in combination only")
                        capture_pressed_keys.discard(key)
                        return True
                    
                    if key == Key.space:
                        hotkey_config = {'type': 'key', 'key': 'space'}
                        display_name = "Space"
                    elif hasattr(key, 'char') and key.char and len(key.char) == 1 and key.char.isprintable():
                        hotkey_config = {'type': 'key', 'key': key.char.lower()}
                        display_name = key.char.upper()
                    else:
                        capture_pressed_keys.discard(key)
                        return True
                    
                    self.is_setting_hotkey = False
                    callback(hotkey_config, display_name)
                    return False
                
                # Just remove the key and continue
                capture_pressed_keys.discard(key)
                self.pressed_keys.discard(key)
                return True
                
            except (AttributeError, TypeError) as e:
                print(f"Key capture error: {e}")
                capture_pressed_keys.discard(key)
                self.pressed_keys.discard(key)
                return True
        
        def on_mouse_capture(x, y, button, pressed):
            print(f"Mouse {button} {'pressed' if pressed else 'released'}")
            if pressed:
                try:
                    # Handle left-click as "Enter" for combinations
                    if button == Button.left:
                        # Check if any modifier is pressed
                        modifiers = [Key.ctrl_l, Key.ctrl_r, Key.alt_l, Key.alt_r, Key.shift_l, Key.shift_r]
                        pressed_modifiers = [k for k in self.pressed_keys if k in modifiers]
                        
                        if pressed_modifiers:
                            # This is a combination with left-click as "Enter"
                            modifier_key = pressed_modifiers[0]
                            
                            # Determine modifier name
                            if modifier_key in [Key.ctrl_l, Key.ctrl_r]:
                                modifier_name = 'ctrl'
                                modifier_display = 'Ctrl'
                            elif modifier_key in [Key.alt_l, Key.alt_r]:
                                modifier_name = 'alt'
                                modifier_display = 'Alt'
                            elif modifier_key in [Key.shift_l, Key.shift_r]:
                                modifier_name = 'shift'
                                modifier_display = 'Shift'
                            
                            hotkey_config = {
                                'type': 'key',
                                'combo': {
                                    'modifier': modifier_name,
                                    'key': 'enter'
                                }
                            }
                            display_name = f"{modifier_display}+Enter"
                            
                            self.is_setting_hotkey = False
                            callback(hotkey_config, display_name)
                            return False
                        else:
                            print(f"Left-click alone not allowed - use with Ctrl/Alt/Shift for combinations")
                            return True
                    
                    button_mappings = {
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
        try:
            capture_keyboard = KeyboardListener(
                on_press=on_key_capture_press,
                on_release=on_key_capture_release
            )
            capture_mouse = MouseListener(on_click=on_mouse_capture)
            
            print("Starting capture listeners...")
            capture_keyboard.start()
            capture_mouse.start()
            print("Capture listeners started successfully")
        except Exception as e:
            print(f"Error starting capture listeners: {e}")
            self.is_setting_hotkey = False
            return lambda: None
        
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
                # Restart main listeners
                print("Restarting main listeners...")
                self.start_listeners()
        
        return stop_capture
    
    def capture_new_hotkey_with_feedback(self, callback: Callable, feedback_callback: Callable):
        """Capture hotkey with real-time feedback"""
        self.is_setting_hotkey = True
        
        # Stop main listeners
        self.stop_listeners()
        
        # Track pressed keys for real-time feedback
        pressed_keys = set()
        
        def on_key_press_feedback(key):
            try:
                # Convert key to string for feedback
                key_str = None
                if key == Key.ctrl_l or key == Key.ctrl_r:
                    key_str = 'ctrl'
                elif key == Key.alt_l or key == Key.alt_r:
                    key_str = 'alt'
                elif key == Key.shift_l or key == Key.shift_r:
                    key_str = 'shift'
                elif key == Key.space:
                    key_str = 'space'
                elif key == Key.enter:
                    # Enter key confirms current combination
                    if pressed_keys:
                        print(f"Enter confirming combination: {list(pressed_keys)}")
                        # Build hotkey from current keys
                        modifiers = [k for k in pressed_keys if k in ['ctrl', 'alt', 'shift']]
                        main_keys = [k for k in pressed_keys if k not in ['ctrl', 'alt', 'shift']]
                        
                        if modifiers and main_keys:
                            # Combination hotkey
                            hotkey_config = {
                                'type': 'key',
                                'combo': {
                                    'modifier': modifiers[0],
                                    'key': main_keys[0]
                                }
                            }
                            display_name = f"{modifiers[0].title()}+{main_keys[0].upper()}"
                            callback(hotkey_config, display_name)
                        elif main_keys:
                            # Single key
                            hotkey_config = {'type': 'key', 'key': main_keys[0]}
                            display_name = main_keys[0].upper()
                            callback(hotkey_config, display_name)
                    return True
                elif hasattr(key, 'char') and key.char and len(key.char) == 1 and key.char.isprintable():
                    key_str = key.char.lower()
                else:
                    print(f"Ignoring unsupported key: {key}")
                    return True
                
                if key_str:
                    pressed_keys.add(key_str)
                    print(f"Key pressed: {key_str}, current keys: {list(pressed_keys)}")
                    # Call feedback from UI thread
                    try:
                        feedback_callback(list(pressed_keys))
                    except Exception as e:
                        print(f"Feedback callback error: {e}")
                
            except Exception as e:
                print(f"Key press feedback error: {e}")
            return True
        
        def on_key_release_feedback(key):
            try:
                # Convert key to string for feedback
                key_str = None
                if key == Key.ctrl_l or key == Key.ctrl_r:
                    key_str = 'ctrl'
                elif key == Key.alt_l or key == Key.alt_r:
                    key_str = 'alt'
                elif key == Key.shift_l or key == Key.shift_r:
                    key_str = 'shift'
                elif key == Key.space:
                    key_str = 'space'
                elif key == Key.enter:
                    key_str = 'enter'
                elif hasattr(key, 'char') and key.char and len(key.char) == 1 and key.char.isprintable():
                    key_str = key.char.lower()
                else:
                    # Silently ignore unsupported keys on release
                    return True
                
                if key_str:
                    pressed_keys.discard(key_str)
                    print(f"Key released: {key_str}, current keys: {list(pressed_keys)}")
                    # Call feedback from UI thread
                    try:
                        feedback_callback(list(pressed_keys))
                    except Exception as e:
                        print(f"Feedback callback error: {e}")
                
            except Exception as e:
                print(f"Key release feedback error: {e}")
            return True
        
        def on_mouse_click_feedback(x, y, button, pressed):
            if pressed and button == Button.left:
                # Left-click confirms current combination
                if pressed_keys:
                    print(f"Left-click confirming combination: {list(pressed_keys)}")
                    # Build hotkey from current keys
                    modifiers = [k for k in pressed_keys if k in ['ctrl', 'alt', 'shift']]
                    main_keys = [k for k in pressed_keys if k not in ['ctrl', 'alt', 'shift']]
                    
                    if modifiers and main_keys:
                        # Combination hotkey
                        hotkey_config = {
                            'type': 'key',
                            'combo': {
                                'modifier': modifiers[0],
                                'key': main_keys[0]
                            }
                        }
                        display_name = f"{modifiers[0].title()}+{main_keys[0].upper()}"
                        callback(hotkey_config, display_name)
                    elif main_keys:
                        # Single key
                        hotkey_config = {'type': 'key', 'key': main_keys[0]}
                        display_name = main_keys[0].upper()
                        callback(hotkey_config, display_name)
                else:
                    print("No keys pressed to confirm")
            return True
        
        # Start feedback listeners
        try:
            feedback_keyboard = KeyboardListener(
                on_press=on_key_press_feedback,
                on_release=on_key_release_feedback
            )
            feedback_mouse = MouseListener(on_click=on_mouse_click_feedback)
            
            feedback_keyboard.start()
            feedback_mouse.start()
            
            def stop_feedback():
                try:
                    feedback_keyboard.stop()
                    feedback_mouse.stop()
                    feedback_keyboard.join(timeout=1.0)
                    feedback_mouse.join(timeout=1.0)
                except Exception as e:
                    print(f"Error stopping feedback listeners: {e}")
                finally:
                    self.is_setting_hotkey = False
                    self.start_listeners()
            
            return stop_feedback
            
        except Exception as e:
            print(f"Error starting feedback listeners: {e}")
            self.is_setting_hotkey = False
            self.start_listeners()
            return lambda: None
    
    def cleanup(self):
        """Clean up listeners"""
        print("Cleaning up hotkey manager...")
        self.is_setting_hotkey = False
        self.stop_listeners()
        print("Hotkey manager cleanup complete") 