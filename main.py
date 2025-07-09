# v3_PTT/main.py
# Main application entry point
# Purpose: Orchestrate all components for v3 PTT
# Dependencies: All v3_PTT modules

from audio_handler import AudioHandler
from ui_manager import UIManager
from settings_manager import SettingsManager
from hotkey_manager import HotkeyManager
from command_structure import CommandParser, CommandExecutor
import sys
import pyperclip
import threading
import time
import signal
import atexit


class V3PTTApp:
    """Main application class that coordinates all components"""
    
    def __init__(self):
        # Initialize components
        self.settings = SettingsManager()
        self.command_parser = CommandParser()
        self.command_executor = CommandExecutor(self.settings.get_type_delay())
        
        # Initialize UI first (needed for status callbacks)
        self.ui = UIManager(
            on_start_recording=self.start_recording,
            on_stop_recording=self.stop_recording,
            on_open_settings=self.open_settings,
            on_mic_mute_toggle=self.toggle_mic_mute
        )
        
        # Initialize audio handler with callbacks (after UI)
        self.audio_handler = AudioHandler(
            self.settings,
            status_callback=self.on_status_update,
            transcript_callback=self.on_transcript_ready
        )
        
        # Initialize hotkey manager with callbacks
        self.hotkey_manager = HotkeyManager(
            on_hotkey_press=self.start_recording,
            on_hotkey_release=self.stop_recording
        )
        
        # Apply settings
        self.apply_settings()
        
        # Update model status in UI
        self.update_model_status()
        
        # Start audio level monitoring
        self.monitoring_active = True
        self.start_audio_monitoring()
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def apply_settings(self):
        """Apply loaded settings to all components"""
        try:
            self.audio_handler.set_device(self.settings.get_device_index())
            self.hotkey_manager.set_hotkey(self.settings.get_hotkey())
            self.ui.update_hotkey_display(self.settings.get_hotkey_display_text())
            self.ui.set_always_on_top(self.settings.get_always_on_top())
            self.command_executor.set_type_delay(self.settings.get_type_delay())
            
            # Apply mic mute state and update UI
            mic_muted = self.settings.get_mic_muted()
            self.audio_handler.set_mute(mic_muted)
            self.ui.set_mic_mute_state(mic_muted)
            
            # Apply technical filter setting
            technical_filter_enabled = self.settings.get_technical_filter()
            if technical_filter_enabled:
                self.command_parser.enable_text_normalization()
            else:
                self.command_parser.disable_text_normalization()
            
            print(f"Settings applied - Hotkey: {self.settings.get_hotkey_display_text()}, Technical Filter: {'Enabled' if technical_filter_enabled else 'Disabled'}")
        except Exception as e:
            print(f"Error applying settings: {e}")
            self.ui.update_status(f"Settings error: {str(e)}")
    
    def start_audio_monitoring(self):
        """Start monitoring audio levels in a separate thread"""
        def monitor_audio():
            while self.monitoring_active:
                try:
                    # Only monitor if not recording to avoid device conflicts
                    if not self.audio_handler.is_recording:
                        level = self.audio_handler.get_audio_level()
                        # Update UI in main thread - fix lambda closure issue
                        self.ui.root.after(0, lambda l=level: self.ui.update_audio_level(l))
                    time.sleep(0.2)  # Update every 200ms (less frequent to reduce load)
                except Exception as e:
                    # Log errors but don't spam console
                    print(f"Audio monitoring error: {e}")
                    time.sleep(0.5)  # Wait longer on error
        
        # Start monitoring in background thread
        self.monitoring_thread = threading.Thread(target=monitor_audio, daemon=True)
        self.monitoring_thread.start()
        print("Audio monitoring thread started")
    
    def start_recording(self):
        """Start audio recording"""
        self.audio_handler.start_recording()
    
    def stop_recording(self):
        """Stop audio recording"""
        self.audio_handler.stop_recording()
    
    def toggle_mic_mute(self, muted: bool):
        """Toggle microphone mute state and save to settings"""
        self.audio_handler.set_mute(muted)
        self.settings.set_mic_muted(muted)
    
    def on_status_update(self, status: str):
        """Handle status updates from audio handler"""
        self.ui.update_status(status)
    
    def on_transcript_ready(self, text: str):
        """Handle completed transcription"""
        self.ui.update_transcript(text)
        
        if not text.strip():
            self.ui.update_status("No speech detected")
            return
        
        # Parse for commands and normalize text FIRST
        clean_text, commands = self.command_parser.parse_commands(text)
        
        # Copy normalized text to clipboard if enabled
        clipboard_success = False
        if self.settings.get_copy_clipboard():
            try:
                clipboard_text = clean_text.strip()
                print(f"Copying to clipboard: '{clipboard_text}'")
                
                # Use a more robust clipboard copy method
                import subprocess
                subprocess.run(['powershell', '-c', f'Set-Clipboard -Value "{clipboard_text}"'], 
                             check=True, capture_output=True)
                
                # Verify with pyperclip
                import time
                time.sleep(0.1)  # Small delay to ensure clipboard is updated
                clipboard_content = pyperclip.paste()
                
                if clipboard_content == clipboard_text:
                    print("✅ Clipboard copy successful")
                    clipboard_success = True
                else:
                    print("❌ Clipboard verification failed, trying fallback...")
                    # Fallback to pyperclip
                    pyperclip.copy(clipboard_text)
                    clipboard_success = True
                
            except Exception as e:
                print(f"❌ Clipboard error: {e}")
                # Fallback to pyperclip if PowerShell fails
                try:
                    pyperclip.copy(clipboard_text)
                    clipboard_success = True
                except Exception:
                    clipboard_success = False
        
        # Execute text and commands - this returns a status message, not text to type
        result = self.command_executor.execute_text_and_commands(clean_text, commands)
        
        # Show combined result in UI status bar
        status_parts = []
        if clipboard_success:
            status_parts.append("✅ Copied to clipboard")
        if result:
            status_parts.append(result)
        
        if status_parts:
            combined_status = " • ".join(status_parts)
            self.ui.update_status(combined_status)
            # Clear status after 3 seconds to return to "Ready"
            self.ui.root.after(3000, lambda: self.ui.update_status("Ready"))
        else:
            self.ui.update_status("Ready")
    
    def open_settings(self):
        """Open settings window"""
        try:
            from settings_window import SettingsWindow
            settings_window = SettingsWindow(
                self.ui.root,
                self.settings,
                self.audio_handler,
                self.hotkey_manager,
                self.on_settings_changed
            )
        except Exception as e:
            print(f"Settings window error: {e}")
            self.ui.update_status(f"Settings error: {str(e)}")
    
    def on_settings_changed(self):
        """Handle settings changes"""
        self.apply_settings()
        self.update_model_status()
    
    def update_model_status(self):
        """Update model status in UI"""
        try:
            # Get current model info
            current_model = self.settings.get_whisper_model_size()
            model_status = self.audio_handler.get_model_quick_status()
            
            # Combine current model with status
            if "✅" in model_status:
                status_with_model = f"✅ {current_model} active • {model_status}"
            else:
                status_with_model = f"⚠️ {current_model} • {model_status}"
                
            self.ui.update_model_status(status_with_model)
        except Exception as e:
            error_status = f"❌ Model status error: {str(e)}"
            print(error_status)
            self.ui.update_model_status(error_status)
    
    def run(self):
        """Run the application"""
        try:
            self.ui.run()
        except KeyboardInterrupt:
            print("Received keyboard interrupt")
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            return
        
        print("Starting cleanup...")
        self._cleanup_done = True
        
        # Stop monitoring thread first
        self.monitoring_active = False
        
        # Collect all threads that need to be joined
        threads_to_join = []
        
        # Add monitoring thread
        if hasattr(self, 'monitoring_thread') and self.monitoring_thread.is_alive():
            threads_to_join.append(('monitoring', self.monitoring_thread))
        
        # Add audio handler recording thread
        if hasattr(self, 'audio_handler') and hasattr(self.audio_handler, 'recording_thread'):
            if self.audio_handler.recording_thread and self.audio_handler.recording_thread.is_alive():
                threads_to_join.append(('recording', self.audio_handler.recording_thread))
        
        # Wait for all threads to complete
        for thread_name, thread in threads_to_join:
            try:
                print(f"Waiting for {thread_name} thread to finish...")
                thread.join(timeout=2.0)
                if thread.is_alive():
                    print(f"Warning: {thread_name} thread did not finish cleanly")
                else:
                    print(f"{thread_name} thread finished")
            except Exception as e:
                print(f"Error joining {thread_name} thread: {e}")
        
        # Clean up audio handler (includes persistent streams)
        if hasattr(self, 'audio_handler'):
            try:
                self.audio_handler.cleanup()
                print("Audio handler cleaned up")
            except Exception as e:
                print(f"Error cleaning up audio handler: {e}")
        
        # Clean up hotkey manager
        if hasattr(self, 'hotkey_manager'):
            try:
                self.hotkey_manager.cleanup()
                print("Hotkey manager cleaned up")
            except Exception as e:
                print(f"Error cleaning up hotkey manager: {e}")
        
        # Clear clipboard if enabled
        if hasattr(self, 'settings'):
            try:
                if self.settings.get_clear_clipboard_on_close():
                    pyperclip.copy("")  # Clear clipboard
                    print("Clipboard cleared")
            except Exception as e:
                print(f"Error clearing clipboard: {e}")
        
        # Clean up UI
        if hasattr(self, 'ui'):
            try:
                self.ui.destroy()
                print("UI destroyed")
            except Exception as e:
                print(f"Error destroying UI: {e}")
        
        print("Cleanup complete")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for clean shutdown"""
        print(f"Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)


def main():
    """Application entry point"""
    app = V3PTTApp()
    app.run()


if __name__ == "__main__":
    main() 