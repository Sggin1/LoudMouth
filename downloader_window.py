# v3_PTT/downloader_window.py
# Model downloader GUI for v3_PTT
# Purpose: User-friendly interface for downloading Whisper models
# Dependencies: tkinter, whisper, threading

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import time
from typing import Optional, Callable
import whisper

# Handle both relative and absolute imports
try:
    from .model_manager import ModelManager
except (ImportError, ValueError):
    from model_manager import ModelManager

class DownloaderWindow:
    """GUI for downloading Whisper models"""
    
    def __init__(self, parent: Optional[tk.Widget] = None, on_downloads_complete: Optional[callable] = None):
        self.parent = parent
        self.on_downloads_complete = on_downloads_complete  # Callback for when downloads finish
        self.download_thread = None
        self.is_downloading = False
        
        # Create window
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("v3_PTT Model Downloader")
        self.window.geometry("500x680")  # Much taller to ensure buttons are visible
        self.window.configure(bg='#1a1a1a')
        self.window.resizable(False, False)
        
        if parent:
            self.window.attributes('-topmost', True)
            self.window.transient(parent)
            self._center_on_parent()
        else:
            self._center_on_screen()
        
        # Model manager
        self.model_manager = ModelManager()
        
        # Get all models (standard only, custom models can't be downloaded)
        self.model_info = {}
        for model in self.model_manager.available_models:
            self.model_info[model] = self.model_manager.model_info[model]
        
        # Sort models by file size (smallest first)
        self.sorted_models = self._sort_models_by_size()
        
        # Variables
        self.selected_models = {model: tk.BooleanVar() for model in self.model_info.keys()}
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to download models")
        
        # Create widgets
        self._create_widgets()
        self._update_model_status()
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _sort_models_by_size(self):
        """Sort models by file size (smallest first)"""
        def size_to_bytes(size_str):
            """Convert size string to bytes for sorting"""
            if 'KB' in size_str:
                return float(size_str.replace('KB', '').replace('MB', '').replace('GB', '')) * 1024
            elif 'MB' in size_str:
                return float(size_str.replace('MB', '').replace('GB', '')) * 1024 * 1024
            elif 'GB' in size_str:
                return float(size_str.replace('GB', '')) * 1024 * 1024 * 1024
            else:
                return 0
        
        # Sort by file size
        sorted_items = sorted(self.model_info.items(), key=lambda x: size_to_bytes(x[1]['size']))
        return [item[0] for item in sorted_items]
    
    def _center_on_parent(self):
        """Center window on parent"""
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_w = self.parent.winfo_width()
        parent_h = self.parent.winfo_height()
        
        x = parent_x + (parent_w // 2) - 250  # 250 = half window width
        y = parent_y + (parent_h // 2) - 340  # 340 = half window height
        
        self.window.geometry(f"500x680+{x}+{y}")
    
    def _center_on_screen(self):
        """Center window on screen"""
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        x = (screen_width // 2) - 250
        y = (screen_height // 2) - 340
        
        self.window.geometry(f"500x680+{x}+{y}")
    
    def _create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = tk.Frame(self.window, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="🎤 Whisper Model Downloader",
                             fg='white', bg='#1a1a1a', font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Description
        desc_label = tk.Label(main_frame, 
                             text="Select models to download to v3_PTT/models/",
                             fg='#cccccc', bg='#1a1a1a', font=('Arial', 9))
        desc_label.pack(pady=(0, 5))
        
                 # Download source info
        source_label = tk.Label(main_frame, 
                               text="📡 Source: OpenAI Whisper models from huggingface.co",
                               fg='#888888', bg='#1a1a1a', font=('Arial', 8))
        source_label.pack(pady=(0, 5))
        
        # Status legend
        legend_label = tk.Label(main_frame, 
                               text="✅ Bundled = Included with app  •  ✅ Cached = Downloaded to user cache  •  🔽 Available = Ready to download",
                               fg='#666666', bg='#1a1a1a', font=('Arial', 7))
        legend_label.pack(pady=(0, 10))
        
        # Model selection frame
        self._create_model_selection(main_frame)
        
        # Custom models section (read-only)
        self._create_custom_models_section(main_frame)
        
        # Progress section
        self._create_progress_section(main_frame)
        
        # Buttons
        self._create_buttons(main_frame)
    
    def _create_model_selection(self, parent):
        """Create model selection checkboxes with scrolling"""
        selection_frame = tk.LabelFrame(parent, text="Available Models", 
                                       fg='white', bg='#1a1a1a', font=('Arial', 10, 'bold'))
        selection_frame.pack(fill='x', pady=(0, 15))
        
        # Headers
        header_frame = tk.Frame(selection_frame, bg='#1a1a1a')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="Model", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=14, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Size", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=8, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Description", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=18, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Status", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=10, anchor='w').pack(side='left')
        
        # Scrollable area for models
        scrollable_frame = tk.Frame(selection_frame, bg='#1a1a1a')
        scrollable_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(scrollable_frame, bg='#1a1a1a', highlightthickness=0, height=250)
        scrollbar = ttk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
        scrollable_inner = tk.Frame(canvas, bg='#1a1a1a')
        
        # Configure scrolling
        scrollable_inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # Model rows (in scrollable area) - sorted by size
        self.model_frames = {}
        for model_name in self.sorted_models:
            info = self.model_info[model_name]
            model_frame = tk.Frame(scrollable_inner, bg='#1a1a1a')
            model_frame.pack(fill='x', pady=2)
            self.model_frames[model_name] = model_frame
            
            # Checkbox
            checkbox = tk.Checkbutton(model_frame, variable=self.selected_models[model_name],
                                    fg='white', bg='#1a1a1a', selectcolor='#404040',
                                    activeforeground='white', activebackground='#1a1a1a',
                                    width=14, anchor='w', text=model_name)
            checkbox.pack(side='left')
            
            # Size
            size_label = tk.Label(model_frame, text=info['size'], fg='#ffcc00', bg='#1a1a1a', 
                                 font=('Arial', 9), width=8, anchor='w')
            size_label.pack(side='left')
            
            # Description
            desc_label = tk.Label(model_frame, text=info['desc'], fg='#cccccc', bg='#1a1a1a', 
                                 font=('Arial', 9), width=18, anchor='w')
            desc_label.pack(side='left')
            
            # Status
            status_label = tk.Label(model_frame, text="Checking...", fg='#888888', bg='#1a1a1a', 
                                   font=('Arial', 9), width=10, anchor='w')
            status_label.pack(side='left')
            
            # Store reference for updates
            setattr(self, f"{model_name}_status_label", status_label)
    
    def _create_custom_models_section(self, parent):
        """Create custom models display section with scrolling"""
        custom_models = self.model_manager._scan_custom_models()
        
        if not custom_models:
            return  # No custom models to show
        
        # Custom models frame
        custom_frame = tk.LabelFrame(parent, text="Custom Models (Read-only)", 
                                    fg='#ffcc00', bg='#1a1a1a', font=('Arial', 10, 'bold'))
        custom_frame.pack(fill='x', pady=(10, 0))
        
        # Description
        desc_label = tk.Label(custom_frame, 
                             text="These are custom models found in your models folder",
                             fg='#888888', bg='#1a1a1a', font=('Arial', 8))
        desc_label.pack(pady=(5, 0))
        
        # Headers
        header_frame = tk.Frame(custom_frame, bg='#1a1a1a')
        header_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(header_frame, text="Model", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=8, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Size", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=8, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Description", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=20, anchor='w').pack(side='left')
        tk.Label(header_frame, text="Status", fg='#cccccc', bg='#1a1a1a', 
                font=('Arial', 9, 'bold'), width=12, anchor='w').pack(side='left')
        
        # Scrollable area for custom models (smaller height for custom section)
        custom_scrollable_frame = tk.Frame(custom_frame, bg='#1a1a1a')
        custom_scrollable_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        # Determine height based on number of custom models (max 5 visible)
        max_visible_custom = 5
        custom_height = min(len(custom_models) * 25, max_visible_custom * 25)
        
        # Create canvas and scrollbar for custom models
        custom_canvas = tk.Canvas(custom_scrollable_frame, bg='#1a1a1a', highlightthickness=0, 
                                 height=custom_height)
        custom_scrollbar = ttk.Scrollbar(custom_scrollable_frame, orient="vertical", 
                                        command=custom_canvas.yview)
        custom_scrollable_inner = tk.Frame(custom_canvas, bg='#1a1a1a')
        
        # Configure scrolling for custom models
        custom_scrollable_inner.bind(
            "<Configure>",
            lambda e: custom_canvas.configure(scrollregion=custom_canvas.bbox("all"))
        )
        
        custom_canvas.create_window((0, 0), window=custom_scrollable_inner, anchor="nw")
        custom_canvas.configure(yscrollcommand=custom_scrollbar.set)
        
        # Pack canvas and scrollbar for custom models
        custom_canvas.pack(side="left", fill="both", expand=True)
        if len(custom_models) > max_visible_custom:
            custom_scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to custom canvas
        def _on_custom_mousewheel(event):
            custom_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        custom_canvas.bind("<MouseWheel>", _on_custom_mousewheel)
        
        # Custom model rows (in scrollable area)
        for model_name in sorted(custom_models):
            model_info = self.model_manager.model_info.get(model_name, {})
            
            model_frame = tk.Frame(custom_scrollable_inner, bg='#1a1a1a')
            model_frame.pack(fill='x', pady=2)
            
            # Model name (no checkbox, just text)
            name_label = tk.Label(model_frame, text=model_name, fg='#ffcc00', bg='#1a1a1a', 
                                 font=('Arial', 9), width=8, anchor='w')
            name_label.pack(side='left')
            
            # Size
            size_label = tk.Label(model_frame, text=model_info.get('size', 'Unknown'), 
                                 fg='#ffcc00', bg='#1a1a1a', font=('Arial', 9), width=8, anchor='w')
            size_label.pack(side='left')
            
            # Description
            desc_label = tk.Label(model_frame, text=model_info.get('desc', 'Custom model'), 
                                 fg='#cccccc', bg='#1a1a1a', font=('Arial', 9), width=20, anchor='w')
            desc_label.pack(side='left')
            
            # Status (always custom)
            status_label = tk.Label(model_frame, text="🔧 Custom", fg='#ffcc00', bg='#1a1a1a', 
                                   font=('Arial', 9), width=12, anchor='w')
            status_label.pack(side='left')
    
    def _create_progress_section(self, parent):
        """Create progress bar and status"""
        progress_frame = tk.LabelFrame(parent, text="Download Progress", 
                                      fg='white', bg='#1a1a1a', font=('Arial', 10, 'bold'))
        progress_frame.pack(fill='x', pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                           maximum=100, length=400)
        self.progress_bar.pack(pady=8, padx=10)
        
        # Status label
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var,
                                    fg='#00ff00', bg='#1a1a1a', font=('Arial', 9))
        self.status_label.pack(pady=(0, 8))
    
    def _create_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg='#1a1a1a')
        button_frame.pack(fill='x', pady=15, padx=10)  # More padding and margins
        
        # Select All button
        select_all_btn = tk.Button(button_frame, text="Select All",
                                  fg='white', bg='#6c757d', font=('Arial', 9),
                                  width=10, height=2, command=self._select_all)
        select_all_btn.pack(side='left', padx=5)
        
        # Clear All button
        clear_all_btn = tk.Button(button_frame, text="Clear All",
                                 fg='white', bg='#6c757d', font=('Arial', 9),
                                 width=10, height=2, command=self._clear_all)
        clear_all_btn.pack(side='left', padx=5)
        
        # Download button
        self.download_btn = tk.Button(button_frame, text="Download Selected",
                                     fg='white', bg='#28a745', font=('Arial', 9, 'bold'),
                                     width=15, height=2, command=self._start_download)
        self.download_btn.pack(side='right', padx=5)
        
        # Close button
        close_btn = tk.Button(button_frame, text="Close",
                             fg='white', bg='#dc3545', font=('Arial', 9),
                             width=10, height=2, command=self._on_close)
        close_btn.pack(side='right', padx=5)
    
    def _update_model_status(self):
        """Update model availability status"""
        def update_status():
            model_status = self.model_manager.get_model_status()
            model_locations = model_status.get('model_locations', {})
            
            for model_name in self.model_info.keys():
                status_label = getattr(self, f"{model_name}_status_label")
                
                if model_name in model_locations:
                    location = model_locations[model_name]
                    if location == 'bundled':
                        status_label.config(text="✅ Bundled", fg='#00ff00')
                    elif location == 'cached':
                        status_label.config(text="✅ Cached", fg='#00ccff')
                    elif location == 'custom':
                        status_label.config(text="🔧 Custom", fg='#ffcc00')
                else:
                    status_label.config(text="🔽 Available", fg='#00aaff')
        
        # Run in thread to avoid blocking UI
        threading.Thread(target=update_status, daemon=True).start()
    
    def _select_all(self):
        """Select all models"""
        for var in self.selected_models.values():
            var.set(True)
    
    def _clear_all(self):
        """Clear all selections"""
        for var in self.selected_models.values():
            var.set(False)
    
    def _start_download(self):
        """Start downloading selected models"""
        if self.is_downloading:
            messagebox.showwarning("Download in Progress", 
                                 "A download is already in progress. Please wait.")
            return
        
        # Get selected models
        selected = [model for model, var in self.selected_models.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Selection", 
                                 "Please select at least one model to download.")
            return
        
        # Start download in separate thread
        self.is_downloading = True
        self.download_btn.config(state='disabled', text="Downloading...")
        self.download_thread = threading.Thread(target=self._download_models, 
                                               args=(selected,), daemon=True)
        self.download_thread.start()
    
    def _download_models(self, selected_models):
        """Download selected models"""
        models_dir = self.model_manager.local_models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        total_models = len(selected_models)
        
        for i, model_name in enumerate(selected_models):
            try:
                # Update status
                model_size = self.model_info[model_name]['size']
                self.status_var.set(f"Downloading {model_name} ({model_size}) from OpenAI/Whisper... ({i+1}/{total_models})")
                self.progress_var.set((i / total_models) * 100)
                
                # Download model
                model = whisper.load_model(model_name, download_root=models_dir, device="cpu")
                
                # Clear memory
                del model
                
                # Update progress
                self.progress_var.set(((i + 1) / total_models) * 100)
                
            except Exception as e:
                self.status_var.set(f"Error downloading {model_name}: {str(e)}")
                break
        
        # Finish
        if self.progress_var.get() >= 100:
            self.status_var.set("✅ All downloads completed successfully!")
            
            # Call the callback if provided
            if self.on_downloads_complete:
                try:
                    self.on_downloads_complete()
                except Exception as e:
                    print(f"Error in downloads complete callback: {e}")
        
        self.is_downloading = False
        self.download_btn.config(state='normal', text="Download Selected")
        
        # Update model status
        self.window.after(1000, self._update_model_status)
    
    def _on_close(self):
        """Handle window close"""
        if self.is_downloading:
            result = messagebox.askyesno("Download in Progress", 
                                       "A download is in progress. Close anyway?")
            if not result:
                return
        
        self.window.destroy()

def main():
    """Standalone launcher"""
    app = DownloaderWindow()
    app.window.mainloop()

if __name__ == "__main__":
    main() 