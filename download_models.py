#!/usr/bin/env python3
"""
v3_PTT Whisper Model Downloader
Downloads all Whisper models in advance to prevent freezing during model switching.
Run this script once before using the v3_PTT application.
"""

import whisper
import sys
import time
import os
from pathlib import Path

def download_all_models(to_bundled: bool = False):
    """Download all Whisper models"""
    models = ['tiny', 'base', 'small', 'medium', 'large']
    model_sizes = {
        'tiny': '72MB',
        'base': '290MB', 
        'small': '967MB',
        'medium': '3.1GB',
        'large': '6.2GB'
    }
    
    print("🎤 Whisper Model Downloader for PTT")
    print("=" * 50)
    print("This will download all Whisper models to prevent freezing during model switching.")
    print("You can cancel anytime with Ctrl+C\n")
    
    # Show download location
    if to_bundled:
        bundled_dir = os.path.join(os.path.dirname(__file__), 'models')
        print(f"📂 Download location: {bundled_dir} (v3_PTT bundled installation)")
    else:
        print(f"📂 Download location: User cache directory (~/.cache/whisper)")
    
    # Show what will be downloaded
    total_size = "~10.7GB"
    print("\nModels to download:")
    for model in models:
        print(f"  • {model:<8} ({model_sizes[model]})")
    print(f"\nTotal size: {total_size}")
    print("-" * 50)
    
    # Ask for confirmation
    try:
        choice = input("\nDownload all models? (y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print("Download cancelled.")
            return False
    except KeyboardInterrupt:
        print("\nDownload cancelled.")
        return False
    
    print("\n🚀 Starting downloads...\n")
    
    # Create bundled directory if needed
    if to_bundled:
        bundled_dir = os.path.join(os.path.dirname(__file__), 'models')
        os.makedirs(bundled_dir, exist_ok=True)
        print(f"📁 Created v3_PTT bundled models directory: {bundled_dir}\n")
    
    success_count = 0
    
    for i, model_name in enumerate(models, 1):
        try:
            print(f"[{i}/{len(models)}] Downloading {model_name} model ({model_sizes[model_name]})...")
            start_time = time.time()
            
            # Download model to appropriate location
            if to_bundled:
                model = whisper.load_model(model_name, download_root=bundled_dir, device="cpu")
            else:
                model = whisper.load_model(model_name, device="cpu")
            
            elapsed = time.time() - start_time
            print(f"✅ {model_name} model downloaded successfully! ({elapsed:.1f}s)")
            success_count += 1
            
            # Clear memory
            del model
            
        except KeyboardInterrupt:
            print(f"\n❌ Download cancelled by user.")
            break
        except Exception as e:
            print(f"❌ Failed to download {model_name} model: {e}")
            continue
        
        print()  # Add spacing between downloads
    
    print("=" * 50)
    if success_count == len(models):
        print("🎉 All models downloaded successfully!")
        print("You can now use the v3_PTT application without freezing during model switching.")
    elif success_count > 0:
        print(f"✅ {success_count}/{len(models)} models downloaded successfully.")
        print("You can still use the downloaded models without freezing.")
    else:
        print("❌ No models were downloaded.")
    
    return success_count > 0

def download_specific_models():
    """Download only specific models chosen by user"""
    models = ['tiny', 'base', 'small', 'medium', 'large']
    model_sizes = {
        'tiny': '72MB',
        'base': '290MB', 
        'small': '967MB',
        'medium': '3.1GB',
        'large': '6.2GB'
    }
    
    print("🎤 Whisper Model Downloader (Custom Selection)")
    print("=" * 50)
    print("Available models:")
    for i, model in enumerate(models, 1):
        print(f"  {i}. {model:<8} ({model_sizes[model]})")
    print("  0. Cancel")
    
    try:
        choices = input("\nEnter numbers to download (e.g., 1,3,5 or 1-3): ").strip()
        if not choices or choices == '0':
            print("Download cancelled.")
            return False
        
        # Parse choices
        selected = []
        for part in choices.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                selected.extend(range(start-1, end))
            else:
                selected.append(int(part)-1)
        
        # Remove duplicates and invalid indices
        selected = list(set([i for i in selected if 0 <= i < len(models)]))
        
        if not selected:
            print("No valid models selected.")
            return False
        
        selected_models = [models[i] for i in selected]
        print(f"\nSelected models: {', '.join(selected_models)}")
        
        confirm = input("Download these models? (y/N): ").strip().lower()
        if confirm not in ['y', 'yes']:
            print("Download cancelled.")
            return False
        
        print("\n🚀 Starting downloads...\n")
        
        success_count = 0
        for i, model_name in enumerate(selected_models, 1):
            try:
                print(f"[{i}/{len(selected_models)}] Downloading {model_name} model ({model_sizes[model_name]})...")
                start_time = time.time()
                
                model = whisper.load_model(model_name, device="cpu")
                
                elapsed = time.time() - start_time
                print(f"✅ {model_name} model downloaded successfully! ({elapsed:.1f}s)")
                success_count += 1
                
                del model
                
            except KeyboardInterrupt:
                print(f"\n❌ Download cancelled by user.")
                break
            except Exception as e:
                print(f"❌ Failed to download {model_name} model: {e}")
                continue
            
            print()
        
        print("=" * 50)
        if success_count == len(selected_models):
            print("🎉 Selected models downloaded successfully!")
        elif success_count > 0:
            print(f"✅ {success_count}/{len(selected_models)} models downloaded successfully.")
        
        return success_count > 0
        
    except (ValueError, KeyboardInterrupt):
        print("\nDownload cancelled.")
        return False

def main():
    print("v3_PTT Model Downloader")
    print("Choose download option:")
    print("1. Download all models to user cache (~10.7GB)")
    print("2. Download all models to v3_PTT/models (~10.7GB)")
    print("3. Download specific models to user cache")
    print("0. Exit")
    
    try:
        choice = input("\nChoice (1/2/3/0): ").strip()
        
        if choice == '1':
            download_all_models(to_bundled=False)
        elif choice == '2':
            download_all_models(to_bundled=True)
        elif choice == '3':
            download_specific_models()
        elif choice == '0':
            print("Goodbye!")
        else:
            print("Invalid choice.")
            
    except KeyboardInterrupt:
        print("\nGoodbye!")

if __name__ == "__main__":
    main() 