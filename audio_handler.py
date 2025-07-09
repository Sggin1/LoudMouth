# v3_PTT/audio_handler.py
# Audio recording and Whisper transcription handler
# Purpose: HIPAA-compliant offline speech recognition
# Dependencies: whisper, pyaudio, numpy, tempfile

import whisper
import pyaudio
import wave
import tempfile
import os
import numpy as np
import threading
import time
from typing import Optional, List, Dict, Callable

from model_manager import ModelManager


class AudioHandler:
    """Handles audio recording and Whisper transcription"""
    
    def __init__(self, settings_manager, status_callback: Optional[Callable] = None, 
                 transcript_callback: Optional[Callable] = None):
        self.settings_manager = settings_manager
        self.status_callback = status_callback
        self.transcript_callback = transcript_callback
        self.whisper_model = None
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # Whisper optimal rate
        self.chunk = 1024
        self.selected_device_index = None
        self.is_recording = False
        self.temp_file_path = None
        self.temp_fd = None  # Track file descriptor for proper cleanup
        self.is_muted = False
        self.recording_thread = None  # Track recording thread
        
        # Persistent audio stream for level monitoring
        self.level_stream = None
        self.level_pyaudio = None  # Persistent PyAudio instance
        
        # Initialize model manager
        self.model_manager = ModelManager(status_callback=self._update_status)
        
        # Load Whisper model on startup (async to prevent UI blocking)
        self._load_whisper_model_async()
    
    def _load_whisper_model_async(self):
        """Load Whisper model asynchronously to prevent UI blocking"""
        def load_model():
            try:
                model_size = self.settings_manager.get_whisper_model_size()
                self._update_status(f"Loading {model_size} model...")
                
                if not self.model_manager.is_model_available(model_size):
                    self._handle_model_download(model_size)
                else:
                    self._load_local_model(model_size)
                
                self._update_status(f"✅ {model_size} model ready")
                print(f"Whisper model '{model_size}' loaded with CPU/FP32 configuration")
                
            except Exception as e:
                self._handle_model_error(e)
        
        # Start model loading in background thread
        self.model_loading_thread = threading.Thread(target=load_model, daemon=True)
        self.model_loading_thread.start()
    
    def _load_whisper_model(self):
        """Load Whisper model with selected size from settings (synchronous version)"""
        try:
            model_size = self.settings_manager.get_whisper_model_size()
            self._update_status(f"Loading {model_size} model...")
            
            if not self.model_manager.is_model_available(model_size):
                self._handle_model_download(model_size)
            else:
                self._load_local_model(model_size)
            
            self._update_status(f"✅ {model_size} model ready")
            print(f"Whisper model '{model_size}' loaded with CPU/FP32 configuration")
            
        except Exception as e:
            self._handle_model_error(e)
    
    def _handle_model_download(self, model_size: str):
        """Handle model download process"""
        warning = self.model_manager.get_model_warning(model_size)
        if warning:
            print(warning)
            print("💡 Tip: Run 'python download_models.py' to pre-download all models and avoid freezing.")
        
        self._update_status(f"Downloading {model_size} model (this may take a while)...")
        try:
            self.whisper_model = whisper.load_model(model_size, device="cpu")
            self._update_status(f"✅ {model_size} model downloaded and ready")
        except Exception as e:
            self._update_status(f"❌ Failed to download {model_size} model")
            raise e
    
    def _load_local_model(self, model_size: str):
        """Load model from local path"""
        try:
            model_path = self.model_manager.get_model_path(model_size)
            if model_path:
                self.whisper_model = whisper.load_model(model_path, device="cpu")
                print(f"Loaded model from: {model_path}")
            else:
                self.whisper_model = whisper.load_model(model_size, device="cpu")
                print(f"Loaded model: {model_size}")
        except Exception as e:
            self._update_status(f"❌ Failed to load {model_size} model")
            raise e
    
    def _handle_model_error(self, error: Exception):
        """Handle model loading errors"""
        error_msg = f"Model load error: {str(error)}"
        self._update_status(error_msg)
        print(f"❌ {error_msg}")
        print("💡 Try running 'python download_models.py' to download models properly.")

    def reload_model(self):
        """Reload Whisper model with new size - called when settings change"""
        model_size = "unknown"
        try:
            model_size = self.settings_manager.get_whisper_model_size()
            self._update_status(f"Switching to {model_size} model...")
            
            # Clean up current model first
            if self.whisper_model:
                del self.whisper_model
                self.whisper_model = None
            
            if not self.model_manager.is_model_available(model_size):
                warning = self.model_manager.get_model_warning(model_size)
                if warning:
                    print(warning)
                    print("💡 Next time, run 'python download_models.py' first to avoid this.")
            
            self._load_whisper_model()
        except Exception as e:
            error_msg = f"❌ Error switching to {model_size}: {e}"
            print(error_msg)
            self._update_status(error_msg)
    
    def _update_status(self, message: str):
        """Update status via callback"""
        if self.status_callback:
            self.status_callback(message)
    
    def get_model_status(self) -> Dict:
        """Get model status from model manager"""
        return self.model_manager.get_model_status()
    
    def get_model_quick_status(self) -> str:
        """Get quick model status for UI"""
        return self.model_manager.get_quick_status()
    
    def get_audio_devices(self) -> List[Dict]:
        """Get available audio input devices"""
        devices = []
        p = None
        try:
            p = pyaudio.PyAudio()
            for i in range(p.get_device_count()):
                info = p.get_device_info_by_index(i)
                if info['maxInputChannels'] > 0:
                    devices.append({
                        'index': i,
                        'name': info['name'],
                        'channels': info['maxInputChannels']
                    })
        except Exception as e:
            self._update_status(f"Device enumeration error: {str(e)}")
        finally:
            if p:
                p.terminate()
        return devices
    
    def set_device(self, device_index: Optional[int]):
        """Set audio input device"""
        self.selected_device_index = device_index
        self._reset_level_stream()  # Reset stream when device changes
    
    def set_mute(self, muted: bool):
        """Set microphone mute state"""
        self.is_muted = muted
        if muted:
            self._update_status("Microphone muted")
        else:
            self._update_status("Ready")
    
    def get_mute_state(self) -> bool:
        """Get current mute state"""
        return self.is_muted
    
    def start_recording(self) -> bool:
        """Start audio recording"""
        if self.is_recording or self.is_muted:
            if self.is_muted:
                self._update_status("Microphone is muted")
            return False
        
        try:
            self.is_recording = True
            self._update_status("Recording...")
            
            self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
            self.recording_thread.start()
            return True
            
        except Exception as e:
            self._update_status(f"Recording start error: {str(e)}")
            self.is_recording = False
            return False
    
    def stop_recording(self) -> bool:
        """Stop audio recording"""
        if not self.is_recording:
            return False
        
        self.is_recording = False
        self._update_status("Processing...")
        return True
    
    def _record_audio(self):
        """Record audio to temporary file"""
        p = None
        stream = None
        try:
            p = pyaudio.PyAudio()
            stream = p.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.selected_device_index,
                frames_per_buffer=self.chunk
            )
            
            frames = []
            while self.is_recording:
                try:
                    data = stream.read(self.chunk, exception_on_overflow=False)
                    frames.append(data)
                except (OSError, IOError) as e:
                    print(f"Recording chunk error: {e}")
                    break
            
            if frames:
                self._save_audio_file(frames)
                
        except Exception as e:
            self._update_status(f"Recording error: {str(e)}")
        finally:
            # Ensure proper cleanup
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except (OSError, IOError):
                    pass
            if p:
                p.terminate()
    
    def _save_audio_file(self, frames: List[bytes]):
        """Save recorded frames to temporary WAV file"""
        try:
            self._cleanup_temp_file()
            
            self.temp_fd, self.temp_file_path = tempfile.mkstemp(suffix='.wav')
            # Don't close temp_fd yet - we need it for proper cleanup
            
            with wave.open(self.temp_file_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(pyaudio.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            
            self._transcribe_audio()
            
        except Exception as e:
            self._update_status(f"Save audio error: {str(e)}")
    
    def _transcribe_audio(self):
        """Transcribe audio using Whisper with optimized parameters"""
        try:
            if not self.whisper_model or not self.temp_file_path:
                self._update_status("No model or audio file")
                return
            
            # Get Whisper settings from settings manager
            # Use simple English-only toggle
            if self.settings_manager.get_english_only():
                language = "en"  # English-only for better performance
            else:
                language = None  # Auto-detect language
            
            # Enhanced Whisper parameters for PTT use case
            result = self.whisper_model.transcribe(
                self.temp_file_path,
                # Core quality settings
                fp16=False,  # Explicit FP32 for stability
                language=language,
                
                # Improved accuracy settings
                temperature=self.settings_manager.get_whisper_temperature(),
                best_of=self.settings_manager.get_whisper_best_of(),
                beam_size=self.settings_manager.get_whisper_beam_size(),
                
                # Silence and noise handling
                no_speech_threshold=self.settings_manager.get_whisper_no_speech_threshold(),
                condition_on_previous_text=False,  # Don't use context (better for PTT)
                
                # Quality thresholds
                compression_ratio_threshold=2.4,  # Detect repetitive text
                logprob_threshold=-1.0,  # Confidence threshold
                
                # Performance optimizations
                suppress_tokens="-1",  # Don't suppress any tokens
                verbose=False,  # Reduce console output
                
                # Optional: Get word-level timestamps
                word_timestamps=self.settings_manager.get_whisper_word_timestamps()
            )
            
            text = result["text"].strip()
            
            # Enhanced result processing
            if text:
                # Optional: Log confidence and other metrics
                if (self.settings_manager.get_whisper_show_confidence() and 
                    "segments" in result and result["segments"]):
                    avg_logprob = sum(seg.get("avg_logprob", 0) for seg in result["segments"]) / len(result["segments"])
                    no_speech_prob = result["segments"][0].get("no_speech_prob", 0)
                    
                    print(f"Transcription confidence: {avg_logprob:.2f}, No speech prob: {no_speech_prob:.2f}")
                
                self._update_status("Transcription ready")
                if self.transcript_callback:
                    self.transcript_callback(text)
            else:
                self._update_status("No speech detected")
                
        except Exception as e:
            self._update_status(f"Transcription error: {str(e)}")
        finally:
            self._cleanup_temp_file()
    
    def get_audio_level(self) -> float:
        """Get current audio level (0-100) - optimized with persistent stream"""
        if self.is_muted:
            return 0.0
        
        try:
            # Create persistent stream if needed
            if not self.level_stream:
                self._create_level_stream()
            
            if self.level_stream:
                data = self.level_stream.read(self.chunk, exception_on_overflow=False)
                audio_array = np.frombuffer(data, dtype=np.int16)
                mean_square = np.mean(audio_array**2)
                
                if mean_square > 0 and not np.isnan(mean_square):
                    rms = np.sqrt(mean_square)
                    return min(100, (rms / 500) * 100)
            
            return 0.0
            
        except (OSError, IOError) as e:
            print(f"Audio level error: {e}")
            self._reset_level_stream()
            return 0.0
    
    def _create_level_stream(self):
        """Create persistent audio stream for level monitoring"""
        try:
            # Create persistent PyAudio instance if needed
            if not self.level_pyaudio:
                self.level_pyaudio = pyaudio.PyAudio()
            
            self.level_stream = self.level_pyaudio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.selected_device_index,
                frames_per_buffer=self.chunk
            )
        except (OSError, IOError) as e:
            print(f"Failed to create level stream: {e}")
            self.level_stream = None
    
    def _reset_level_stream(self):
        """Reset the persistent audio stream"""
        if self.level_stream:
            try:
                self.level_stream.stop_stream()
                self.level_stream.close()
            except (OSError, IOError):
                pass
            self.level_stream = None
    
    def _cleanup_temp_file(self):
        """Clean up temporary audio file"""
        if self.temp_fd is not None:
            try:
                os.close(self.temp_fd)
            except (OSError, ValueError):
                pass  # Already closed
            self.temp_fd = None
            
        if self.temp_file_path and os.path.exists(self.temp_file_path):
            try:
                os.unlink(self.temp_file_path)
            except (OSError, IOError):
                pass  # File already deleted
            self.temp_file_path = None
    
    def cleanup(self):
        """Clean up all resources"""
        if hasattr(self, '_cleanup_done') and self._cleanup_done:
            return
            
        print("Cleaning up audio handler...")
        self._cleanup_done = True
        
        # Stop recording if active
        if self.is_recording:
            self.stop_recording()
        
        # Wait for recording thread to finish
        if hasattr(self, 'recording_thread') and self.recording_thread and self.recording_thread.is_alive():
            try:
                self.recording_thread.join(timeout=3.0)
                if self.recording_thread.is_alive():
                    print("Warning: Recording thread did not finish cleanly")
            except Exception as e:
                print(f"Error joining recording thread: {e}")
        
        # Wait for model loading thread to finish
        if hasattr(self, 'model_loading_thread') and self.model_loading_thread and self.model_loading_thread.is_alive():
            try:
                self.model_loading_thread.join(timeout=3.0)
                if self.model_loading_thread.is_alive():
                    print("Warning: Model loading thread did not finish cleanly")
            except Exception as e:
                print(f"Error joining model loading thread: {e}")
        
        # Clean up model manager
        if hasattr(self, 'model_manager') and self.model_manager:
            try:
                self.model_manager.cleanup()
            except Exception as e:
                print(f"Error cleaning up model manager: {e}")
        
        # Clean up persistent PyAudio
        try:
            if hasattr(self, 'persistent_pyaudio') and self.persistent_pyaudio:
                self.persistent_pyaudio.terminate()
                self.persistent_pyaudio = None
                print("Persistent PyAudio terminated")
        except Exception as e:
            print(f"Error terminating persistent PyAudio: {e}")
        
        # Close any open file descriptors
        if hasattr(self, 'open_file_descriptors'):
            for fd in self.open_file_descriptors:
                try:
                    os.close(fd)
                except:
                    pass
            self.open_file_descriptors.clear()
        
        # Force garbage collection
        import gc
        gc.collect()
        
        print("Audio handler cleanup complete")
        
    def __del__(self):
        """Destructor to ensure cleanup"""
        if hasattr(self, '_cleanup_done') and not self._cleanup_done:
            self.cleanup() 