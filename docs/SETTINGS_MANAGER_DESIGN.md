# PTT/LoudMouth/SETTINGS_MANAGER_DESIGN.md
# Settings Manager Design Pattern
# Explains the generic + specific method pattern

## Design Pattern

The settings_manager.py uses a two-tier method pattern:

### 1. Generic Methods
```python
get_setting(key, default) -> Any
set_setting(key, value)
```
- Handle any setting dynamically
- Apply validation if defined
- Single point for persistence

### 2. Specific Methods
```python
get_hotkey() -> Dict[str, Any]
set_hotkey(hotkey_config: Dict[str, Any])
get_device_index() -> Optional[int]
set_device_index(index: Optional[int])
```

## Benefits
- **Type Safety**: IDE knows return types
- **Custom Logic**: e.g., device_index returns None instead of -1
- **Validation**: Centralized in validators dict
- **Backward Compatibility**: Existing code continues to work
- **Clear API**: Developers see available settings

## Example Usage
```python
# Generic way
model = settings.get_setting('whisper_model_size', 'base')

# Specific way (preferred)
model = settings.get_whisper_model_size()  # Returns str

# Dynamic attribute access (backward compat)
delay = settings.get_type_delay()  # Auto-generated
```

This is NOT duplication 