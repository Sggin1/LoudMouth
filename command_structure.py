# v3_PTT/command_structure.py
# Command parsing and execution framework (stub)
# Purpose: Future expansion hook for voice commands
# Dependencies: pyautogui (for future implementation)

from typing import List, Dict, Any, Optional
import pyautogui
import time
import os
from text_normalizer import text_normalizer

# win32gui is only available on Windows
try:
    import win32gui
    HAS_WIN32 = True
except ImportError:
    HAS_WIN32 = False


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
        if not HAS_WIN32:
            return ""
        try:
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

        except (OSError, AttributeError) as e:
            print(f"Window class detection error: {e}")
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
        if not HAS_WIN32:
            # On non-Windows platforms, assume text area is available
            return True
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return True

            class_name = win32gui.GetClassName(hwnd)

            text_classes = [
                'Edit', 'RichEdit', 'RichEdit20A', 'RichEdit20W',
                'TMemo', 'TEdit', 'Chrome_WidgetWin_1', 'Notepad', 'WordPadClass',
            ]

            if any(text_class in class_name for text_class in text_classes):
                return True

            window_title = win32gui.GetWindowText(hwnd)
            text_apps = [
                'notepad', 'wordpad', 'code', 'sublime', 'atom',
                'vim', 'emacs', 'nano', 'textedit', 'word', 'excel',
                'chrome', 'firefox', 'edge', 'brave', 'opera'
            ]

            if any(app in window_title.lower() for app in text_apps):
                return True

            # Default to True to avoid blocking text input
            return True

        except (OSError, AttributeError) as e:
            print(f"Text area detection failed: {e}")
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