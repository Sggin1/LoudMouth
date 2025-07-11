# PTT/LoudMouth/settings_manager.py
# JSON settings persistence manager - refactored to reduce duplication
# Purpose: Save/load application settings with dynamic getter/setter
# Dependencies: json, os, typing

import json
import os
from typing import Dict, Any, Optional


class SettingsManager:
    """Manages application settings persistence"""
    
    def __init__(self, settings_file: str = "v3_ptt_settings.json"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(script_dir)
        self.settings_file = os.path.join(parent_dir, settings_file)
        
        if not os.path.exists(self.settings_file):
            self.settings_file = os.path.join(script_dir, settings_file)
        
        # Default settings with type hints for validation
        self.default_settings = {
            "hotkey": {"type": "key", "key": "shift"},
            "selected_device_index": -1,
            "type_delay": 1.0,
            "always_on_top": True,
            "window_position": None,
            "whisper_model_size": "small",
            "copy_clipboard": True,
            "clear_clipboard_on_close": True,
            "english_only": True,
            "technical_filter": True,
            "mic_muted": True,
            "download_url": "https://openaipublic.azureedge.net/main/whisper/models",
            "whisper_language": "en",
            "whisper_temperature": 0.0,
            "whisper_best_of": 5,
            "whisper_beam_size": 5,
            "whisper_no_speech_threshold": 0.6,
            "whisper_word_timestamps": True,
            "whisper_show_confidence": True
        }
        
        # Validation rules for settings
        self.validators = {
            "type_delay": lambda v: max(0.0, min(5.0, float(v))),
            "whisper_temperature": lambda v: max(0.0, min(1.0, float(v))),
            "whisper_best_of": lambda v: max(1, min(10, int(v))),
            "whisper_beam_size": lambda v: max(1, min(10, int(v))),
            "whisper_no_speech_threshold": lambda v: max(0.0, min(1.0, float(v)))
        }
        
        self.settings = self.default_settings.copy()
        self._load_settings()
        self._clean_invalid_settings()
        print(f"Settings file location: {self.settings_file}")
    
    def _load_settings(self):
        """Load settings from JSON file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings = self.default_settings.copy()
                    self.settings.update(loaded_settings)
                    print(f"Settings loaded from {self.settings_file}")
            else:
                print(f"Settings file not found, using defaults")
                self.save_settings()
        except (json.JSONDecodeError, ValueError) as e:
            print(f"❌ Settings JSON error: {e}")
            print("Using default settings")
            self.save_settings()
        except Exception as e:
            print(f"❌ Unexpected settings load error: {e}")
            print("Using default settings")
    
    def _clean_invalid_settings(self):
        """Remove invalid settings not in defaults"""
        try:
            valid_keys = set(self.default_settings.keys())
            current_keys = set(self.settings.keys())
            invalid_keys = current_keys - valid_keys
            
            if invalid_keys:
                print(f"Removing invalid settings keys: {invalid_keys}")
                for key in invalid_keys:
                    del self.settings[key]
                self.save_settings()
        except Exception as e:
            print(f"❌ Error cleaning settings: {e}")
    
    def save_settings(self):
        """Save current settings to JSON file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            print(f"Settings saved to {self.settings_file}")
        except Exception as e:
            print(f"❌ Settings save error: {e}")
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Generic getter for any setting"""
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        """Generic setter with optional validation"""
        try:
            if key in self.validators:
                value = self.validators[key](value)
            self.settings[key] = value
            self.save_settings()
        except Exception as e:
            print(f"Error setting {key}: {e}")
    
    # Specific getters/setters for commonly used settings
    def get_hotkey(self) -> Dict[str, Any]:
        return self.get_setting('hotkey')
    
    def set_hotkey(self, hotkey_config: Dict[str, Any]):
        self.set_setting('hotkey', hotkey_config)
    
    def get_device_index(self) -> Optional[int]:
        index = self.get_setting('selected_device_index')
        return index if index != -1 else None
    
    def set_device_index(self, index: Optional[int]):
        self.set_setting('selected_device_index', index if index is not None else -1)
    
    def get_whisper_model_size(self) -> str:
        return self.get_setting('whisper_model_size', 'base')
    
    def set_whisper_model_size(self, size: str) -> bool:
        base_model = size.split('.')[0]
        valid_sizes = ['tiny', 'base', 'small', 'medium', 'large']
        if base_model in valid_sizes:
            self.set_setting('whisper_model_size', size)
            return True
        print(f"❌ Invalid model size: {size} (base: {base_model})")
        return False
    
    def get_hotkey_display_text(self) -> str:
        """Get display text for current hotkey"""
        hotkey = self.get_hotkey()
        if hotkey['type'] == 'key':
            if 'combo' in hotkey:
                combo = hotkey['combo']
                modifier = combo.get('modifier', '').title()
                key = combo.get('key', '')
                
                key_display = {
                    'space': 'Space',
                    'enter': 'Enter'
                }.get(key, key.upper() if len(key) == 1 else key.title())
                
                return f"{modifier}+{key_display}"
            
            key = hotkey.get('key', 'space')
            return {
                'space': 'Space',
                'enter': 'Enter',
                'ctrl': 'Ctrl',
                'alt': 'Alt',
                'shift': 'Shift'
            }.get(key, key.upper())
        elif hotkey['type'] == 'mouse':
            button = hotkey.get('button', 'left')
            return f"{button.title()} Click"
        return "Unknown"
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        try:
            self.settings = self.default_settings.copy()
            self.save_settings()
            print("Settings reset to defaults")
        except Exception as e:
            print(f"❌ Error resetting settings: {e}")
    
    def validate_settings(self) -> bool:
        """Validate current settings and fix issues"""
        try:
            # Validate model size
            model_size = self.get_setting('whisper_model_size', 'base')
            base_model = model_size.split('.')[0]
            if base_model not in ['tiny', 'base', 'small', 'medium', 'large']:
                self.set_setting('whisper_model_size', 'base')
                print(f"Fixed invalid model size: {model_size} -> base")
            
            # Validate numeric values
            for key, validator in self.validators.items():
                if key in self.settings:
                    self.settings[key] = validator(self.settings[key])
            
            # Validate boolean values
            bool_keys = ['always_on_top', 'copy_clipboard', 'clear_clipboard_on_close',
                        'english_only', 'technical_filter', 'mic_muted',
                        'whisper_word_timestamps', 'whisper_show_confidence']
            for key in bool_keys:
                if key in self.settings and not isinstance(self.settings[key], bool):
                    self.settings[key] = self.default_settings[key]
                    print(f"Fixed invalid {key} value")
            
            # Validate hotkey configuration
            hotkey = self.get_setting('hotkey', {})
            if not isinstance(hotkey, dict) or 'type' not in hotkey:
                self.set_setting('hotkey', self.default_settings['hotkey'])
                print("Fixed invalid hotkey configuration")
            
            self.save_settings()
            return True
        except Exception as e:
            print(f"❌ Settings validation error: {e}")
            return False
    
    # Dynamic attribute access for backward compatibility
    def __getattr__(self, name):
        """Dynamic getter for settings using attribute access"""
        if name.startswith('get_') and name != 'get_setting':
            key = name[4:]  # Remove 'get_' prefix
            # Return a method that gets the setting
            def getter():
                return self.get_setting(key, self.default_settings.get(key))
            return getter
        elif name.startswith('set_') and name != 'set_setting':
            key = name[4:]  # Remove 'set_' prefix
            # Return a method that sets the setting
            def setter(value):
                return self.set_setting(key, value)
            return setter
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")