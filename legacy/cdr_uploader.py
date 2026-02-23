#!/usr/bin/env python3
import argparse
import csv
import sqlite3
from datetime import datetime
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

def parse_lat_long(lat_long_str):
    if lat_long_str and lat_long_str != '---':
        try:
            lat, long = lat_long_str.split('/')
            return float(lat), float(long)
        except ValueError:
            return None, None
    return None, None

def upload_csv_to_sqlite(csv_file_path, db_path='cdr_database.db'):
    conn = None
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cdrs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_no TEXT,
            call_type TEXT,
            toc TEXT,
            b_party_no TEXT,
            lrn_no TEXT,
            lrn_tsp_lsa TEXT,
            datetime TIMESTAMP,
            duration_seconds INTEGER,
            first_cgi_lat REAL,
            first_cgi_long REAL,
            first_cgi TEXT,
            last_cgi_lat REAL,
            last_cgi_long REAL,
            last_cgi TEXT,
            smsc_no TEXT,
            service_type TEXT,
            imei TEXT,
            imsi TEXT,
            call_fow_no TEXT,
            roam_nw TEXT,
            sw_msc_id TEXT,
            in_tg TEXT,
            out_tg TEXT,
            vowifi_first_ue_ip TEXT,
            port1 TEXT,
            vowifi_last_ue_ip TEXT,
            port2 TEXT
        )
        ''')
        
        # Read CSV file
        with open(csv_file_path, 'r', newline='', encoding='utf-8') as csvfile:
            lines = csvfile.readlines()
            
            # Find the header line (assuming it contains 'Target No')
            header_index = None
            for i, line in enumerate(lines):
                if 'Target No' in line:
                    header_index = i
                    break
            
            if header_index is None:
                raise ValueError("Header line not found in CSV file.")
            
            # Use StringIO to create a file-like object from the remaining lines
            from io import StringIO
            csv_data = StringIO(''.join(lines[header_index:]))
            
            reader = csv.DictReader(csv_data)
            records = []
            for row in reader:
                # Clean the row to remove any None keys (from extra fields)
                cleaned_row = {k: v for k, v in row.items() if k is not None}
                
                # Parse and convert fields
                parsed_record = {}
                
                # Basic fields
                parsed_record['target_no'] = cleaned_row.get('Target No')
                parsed_record['call_type'] = cleaned_row.get('Call Type')
                parsed_record['toc'] = cleaned_row.get('TOC')
                parsed_record['b_party_no'] = cleaned_row.get('B Party No')
                parsed_record['lrn_no'] = cleaned_row.get('LRN No')
                parsed_record['lrn_tsp_lsa'] = cleaned_row.get('LRN TSP-LSA')
                
                # Date and Time
                date_str = cleaned_row.get('Date')
                if date_str:
                    date_str = date_str.strip("'")
                else:
                    date_str = None
                time_str = cleaned_row.get('Time')
                if date_str and time_str:
                    try:
                        datetime_str = f"{date_str} {time_str}"
                        parsed_record['datetime'] = datetime.strptime(datetime_str, "%d/%m/%Y %H:%M:%S")
                    except ValueError:
                        parsed_record['datetime'] = None
                else:
                    parsed_record['datetime'] = None
                
                # Duration
                dur_str = cleaned_row.get('Dur(s)')
                if dur_str:
                    try:
                        parsed_record['duration_seconds'] = int(dur_str)
                    except ValueError:
                        parsed_record['duration_seconds'] = None
                else:
                    parsed_record['duration_seconds'] = None
                
                # First CGI Lat/Long
                first_lat, first_long = parse_lat_long(cleaned_row.get('First CGI Lat/Long'))
                parsed_record['first_cgi_lat'] = first_lat
                parsed_record['first_cgi_long'] = first_long
                parsed_record['first_cgi'] = cleaned_row.get('First CGI')
                
                # Last CGI Lat/Long
                last_lat, last_long = parse_lat_long(cleaned_row.get('Last CGI Lat/Long'))
                parsed_record['last_cgi_lat'] = last_lat
                parsed_record['last_cgi_long'] = last_long
                parsed_record['last_cgi'] = cleaned_row.get('Last CGI')
                
                # Other fields
                parsed_record['smsc_no'] = cleaned_row.get('SMSC No')
                parsed_record['service_type'] = cleaned_row.get('Service Type')
                parsed_record['imei'] = cleaned_row.get('IMEI')
                parsed_record['imsi'] = cleaned_row.get('IMSI')
                parsed_record['call_fow_no'] = cleaned_row.get('Call Fow No')
                parsed_record['roam_nw'] = cleaned_row.get('Roam Nw')
                parsed_record['sw_msc_id'] = cleaned_row.get('SW & MSC ID')
                parsed_record['in_tg'] = cleaned_row.get('IN TG')
                parsed_record['out_tg'] = cleaned_row.get('OUT TG')
                parsed_record['vowifi_first_ue_ip'] = cleaned_row.get('Vowifi First UE IP')
                parsed_record['port1'] = cleaned_row.get('Port1')
                parsed_record['vowifi_last_ue_ip'] = cleaned_row.get('Vowifi Last UE IP')
                parsed_record['port2'] = cleaned_row.get('Port2')
                
                records.append(parsed_record)
        
        if records:
            # Insert records into SQLite
            insert_query = '''
            INSERT INTO cdrs (target_no, call_type, toc, b_party_no, lrn_no, lrn_tsp_lsa, 
                            datetime, duration_seconds, first_cgi_lat, first_cgi_long, first_cgi,
                            last_cgi_lat, last_cgi_long, last_cgi, smsc_no, service_type,
                            imei, imsi, call_fow_no, roam_nw, sw_msc_id, in_tg, out_tg,
                            vowifi_first_ue_ip, port1, vowifi_last_ue_ip, port2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            
            for record in records:
                cursor.execute(insert_query, (
                    record['target_no'], record['call_type'], record['toc'], 
                    record['b_party_no'], record['lrn_no'], record['lrn_tsp_lsa'],
                    record['datetime'], record['duration_seconds'], 
                    record['first_cgi_lat'], record['first_cgi_long'], record['first_cgi'],
                    record['last_cgi_lat'], record['last_cgi_long'], record['last_cgi'],
                    record['smsc_no'], record['service_type'], record['imei'], record['imsi'],
                    record['call_fow_no'], record['roam_nw'], record['sw_msc_id'],
                    record['in_tg'], record['out_tg'], record['vowifi_first_ue_ip'],
                    record['port1'], record['vowifi_last_ue_ip'], record['port2']
                ))
            
            conn.commit()
            message = f"Successfully inserted {len(records)} records into SQLite database."
            print(message)
            return True, message
        else:
            message = "No records found in the CSV file."
            print(message)
            return False, message
    
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        return False, error_msg
    finally:
        if conn:
            conn.close()


class CDRUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CDR SQLite Uploader")
        self.root.geometry("700x600")
        self.root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Variables
        self.csv_file_path = tk.StringVar()
        self.db_path = tk.StringVar(value="cdr_database.db")
        self.is_uploading = False
        
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="CDR SQLite Uploader",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=(0, 20))
        
        # SQLite Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="SQLite Configuration", padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Database Path
        db_path_frame = ttk.Frame(config_frame)
        db_path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(db_path_frame, text="DB Path:", width=12).pack(side=tk.LEFT)
        db_entry = ttk.Entry(db_path_frame, textvariable=self.db_path, width=30)
        db_entry.pack(side=tk.LEFT, padx=5)
        
        # File Selection Section
        file_frame = ttk.LabelFrame(main_frame, text="CSV File Selection", padding="15")
        file_frame.pack(fill=tk.X, pady=(0, 15))
        
        file_path_frame = ttk.Frame(file_frame)
        file_path_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_path_frame, text="File:", width=12).pack(side=tk.LEFT)
        file_entry = ttk.Entry(file_path_frame, textvariable=self.csv_file_path, width=35)
        file_entry.pack(side=tk.LEFT, padx=5)
        browse_btn = ttk.Button(
            file_path_frame,
            text="Browse",
            width=10,
            command=self.browse_file,
        )
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        # Upload Button
        self.upload_btn = ttk.Button(
            main_frame,
            text="Upload to SQLite",
            width=25,
            command=self.start_upload,
            style='Accent.TButton'
        )
        self.upload_btn.pack(pady=15)
        
        # Progress Frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=660
        )
        self.progress_bar.pack()
        
        # Status Label
        self.status_label = ttk.Label(
            main_frame,
            text="Ready to upload",
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=5)
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="Upload Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            width=75,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Clear Log Button
        clear_log_btn = ttk.Button(
            log_frame,
            text="Clear Log",
            command=self.clear_log,
            width=15
        )
        clear_log_btn.pack(pady=(5, 0))

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            self.csv_file_path.set(filename)
            self.log_message(f"Selected file: {filename}")

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def start_upload(self):
        # Validate inputs
        if self.is_uploading:
            messagebox.showwarning("Upload in Progress", "An upload is already in progress!")
            return
        
        if not self.csv_file_path.get():
            messagebox.showerror("Error", "Please select a CSV file!")
            return
        
        if not self.db_path.get():
            messagebox.showerror("Error", "Please enter a database path!")
            return
        
        # Start upload in a separate thread
        self.is_uploading = True
        upload_thread = threading.Thread(target=self.upload_data)
        upload_thread.daemon = True
        upload_thread.start()

    def upload_data(self):
        try:
            self.upload_btn.config(state='disabled')
            self.progress_bar.start(10)
            self.status_label.config(text="Uploading...")
            
            self.log_message("=" * 60)
            self.log_message(f"Starting upload process...")
            self.log_message(f"File: {self.csv_file_path.get()}")
            self.log_message(f"Database: {self.db_path.get()}")
            self.log_message("-" * 60)
            
            success, message = upload_csv_to_sqlite(
                self.csv_file_path.get(),
                db_path=self.db_path.get()
            )
            
            self.log_message(message)
            
            if success:
                self.status_label.config(text="Upload completed successfully!")
                messagebox.showinfo("Success", message)
            else:
                self.status_label.config(text="Upload failed!")
                messagebox.showerror("Error", message)
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_message(error_msg)
            self.status_label.config(text="Upload failed with error!")
            messagebox.showerror("Error", error_msg)
        
        finally:
            self.progress_bar.stop()
            self.upload_btn.config(state='normal')
            self.is_uploading = False
            self.log_message("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Upload CSV data to SQLite')
    parser.add_argument('csv_file', help='Path to the CSV file')
    parser.add_argument('--db', default='cdr_database.db', help='Path to SQLite database file')
    args = parser.parse_args()
    
    upload_csv_to_sqlite(args.csv_file, db_path=args.db)


if __name__ == '__main__':
    root = tk.Tk()
    app = CDRUploaderGUI(root)
    root.mainloop()
