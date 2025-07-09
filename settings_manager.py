# v3_PTT/settings_manager.py
# JSON settings persistence manager
# Purpose: Save/load application settings
# Dependencies: json, os

import json
import os
from typing import Dict, Any, Optional


class SettingsManager:
    """Manages application settings persistence"""
    
    def __init__(self, settings_file: str = "v3_ptt_settings.json"):
        # Use the original settings file name to maintain compatibility
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Check for the file in the parent directory (project root)
        parent_dir = os.path.dirname(script_dir)
        self.settings_file = os.path.join(parent_dir, settings_file)
        
        # If not found in parent, check current directory
        if not os.path.exists(self.settings_file):
            self.settings_file = os.path.join(script_dir, settings_file)
        
        # Default settings
        self.default_settings = {
            "hotkey": {"type": "keyboard", "key": "shift"},
            "selected_device_index": -1,
            "type_delay": 1.0,
            "always_on_top": True,
            "window_position": None,
            "whisper_model_size": "small",
            "copy_clipboard": True,
            "clear_clipboard_on_close": False,
            "english_only": True,  # Default to English-only for better performance
            "technical_filter": True,  # Enable text normalization by default
            "mic_muted": False,
            "download_url": "https://openaipublic.azureedge.net/main/whisper/models",
            
            # New Whisper optimization settings
            "whisper_language": "en",  # "auto" for auto-detection
            "whisper_temperature": 0.0,  # 0.0 = deterministic, higher = more random
            "whisper_best_of": 5,  # Number of attempts (1-5)
            "whisper_beam_size": 5,  # Beam search size (1-10)
            "whisper_no_speech_threshold": 0.6,  # Silence detection (0.0-1.0)
            "whisper_word_timestamps": True,  # Get word-level timing info
            "whisper_show_confidence": True  # Show confidence metrics in console
        }
        self.settings = self.default_settings.copy()
        self._load_settings()
        self._clean_invalid_settings()
        
        print(f"Settings file location: {self.settings_file}")  # Debug
    
    def _load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    
                    # Clean merge: only use JSON values, fill missing with defaults
                    self.settings = self.default_settings.copy()
                    self.settings.update(loaded_settings)
                    print(f"Settings loaded from {self.settings_file}")
            else:
                print(f"Settings file not found, using defaults")
                self.save_settings()  # Create default settings file
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Settings JSON error: {e}")
            print("Using default settings")
            self.save_settings()  # Overwrite corrupted file with defaults
        except (OSError, IOError) as e:
            print(f"❌ Settings file error: {e}")
            print("Using default settings")
        except Exception as e:
            print(f"❌ Unexpected settings load error: {e}")
            print("Using default settings")
    
    def _clean_invalid_settings(self):
        """Remove any invalid or leftover settings that aren't in defaults"""
        try:
            # Get list of valid keys from defaults
            valid_keys = set(self.default_settings.keys())
            current_keys = set(self.settings.keys())
            
            # Find invalid keys
            invalid_keys = current_keys - valid_keys
            
            if invalid_keys:
                print(f"Removing invalid settings keys: {invalid_keys}")
                for key in invalid_keys:
                    del self.settings[key]
                
                # Save cleaned settings
                self.save_settings()
        except Exception as e:
            print(f"❌ Error cleaning settings: {e}")
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"Settings saved to {self.settings_file}")
        except (OSError, IOError) as e:
            print(f"❌ Settings save error: {e}")
        except (TypeError, ValueError) as e:
            print(f"❌ Settings serialization error: {e}")
        except Exception as e:
            print(f"❌ Unexpected settings save error: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Set a specific setting value"""
        try:
            self.settings[key] = value
            self.save_settings()
        except Exception as e:
            print(f"Error setting {key}: {e}")
    
    def get_hotkey(self) -> Dict[str, Any]:
        """Get hotkey configuration"""
        return self.settings['hotkey']
    
    def set_hotkey(self, hotkey_config: Dict[str, Any]):
        """Set hotkey configuration"""
        self.settings['hotkey'] = hotkey_config
        self.save_settings()
    
    def get_device_index(self) -> Optional[int]:
        """Get audio device index"""
        device_index = self.settings.get('selected_device_index')
        return device_index if device_index != -1 else None
    
    def set_device_index(self, index: Optional[int]):
        """Set audio device index"""
        self.settings['selected_device_index'] = index if index is not None else -1
        self.save_settings()
    
    def get_type_delay(self) -> float:
        """Get post-processing delay in seconds"""
        return self.settings.get('type_delay', 0.5)
    
    def set_type_delay(self, delay: float):
        """Set post-processing delay in seconds"""
        self.settings['type_delay'] = max(0.0, min(5.0, delay))  # Clamp to 0-5 seconds
        self.save_settings()
    
    def get_always_on_top(self) -> bool:
        """Get always on top setting"""
        return self.settings.get('always_on_top', True)
    
    def set_always_on_top(self, on_top: bool):
        """Set always on top setting"""
        self.settings['always_on_top'] = on_top
        self.save_settings()
    
    def get_window_position(self) -> Optional[str]:
        """Get saved window position"""
        return self.settings.get('window_position')
    
    def set_window_position(self, position: str):
        """Set window position"""
        self.set_setting('window_position', position)
    
    def get_whisper_model_size(self) -> str:
        """Get Whisper model size"""
        return self.settings.get('whisper_model_size', 'base')
    
    def set_whisper_model_size(self, size: str):
        """Set Whisper model size"""
        # Extract base model name (remove language suffix if present)
        base_model = size.split('.')[0]
        
        valid_sizes = ['tiny', 'base', 'small', 'medium', 'large']
        if base_model in valid_sizes:
            self.settings['whisper_model_size'] = size  # Store full name including .en if present
            self.save_settings()
            return True
        else:
            print(f"❌ Invalid model size: {size} (base: {base_model})")
            return False
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        try:
            self.settings = self.default_settings.copy()
            self.save_settings()
            print("Settings reset to defaults")
        except Exception as e:
            print(f"❌ Error resetting settings: {e}")
    
    def get_hotkey_display_text(self) -> str:
        """Get display text for current hotkey"""
        hotkey = self.get_hotkey()
        if hotkey['type'] == 'key':
            key = hotkey.get('key', 'space')
            return key.title()
        elif hotkey['type'] == 'mouse':
            button = hotkey.get('button', 'left')
            return f"{button.title()} Click"
        else:
            return "Unknown"
    
    def get_copy_clipboard(self) -> bool:
        """Get copy to clipboard setting"""
        return self.settings.get('copy_clipboard', True)
    
    def set_copy_clipboard(self, copy: bool):
        """Set copy to clipboard setting"""
        self.settings['copy_clipboard'] = copy
        self.save_settings()
    
    def get_clear_clipboard_on_close(self) -> bool:
        """Get clear clipboard on close setting"""
        return self.settings.get("clear_clipboard_on_close", False)
    
    def set_clear_clipboard_on_close(self, enabled: bool):
        """Set clear clipboard on close setting"""
        self.settings["clear_clipboard_on_close"] = enabled
        self.save_settings()
    
    def get_english_only(self) -> bool:
        """Get English-only setting"""
        return self.settings.get("english_only", True)
    
    def set_english_only(self, enabled: bool):
        """Set English-only setting"""
        self.settings["english_only"] = enabled
        self.save_settings()
    
    def get_technical_filter(self) -> bool:
        """Get technical filter (text normalization) setting"""
        return self.settings.get("technical_filter", True)
    
    def set_technical_filter(self, enabled: bool):
        """Set technical filter (text normalization) setting"""
        self.settings["technical_filter"] = enabled
        self.save_settings()
    
    # New Whisper optimization setting getters
    def get_whisper_language(self) -> str:
        """Get Whisper language setting"""
        return self.settings.get("whisper_language", "en")
    
    def set_whisper_language(self, language: str):
        """Set Whisper language setting"""
        self.settings["whisper_language"] = language
        self.save_settings()
    
    def get_whisper_temperature(self) -> float:
        """Get Whisper temperature setting"""
        return self.settings.get("whisper_temperature", 0.0)
    
    def set_whisper_temperature(self, temperature: float):
        """Set Whisper temperature setting"""
        self.settings["whisper_temperature"] = max(0.0, min(1.0, temperature))
        self.save_settings()
    
    def get_whisper_best_of(self) -> int:
        """Get Whisper best_of setting"""
        return self.settings.get("whisper_best_of", 5)
    
    def set_whisper_best_of(self, best_of: int):
        """Set Whisper best_of setting"""
        self.settings["whisper_best_of"] = max(1, min(10, best_of))
        self.save_settings()
    
    def get_whisper_beam_size(self) -> int:
        """Get Whisper beam_size setting"""
        return self.settings.get("whisper_beam_size", 5)
    
    def set_whisper_beam_size(self, beam_size: int):
        """Set Whisper beam_size setting"""
        self.settings["whisper_beam_size"] = max(1, min(10, beam_size))
        self.save_settings()
    
    def get_whisper_no_speech_threshold(self) -> float:
        """Get Whisper no_speech_threshold setting"""
        return self.settings.get("whisper_no_speech_threshold", 0.6)
    
    def set_whisper_no_speech_threshold(self, threshold: float):
        """Set Whisper no_speech_threshold setting"""
        self.settings["whisper_no_speech_threshold"] = max(0.0, min(1.0, threshold))
        self.save_settings()
    
    def get_whisper_word_timestamps(self) -> bool:
        """Get Whisper word_timestamps setting"""
        return self.settings.get("whisper_word_timestamps", True)
    
    def set_whisper_word_timestamps(self, enabled: bool):
        """Set Whisper word_timestamps setting"""
        self.settings["whisper_word_timestamps"] = enabled
        self.save_settings()
    
    def get_whisper_show_confidence(self) -> bool:
        """Get Whisper show_confidence setting"""
        return self.settings.get("whisper_show_confidence", True)
    
    def set_whisper_show_confidence(self, enabled: bool):
        """Set Whisper show_confidence setting"""
        self.settings["whisper_show_confidence"] = enabled
        self.save_settings()
    
    def get_mic_muted(self) -> bool:
        """Get microphone muted setting"""
        return self.settings.get('mic_muted', False)
    
    def set_mic_muted(self, muted: bool):
        """Set microphone muted setting"""
        self.settings['mic_muted'] = muted
        self.save_settings()
    
    def get_all_settings(self) -> Dict:
        """Get all settings as dictionary"""
        return self.settings.copy()
    
    def update_settings(self, new_settings: Dict):
        """Update multiple settings at once"""
        try:
            self.settings.update(new_settings)
            self.save_settings()
            print("Settings updated successfully")
        except Exception as e:
            print(f"❌ Error updating settings: {e}")
    
    def validate_settings(self) -> bool:
        """Validate current settings and fix any issues"""
        try:
            # Check model size
            model_size = self.settings.get('whisper_model_size', 'base')
            base_model = model_size.split('.')[0]  # Extract base name
            valid_sizes = ['tiny', 'base', 'small', 'medium', 'large']
            
            if base_model not in valid_sizes:
                self.settings['whisper_model_size'] = 'base'
                print(f"Fixed invalid model size: {model_size} -> base")
            
            # Check delay value
            delay = self.settings.get('type_delay', 0.5)
            if not isinstance(delay, (int, float)) or delay < 0 or delay > 3:
                self.settings['type_delay'] = 0.5
                print("Fixed invalid delay value")
            
            # Check boolean values
            for key in ['always_on_top', 'copy_clipboard', 'clear_clipboard_on_close']:
                if not isinstance(self.settings.get(key), bool):
                    self.settings[key] = self.default_settings[key]
                    print(f"Fixed invalid {key} value")
            
            # Check hotkey configuration
            hotkey = self.settings.get('hotkey', {})
            if not isinstance(hotkey, dict) or 'type' not in hotkey:
                self.settings['hotkey'] = self.default_settings['hotkey']
                print("Fixed invalid hotkey configuration")
            
            self.save_settings()
            return True
            
        except Exception as e:
            print(f"❌ Settings validation error: {e}")
            return False 