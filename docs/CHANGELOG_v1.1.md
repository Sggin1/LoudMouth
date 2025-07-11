# LoudMouth v1.1 Changelog

## Version 1.1.0 - January 2025

### 🎯 Major Features

#### Enhanced Hotkey System
- **Combo Key Support**: Now supports modifier combinations (Ctrl+X, Alt+Space, Shift+Enter)
- **Improved Hotkey Capture**: New intuitive UI with Single/Combo/Reset/Exit buttons
- **Mouse Button Support**: Right-click, middle-click, and side buttons can be hotkeys
- **Real-time Feedback**: Visual confirmation during hotkey selection
- **Left-click Protection**: Prevents accidental left-click hotkey assignment

#### Settings Window Improvements
- **Apply Button Intelligence**: Only enabled when actual changes are made
- **Color-coded Apply Button**: Gray when disabled, green when changes detected
- **Window Management**: Settings window properly stays on top after applying changes
- **Auto-refresh Models**: Model list updates when downloader completes or settings close

### 🔧 Technical Improvements

#### Code Refactoring
- **Settings Manager**: Reduced ~170 lines of duplicate code using generic getter/setter pattern
- **Dynamic Attribute Access**: Maintains backward compatibility while improving maintainability
- **Validation System**: Centralized validators for numeric settings with automatic bounds checking
- **Error Handling**: Better exception handling throughout the application

#### Model Management
- **Simplified Model Counting**: Only counts models in `./models/` folder (no cache confusion)
- **Clear Status Display**: Shows "✅ X models ready" without complex breakdowns
- **No Cache Usage**: Removed all `~/.cache/whisper/` directory dependencies
- **Download Integration**: Model count updates automatically after downloads complete

### 🐛 Bug Fixes
- Fixed settings window closing unexpectedly when reverting changes
- Fixed window jumping between main app and settings when applying changes
- Fixed model count not updating after downloading new models
- Fixed error messages appearing in UI status (now logged to console only)
- Fixed hotkey capture dialog not working properly
- Fixed memory cleanup on application exit

### 📝 Documentation
- Added `SETTINGS_MANAGER_DESIGN.md` explaining the API pattern
- Added `MODEL_STATUS_UPDATE_FIX.md` documenting model management changes
- Improved code comments and docstrings

### 🎨 UI/UX Enhancements
- Apply button shows "Applied!" confirmation before disabling
- Model status updates without showing error messages to user
- Hotkey display shows user-friendly names (e.g., "Ctrl+Space" instead of "ctrl+space")
- Settings window maintains focus when applying changes
- Cleaner visual feedback for all user actions

### ⚡ Performance
- Removed unnecessary 5-second periodic model status checks
- More efficient model scanning (only when needed)
- Better thread management and cleanup
- Reduced window redraw operations

### 🔄 Backward Compatibility
- All existing settings preserved
- Dynamic method generation maintains old API
- Smooth upgrade path from v1.0

## Upgrade Notes
- Your existing settings will be preserved
- The new hotkey system is fully backward compatible
- Model files remain in the same `./models/` directory
- No action required for existing users