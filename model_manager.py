# v3_PTT/model_manager.py
# Async Whisper model management and updates
# Purpose: Handle model availability, updates, and network issues gracefully
# Dependencies: whisper, asyncio, threading, requests

import os
import asyncio
import threading
import time
import requests
from typing import Dict, List, Optional, Callable
import whisper

class ModelManager:
    """Async manager for Whisper model availability and updates"""
    
    def __init__(self, status_callback: Optional[Callable] = None):
        self.status_callback = status_callback
        self.local_models_dir = os.path.join(os.path.dirname(__file__), 'models')
        self.cache_dir = os.path.expanduser("~/.cache/whisper")
        
        # Dynamically get available models from Whisper
        try:
            self.available_models = sorted(whisper.available_models())
        except Exception:
            # Fallback to known models if discovery fails
            self.available_models = ['tiny', 'base', 'small', 'medium', 'large']
        
        # Dynamic model info with better estimates
        self.model_info = self._get_dynamic_model_info()
        self.last_check = 0
        self.check_interval = 3600  # Check every hour
    
    def _get_dynamic_model_info(self) -> Dict:
        """Get model info dynamically for any available model"""
        # Base size estimates (approximate)
        size_estimates = {
            'tiny': '72MB', 'base': '290MB', 'small': '967MB', 
            'medium': '3.1GB', 'large': '6.2GB', 'turbo': '1.5GB'
        }
        
        # Generate info for all available models
        model_info = {}
        for model in self.available_models:
            # Extract base model name for size estimation
            base_name = model.split('.')[0].split('-')[0]  # tiny.en -> tiny, large-v3 -> large
            
            # Get size estimate
            size = size_estimates.get(base_name, '~GB')
            
            # Generate description
            if '.en' in model:
                desc = f"English-only {base_name} model"
            elif 'turbo' in model:
                desc = "Fast, optimized model"
            elif 'large-v' in model:
                version = model.split('-v')[1] if '-v' in model else ''
                desc = f"Large model version {version}"
            else:
                descriptions = {
                    'tiny': 'Fastest, least accurate',
                    'base': 'Good balance (recommended)',
                    'small': 'Better accuracy',
                    'medium': 'High accuracy',
                    'large': 'Best accuracy, slowest'
                }
                desc = descriptions.get(base_name, 'Whisper model')
            
            model_info[model] = {'size': size, 'desc': desc}
        
        return model_info
    
    def _scan_custom_models(self) -> List[str]:
        """Scan models folder for custom .pt files"""
        custom_models = []
        
        if os.path.exists(self.local_models_dir):
            for filename in os.listdir(self.local_models_dir):
                if filename.endswith('.pt'):
                    model_name = filename[:-3]  # Remove .pt extension
                    # Only add if not already in standard models
                    if model_name not in self.available_models:
                        custom_models.append(model_name)
                        
                        # Add to model_info for custom models
                        file_path = os.path.join(self.local_models_dir, filename)
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size < 1024*1024:  # Less than 1MB
                                size_str = f"{file_size//1024}KB"
                            elif file_size < 1024*1024*1024:  # Less than 1GB
                                size_str = f"{file_size//(1024*1024)}MB"
                            else:
                                size_str = f"{file_size//(1024*1024*1024):.1f}GB"
                        except:
                            size_str = "Unknown"
                        
                        self.model_info[model_name] = {
                            'size': size_str,
                            'desc': 'Custom model'
                        }
        
        return custom_models
    
    def _scan_local_models(self) -> List[str]:
        """Scan models folder for ALL .pt files (including standard models)"""
        local_models = []
        
        if os.path.exists(self.local_models_dir):
            for filename in os.listdir(self.local_models_dir):
                if filename.endswith('.pt'):
                    model_name = filename[:-3]  # Remove .pt extension
                    local_models.append(model_name)
                    
                    # Add to model_info if not already present
                    if model_name not in self.model_info:
                        file_path = os.path.join(self.local_models_dir, filename)
                        try:
                            file_size = os.path.getsize(file_path)
                            if file_size < 1024*1024:  # Less than 1MB
                                size_str = f"{file_size//1024}KB"
                            elif file_size < 1024*1024*1024:  # Less than 1GB
                                size_str = f"{file_size//(1024*1024)}MB"
                            else:
                                size_str = f"{file_size//(1024*1024*1024):.1f}GB"
                        except:
                            size_str = "Unknown"
                        
                        # Determine if it's a standard model or custom
                        if model_name in self.available_models:
                            desc = self.model_info.get(model_name, {}).get('desc', 'Whisper model')
                        else:
                            desc = 'Custom model'
                        
                        self.model_info[model_name] = {
                            'size': size_str,
                            'desc': desc
                        }
        
        return local_models
    
    def get_all_models(self) -> List[str]:
        """Get all models (standard + custom)"""
        custom_models = self._scan_custom_models()
        all_models = list(self.available_models) + custom_models
        return sorted(all_models)
    
    def _update_status(self, message: str):
        """Update status via callback"""
        if self.status_callback:
            self.status_callback(message)
    
    def get_local_models(self) -> List[str]:
        """Get list of locally available models"""
        available = []
        
        # First, scan the local models directory for actual files
        local_folder_models = self._scan_local_models()
        
        # Then check cache directory for standard models
        all_models = self.get_all_models()
        
        for model_size in all_models:
            if self.is_model_available(model_size):
                available.append(model_size)
        
        # Ensure all models found in local folder are included
        for model in local_folder_models:
            if model not in available:
                available.append(model)
        
        return available
    
    def get_missing_models(self) -> List[str]:
        """Get list of missing models (only standard models, not custom)"""
        local = self.get_local_models()
        return [m for m in self.available_models if m not in local]
    
    def is_model_available(self, model_size: str) -> bool:
        """Check if specific model is available locally"""
        # Check local models dir first, then cache
        local_path = os.path.join(self.local_models_dir, f"{model_size}.pt")
        cache_path = os.path.join(self.cache_dir, f"{model_size}.pt")
        cache_path_v3 = os.path.join(self.cache_dir, f"{model_size}-v3.pt")
        
        return (os.path.exists(local_path) or 
                os.path.exists(cache_path) or 
                os.path.exists(cache_path_v3))
    
    def get_model_path(self, model_size: str) -> Optional[str]:
        """Get full path to model file"""
        local_path = os.path.join(self.local_models_dir, f"{model_size}.pt")
        cache_path = os.path.join(self.cache_dir, f"{model_size}.pt")
        cache_path_v3 = os.path.join(self.cache_dir, f"{model_size}-v3.pt")
        
        if os.path.exists(local_path):
            return local_path
        elif os.path.exists(cache_path):
            return cache_path
        elif os.path.exists(cache_path_v3):
            return cache_path_v3
        return None
    
    def get_model_status(self) -> Dict:
        """Get comprehensive model status"""
        local_models = self.get_local_models()
        missing_models = self.get_missing_models()
        custom_models = self._scan_custom_models()
        
        # Get location info for available models
        model_locations = {}
        for model in local_models:
            path = self.get_model_path(model)
            if path:
                if self.local_models_dir in path:
                    if model in custom_models:
                        model_locations[model] = 'custom'
                    else:
                        model_locations[model] = 'bundled'
                else:
                    model_locations[model] = 'cached'
        
        return {
            'local_models': local_models,
            'missing_models': missing_models,
            'custom_models': custom_models,
            'total_available': len(local_models),
            'total_missing': len(missing_models),
            'total_custom': len(custom_models),
            'model_locations': model_locations,
            'bundled_dir': self.local_models_dir,
            'cache_dir': self.cache_dir
        }
    
    def check_internet_connection(self, timeout: int = 5) -> bool:
        """Check if internet connection is available"""
        try:
            response = requests.get('https://httpbin.org/get', timeout=timeout)
            return response.status_code == 200
        except:
            return False
    
    def estimate_download_time(self, model_size: str, connection_speed: str = 'medium') -> str:
        """Estimate download time based on model size and connection"""
        speeds = {
            'slow': 1,      # 1 MB/s (mobile/poor)
            'medium': 10,   # 10 MB/s (normal broadband)
            'fast': 50      # 50 MB/s (good broadband)
        }
        
        size_mb = {
            'tiny': 72, 'base': 290, 'small': 967, 
            'medium': 3100, 'large': 6200
        }
        
        if model_size not in size_mb:
            return "Unknown"
            
        mb = size_mb[model_size]
        speed = speeds.get(connection_speed, 10)
        seconds = mb / speed
        
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        else:
            return f"{int(seconds/3600)}h {int((seconds%3600)/60)}m"
    
    async def check_model_updates_async(self) -> Dict:
        """HIPAA-compliant async model check (user-initiated only)"""
        def _check_updates():
            try:
                # Only check local models - no network calls
                status = self.get_model_status()
                
                if status['total_missing'] > 0:
                    return {
                        'status': 'missing_models',
                        'missing': status['missing_models'],
                        'message': f"{status['total_missing']} models not downloaded",
                        'action': 'Use download_models.py to get missing models'
                    }
                else:
                    return {
                        'status': 'up_to_date',
                        'message': 'All models available locally'
                    }
                    
            except Exception as e:
                return {'status': 'error', 'message': str(e)}
        
        # Run in thread to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, _check_updates)
    
    def get_download_recommendation(self, model_size: str) -> Dict:
        """Get recommendation for downloading a model (local check only)"""
        if self.is_model_available(model_size):
            return {
                'action': 'ready',
                'message': f"Model '{model_size}' is ready to use"
            }
        
        info = self.model_info.get(model_size, {})
        estimates = {
            'slow': self.estimate_download_time(model_size, 'slow'),
            'medium': self.estimate_download_time(model_size, 'medium'),
            'fast': self.estimate_download_time(model_size, 'fast')
        }
        
        return {
            'action': 'download_needed',
            'model_size': model_size,
            'file_size': info.get('size', 'unknown'),
            'estimates': estimates,
            'suggestion': f"Run 'python download_models.py' to download {model_size} model ({info.get('size', 'unknown')})"
        }
    
    def manual_network_check(self, timeout: int = 5) -> Dict:
        """Manual network check (user-initiated only for HIPAA compliance)"""
        try:
            if self.check_internet_connection(timeout):
                return {
                    'status': 'online',
                    'message': 'Internet connection available',
                    'action': 'Can download models if needed'
                }
            else:
                return {
                    'status': 'offline',
                    'message': 'No internet connection detected',
                    'action': 'Check connection and try again'
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Network check failed: {str(e)}',
                'action': 'Check connection and try again'
            }
    
    def get_model_warning(self, model_size: str) -> Optional[str]:
        """Get warning message for model if needed"""
        if self.is_model_available(model_size):
            return None
        
        info = self.model_info.get(model_size, {})
        return f"⚠️  Model '{model_size}' ({info.get('size', 'unknown')}) not downloaded. App may freeze during download."
    
    def get_quick_status(self) -> str:
        """Get quick status for UI display"""
        local_models = self._scan_local_models()  # Only bundled models
        custom_count = len(self._scan_custom_models())
        
        if len(local_models) == 0:
            return "❌ No models available"
        else:
            model_text = f"{len(local_models)} model{'s' if len(local_models) != 1 else ''}"
            if custom_count > 0:
                model_text += f" + {custom_count} custom"
            return f"✅ {model_text} ready" 
    
    def cleanup(self):
        """Clean up model resources"""
        try:
            if hasattr(self, 'model') and self.model is not None:
                print("Cleaning up Whisper model...")
                # Clear model from memory
                del self.model
                self.model = None
                
                # Force garbage collection
                import gc
                gc.collect()
                
                # Clear CUDA cache if available
                try:
                    import torch
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                except:
                    pass
                
                print("Model cleanup complete")
        except Exception as e:
            print(f"Error during model cleanup: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup() 