# v3_PTT/command_structure.py
# Command parsing and execution framework (stub)
# Purpose: Future expansion hook for voice commands
# Dependencies: pyautogui (for future implementation)

from typing import List, Dict, Any, Optional
import pyautogui
import time
import os
import win32gui
from text_normalizer import text_normalizer


class CommandParser:
    """Parser for voice commands (stub for future implementation)"""
    
    def __init__(self):
        self.enabled = False  # Commands disabled for now
        self.command_patterns = {}  # Future: command definitions
        self.text_normalizer = text_normalizer  # Use the global text normalizer
    
    def parse_commands(self, text: str) -> tuple[str, List[str]]:
        """Parse text for commands - returns (clean_text, commands)"""
        # Always apply text normalization first
        normalized_text = self.text_normalizer.normalize_text(text)
        
        # If commands are not enabled, just return normalized text
        if not self.enabled:
            return normalized_text, []
        
        # TODO: Implement command parsing logic
        # Example: "Hello world enter" -> ("Hello world", ["enter"])
        return normalized_text, []
    
    def enable_commands(self):
        """Enable command parsing (for future use)"""
        self.enabled = True
    
    def disable_commands(self):
        """Disable command parsing"""
        self.enabled = False
    
    def enable_text_normalization(self):
        """Enable text normalization"""
        self.text_normalizer.enable()
    
    def disable_text_normalization(self):
        """Disable text normalization"""
        self.text_normalizer.disable()
    
    def is_text_normalization_enabled(self) -> bool:
        """Check if text normalization is enabled"""
        return self.text_normalizer.is_enabled()
    
    def add_normalization_rule(self, phrase: str, replacement: str, case_sensitive: bool = False):
        """Add a custom normalization rule"""
        self.text_normalizer.add_custom_rule(phrase, replacement, case_sensitive)
    
    def preview_normalization(self, text: str) -> Dict[str, str]:
        """Preview what normalization changes would be made"""
        return self.text_normalizer.preview_normalization(text)


class CommandExecutor:
    """Executes parsed commands (stub for future implementation)"""
    
    def __init__(self, type_delay: float = 1.0):
        self.type_delay = type_delay
        self.command_actions = {}  # Future: command implementations
        
        # Disable PyAutoGUI fail-safe and sounds
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.01  # Reduce delay between actions
    
    def type_text(self, text: str) -> bool:
        """Type text using pyautogui with error handling"""
        try:
            # Add small delay before typing
            time.sleep(self.type_delay)
            
            # Type the text
            pyautogui.typewrite(text)
            print(f"✅ Typed: '{text}'")
            return True
            
        except (OSError, IOError, pyautogui.FailSafeException) as e:
            print(f"❌ Typing error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected typing error: {e}")
            return False
    
    def execute_command(self, command: str) -> bool:
        """Execute a parsed command"""
        try:
            if command.startswith('key:'):
                key_combo = command[4:]  # Remove 'key:' prefix
                # Handle key combinations like 'ctrl+c', 'alt+tab', etc.
                if '+' in key_combo:
                    keys = key_combo.split('+')
                    pyautogui.hotkey(*keys)
                    print(f"✅ Key combo: {key_combo}")
                else:
                    pyautogui.press(key_combo)
                    print(f"✅ Key press: {key_combo}")
                return True
            
            elif command.startswith('click:'):
                # Handle click commands (future feature)
                print(f"⚠️ Click commands not implemented yet: {command}")
                return False
            
            else:
                print(f"⚠️ Unknown command: {command}")
                return False
                
        except (OSError, IOError, pyautogui.FailSafeException) as e:
            print(f"❌ Command execution error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected command error: {e}")
            return False
    
    def _get_window_class(self, window_title: str) -> str:
        """Get the class name of a window for better targeting"""
        try:
            import win32gui
            import win32con
            
            def enum_windows_proc(hwnd, param):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in title.lower():
                        class_name = win32gui.GetClassName(hwnd)
                        param.append(class_name)
                return True
            
            window_classes = []
            win32gui.EnumWindows(enum_windows_proc, window_classes)
            return window_classes[0] if window_classes else ""
            
        except (ImportError, OSError, AttributeError) as e:
            print(f"Window class detection error: {e}")
            return ""
        except Exception as e:
            print(f"Unexpected window class error: {e}")
            return ""
    
    def _is_text_editor_window(self, class_name: str) -> bool:
        """Check if window is likely a text editor"""
        try:
            text_classes = [
                'notepad', 'wordpad', 'edit', 'scintilla', 'richedit',
                'chrome', 'firefox', 'edge', 'vscode', 'sublime',
                'atom', 'vim', 'emacs', 'code'
            ]
            
            if any(text_class in class_name for text_class in text_classes):
                return True
            
            return False
            
        except (AttributeError, TypeError) as e:
            print(f"Text editor check error: {e}")
            return True  # Default to True if unsure
        except Exception as e:
            print(f"Unexpected text editor check error: {e}")
            return True
    
    def execute_text_and_commands(self, text: str, commands: List[str]) -> str:
        """Execute text typing and commands with improved error handling"""
        try:
            results = []
            
            # Type the text if not empty
            if text.strip():
                success = self.type_text(text)
                if success:
                    results.append("✅ Text typed")
                else:
                    results.append("❌ Text typing failed")
            
            # Execute commands
            for command in commands:
                success = self.execute_command(command)
                if success:
                    results.append(f"✅ Command: {command}")
                else:
                    results.append(f"❌ Command failed: {command}")
            
            return " • ".join(results) if results else "No actions performed"
            
        except Exception as e:
            error_msg = f"❌ Execution error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _detect_active_text_area(self):
        """Detect if there's an active text input area"""
        try:
            # Get the currently focused window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return self._simple_text_area_fallback()
            
            # Get window class name to determine if it's a text input
            class_name = win32gui.GetClassName(hwnd)
            
            # Common text input window classes
            text_classes = [
                'Edit',           # Standard Windows text box
                'RichEdit',       # Rich text editor
                'RichEdit20A',    # Rich text editor variant
                'RichEdit20W',    # Rich text editor variant
                'TMemo',          # Delphi memo
                'TEdit',          # Delphi edit
                'Chrome_WidgetWin_1',  # Chrome/Edge text areas
                'Notepad',        # Notepad
                'WordPadClass',   # WordPad
            ]
            
            # Check if the focused window is a text input
            if any(text_class in class_name for text_class in text_classes):
                return True
            
            # Additional check for web browsers and modern apps
            window_title = win32gui.GetWindowText(hwnd)
            
            # Check for common text editor applications
            text_apps = [
                'notepad', 'wordpad', 'code', 'sublime', 'atom', 
                'vim', 'emacs', 'nano', 'textedit', 'word', 'excel',
                'chrome', 'firefox', 'edge', 'brave', 'opera'
            ]
            
            if any(app in window_title.lower() for app in text_apps):
                return True
            
            # Fall back to simple detection
            return self._simple_text_area_fallback()
                
        except Exception as e:
            # If Windows API detection fails, use simple fallback
            print(f"Advanced text area detection failed: {e}")
            return self._simple_text_area_fallback()
    
    def _simple_text_area_fallback(self):
        """Simple fallback text area detection"""
        try:
            # Store current clipboard content
            import pyperclip
            original_clipboard = ""
            try:
                original_clipboard = pyperclip.paste()
            except:
                pass
            
            # Try to select all text (Ctrl+A) to see if there's a text area
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.1)
            
            # Try to copy to see if anything was selected
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.1)
            
            # Check if clipboard changed (indicating text was selected)
            try:
                current_clipboard = pyperclip.paste()
                has_text_area = current_clipboard != original_clipboard
                
                # Restore original clipboard
                pyperclip.copy(original_clipboard)
                
                return has_text_area
            except:
                # If clipboard detection fails, assume there's a text area
                return True
                
        except Exception as e:
            # If all detection fails, assume there's a text area to avoid blocking
            print(f"Simple text area detection failed: {e}")
            return True
    
    def _disable_system_sounds(self):
        """Temporarily disable Windows system sounds"""
        try:
            # Disable Windows default beep
            import ctypes
            import ctypes.wintypes
            
            # Get handle to kernel32
            kernel32 = ctypes.windll.kernel32
            
            # Call Beep with 0 frequency to disable
            kernel32.Beep(0, 0)
            
        except Exception:
            pass  # Ignore if we can't disable sounds
    
    def _enable_system_sounds(self):
        """Re-enable Windows system sounds"""
        try:
            # Re-enable by calling with normal frequency
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.Beep(1000, 1)  # Brief beep to re-enable
            
        except Exception:
            pass  # Ignore if we can't enable sounds
    
    def _execute_command(self, command: str):
        """Execute a single command (stub)"""
        # TODO: Implement command execution
        # Example commands: enter, tab, copy, paste, etc.
        pass
    
    def set_type_delay(self, delay: float):
        """Set typing delay"""
        self.type_delay = delay 