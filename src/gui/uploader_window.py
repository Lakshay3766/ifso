#!/usr/bin/env python3
"""
CDR Uploader GUI Window
Standalone window for uploading CSV files to database
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from database.csv_importer import CSVImporter


class CDRUploaderGUI:
    """GUI for uploading CDR CSV files"""
    
    def __init__(self, root):
        """
        Initialize uploader GUI
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("CDR Data Uploader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        self.csv_file_path = tk.StringVar()
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_dir = os.path.join(project_root, "data")
        os.makedirs(data_dir, exist_ok=True)
        default_db = os.path.join(data_dir, "cdr_database.db")
        self.db_path = tk.StringVar(value=default_db)
        self.is_uploading = False
        self._last_progress_logged = -1
        
        self._configure_style()
        self.setup_ui()
    
    def _configure_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
            
        bg_color = "#f8fafc"
        card_color = "#ffffff"
        text_color = "#0f172a"
        accent_color = "#2563eb"
        
        style.configure("TFrame", background=bg_color)
        style.configure("Card.TFrame", background=card_color, relief="flat", borderwidth=1, bordercolor="#e2e8f0")
        style.configure("Accent.TButton", background=accent_color, foreground="#ffffff", borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])
        style.configure("Muted.TLabel", foreground="#64748b", background=bg_color)
        
        style.configure("TLabel", foreground=text_color, background=bg_color)
        style.configure("TButton", background="#e2e8f0", foreground=text_color)
        style.configure("TEntry", fieldbackground="#ffffff", foreground=text_color)
        style.configure("TCombobox", fieldbackground="#ffffff", foreground=text_color)
        
        self.root.configure(background=bg_color)
    
    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="CDR Data Uploader", 
                               font=("Helvetica", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="15")
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="CSV File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        csv_entry = ttk.Entry(file_frame, textvariable=self.csv_file_path, width=50)
        csv_entry.grid(row=0, column=1, padx=10, pady=5)
        browse_btn = ttk.Button(file_frame, text="Browse", command=self.browse_csv)
        browse_btn.grid(row=0, column=2, pady=5)
        
        ttk.Label(file_frame, text="Database:").grid(row=1, column=0, sticky=tk.W, pady=5)
        db_entry = ttk.Entry(file_frame, textvariable=self.db_path, width=50)
        db_entry.grid(row=1, column=1, padx=10, pady=5)
        browse_db_btn = ttk.Button(file_frame, text="Browse", command=self.browse_db)
        browse_db_btn.grid(row=1, column=2, pady=5)
        
        # Upload button
        upload_frame = ttk.Frame(main_frame)
        upload_frame.pack(fill=tk.X, pady=10)
        
        self.upload_btn = ttk.Button(upload_frame, text="Upload Data", 
                                     command=self.start_upload, width=20)
        self.upload_btn.pack()
        
        # Progress bar
        progress_frame = ttk.LabelFrame(main_frame, text="Upload Progress", padding="15")
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=300, maximum=100)
        self.progress_bar.pack(pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="Ready to upload", 
                                      font=("Helvetica", 10))
        self.status_label.pack(pady=5)
        
        # Log text area
        log_frame = ttk.LabelFrame(main_frame, text="Upload Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80, 
                                                  wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Initial log message
        self.log_message("Welcome to CDR Data Uploader")
        self.log_message("Please select a CSV file and click 'Upload Data' to begin")
        self.log_message("=" * 60)
    
    def browse_csv(self):
        """Browse for CSV file"""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.csv_file_path.set(file_path)
            self.log_message(f"Selected CSV file: {file_path}")
    
    def browse_db(self):
        """Browse for database file"""
        db_path = filedialog.asksaveasfilename(
            title="Select Database File",
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if db_path:
            self.db_path.set(db_path)
            self.log_message(f"Selected database: {db_path}")
    
    def log_message(self, message):
        """
        Add message to log
        
        Args:
            message: Message to log
        """
        def append():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        self.root.after(0, append)
    
    def start_upload(self):
        """Start the upload process in a separate thread"""
        if self.is_uploading:
            messagebox.showwarning("Upload in Progress", 
                                 "An upload is already in progress. Please wait.")
            return
        
        csv_path = self.csv_file_path.get().strip()
        if not csv_path:
            messagebox.showwarning("No File Selected", 
                                 "Please select a CSV file to upload.")
            return
        
        self.is_uploading = True
        self._last_progress_logged = -1
        self.upload_btn.config(state='disabled')
        self.status_label.config(text="Uploading...")
        self.progress_bar["value"] = 0
        
        # Run upload in separate thread
        upload_thread = threading.Thread(target=self.perform_upload, daemon=True)
        upload_thread.start()
    
    def perform_upload(self):
        """Perform the actual upload"""
        try:
            self.log_message("=" * 60)
            self.log_message("Starting upload process...")
            self.log_message(f"CSV File: {self.csv_file_path.get()}")
            self.log_message(f"Database: {self.db_path.get()}")
            
            # Initialize database manager and importer
            db_manager = DatabaseManager(self.db_path.get())
            importer = CSVImporter(db_manager)
            
            # Define progress callback
            def progress_callback(progress, count):
                def update():
                    self.progress_bar["value"] = progress
                    self.status_label.config(text=f"Uploading... {progress}% (Inserted {count})")

                self.root.after(0, update)

                if progress >= self._last_progress_logged + 5 or progress == 100:
                    self._last_progress_logged = progress
                    self.log_message(f"Progress: {progress}% - Inserted {count} records")
            
            # Import CSV
            success, message, count = importer.import_csv(
                self.csv_file_path.get(),
                progress_callback=progress_callback
            )
            
            self.log_message(message)
            
            if success:
                def done_ok():
                    self.status_label.config(text="Upload completed successfully!")
                    messagebox.showinfo("Success", message)

                self.root.after(0, done_ok)
            else:
                def done_err():
                    self.status_label.config(text="Upload failed!")
                    messagebox.showerror("Error", message)

                self.root.after(0, done_err)
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_message(error_msg)
            def failed():
                self.status_label.config(text="Upload failed with error!")
                messagebox.showerror("Error", error_msg)

            self.root.after(0, failed)
        
        finally:
            def cleanup():
                self.upload_btn.config(state='normal')
                self.is_uploading = False
                self.log_message("=" * 60)

            self.root.after(0, cleanup)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = CDRUploaderGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
