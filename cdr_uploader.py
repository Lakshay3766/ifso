#!/usr/bin/env python3
import argparse























































































































































































































    main()if __name__ == '__main__':    root.mainloop()    app = CDRUploaderGUI(root)    root = tk.Tk()def main():            self.log_message("=" * 60)            self.is_uploading = False            self.upload_btn.config(state='normal')            self.progress_bar.stop()        finally:                    messagebox.showerror("Error", error_msg)            self.status_label.config(text="Upload failed with error!")            self.log_message(error_msg)            error_msg = f"Error: {str(e)}"        except Exception as e:                        messagebox.showerror("Error", message)                self.status_label.config(text="Upload failed!")            else:                messagebox.showinfo("Success", message)                self.status_label.config(text="Upload completed successfully!")            if success:                        self.log_message(message)                        )                mongo_port=self.mongo_port.get()                mongo_host=self.mongo_host.get(),                self.csv_file_path.get(),            success, message = upload_csv_to_mongodb(        try:                self.log_message("-" * 60)        self.log_message(f"MongoDB: {self.mongo_host.get()}:{self.mongo_port.get()}")        self.log_message(f"File: {self.csv_file_path.get()}")        self.log_message(f"Starting upload process...")        self.log_message("=" * 60)                self.status_label.config(text="Uploading...")        self.progress_bar.start(10)        self.upload_btn.config(state='disabled')        self.is_uploading = True    def upload_data(self):            upload_thread.start()        upload_thread.daemon = True        upload_thread = threading.Thread(target=self.upload_data)        # Start upload in a separate thread                    return            messagebox.showerror("Error", "Please enter a valid port number (1-65535)!")        except:                raise ValueError()            if port <= 0 or port > 65535:            port = self.mongo_port.get()        try:                    return            messagebox.showerror("Error", "Please enter MongoDB host!")        if not self.mongo_host.get():                    return            messagebox.showerror("Error", "Please select a CSV file!")        if not self.csv_file_path.get():        # Validate inputs                    return            messagebox.showwarning("Upload in Progress", "An upload is already in progress!")        if self.is_uploading:    def start_upload(self):            self.log_text.delete(1.0, tk.END)    def clear_log(self):            self.log_text.see(tk.END)        self.log_text.insert(tk.END, f"{message}\n")    def log_message(self, message):                self.log_message(f"Selected file: {filename}")            self.csv_file_path.set(filename)        if filename:        )            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]            title="Select CSV File",        filename = filedialog.askopenfilename(    def browse_file(self):            clear_log_btn.pack(pady=(5, 0))        )            width=15            command=self.clear_log,            text="Clear Log",            log_frame,        clear_log_btn = ttk.Button(        # Clear Log Button                self.log_text.pack(fill=tk.BOTH, expand=True)        )            font=("Courier", 9)            wrap=tk.WORD,            width=75,            height=10,            log_frame,        self.log_text = scrolledtext.ScrolledText(                log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))        log_frame = ttk.LabelFrame(main_frame, text="Upload Log", padding="10")        # Log Section                self.status_label.pack(pady=5)        )            font=("Helvetica", 10)            text="Ready to upload",             main_frame,         self.status_label = ttk.Label(        # Status Label                self.progress_bar.pack()        )            length=660            mode='indeterminate',            progress_frame,         self.progress_bar = ttk.Progressbar(                progress_frame.pack(fill=tk.X, pady=(0, 10))        progress_frame = ttk.Frame(main_frame)        # Progress Frame                self.upload_btn.pack(pady=15)        )            style='Accent.TButton'            width=25,            command=self.start_upload,            text="Upload to MongoDB",            main_frame,        self.upload_btn = ttk.Button(        # Upload Button                browse_btn.pack(side=tk.LEFT, padx=5)        )            width=10            command=self.browse_file,            text="Browse",             file_path_frame,         browse_btn = ttk.Button(                file_entry.pack(side=tk.LEFT, padx=5)        file_entry = ttk.Entry(file_path_frame, textvariable=self.csv_file_path, width=35)        ttk.Label(file_path_frame, text="File:", width=12).pack(side=tk.LEFT)                file_path_frame.pack(fill=tk.X, pady=5)        file_path_frame = ttk.Frame(file_frame)                file_frame.pack(fill=tk.X, pady=(0, 15))        file_frame = ttk.LabelFrame(main_frame, text="CSV File Selection", padding="15")        # File Selection Section                port_entry.pack(side=tk.LEFT, padx=5)        port_entry = ttk.Entry(port_frame, textvariable=self.mongo_port, width=30)        ttk.Label(port_frame, text="Port:", width=12).pack(side=tk.LEFT)        port_frame.pack(fill=tk.X, pady=5)        port_frame = ttk.Frame(config_frame)        # Port                host_entry.pack(side=tk.LEFT, padx=5)        host_entry = ttk.Entry(host_frame, textvariable=self.mongo_host, width=30)        ttk.Label(host_frame, text="Host:", width=12).pack(side=tk.LEFT)        host_frame.pack(fill=tk.X, pady=5)        host_frame = ttk.Frame(config_frame)        # Host                config_frame.pack(fill=tk.X, pady=(0, 15))        config_frame = ttk.LabelFrame(main_frame, text="MongoDB Configuration", padding="15")        # MongoDB Configuration Section                title_label.pack(pady=(0, 20))        )            font=("Helvetica", 18, "bold")            text="CDR MongoDB Uploader",             main_frame,         title_label = ttk.Label(        # Title                main_frame.pack(fill=tk.BOTH, expand=True)        main_frame = ttk.Frame(self.root, padding="20")        # Main frame    def create_widgets(self):            self.create_widgets()                self.is_uploading = False        self.mongo_port = tk.IntVar(value=27017)        self.mongo_host = tk.StringVar(value="localhost")        self.csv_file_path = tk.StringVar()        # Variables                style.theme_use('clam')        style = ttk.Style()        # Configure style                self.root.resizable(False, False)        self.root.geometry("700x600")        self.root.title("CDR MongoDB Uploader")        self.root = root    def __init__(self, root):class CDRUploaderGUI:from cdr_uploader import upload_csv_to_mongodbimport threadingfrom tkinter import ttk, filedialog, messagebox, scrolledtextimport csv
from pymongo import MongoClient
from datetime import datetime
import os

def parse_lat_long(lat_long_str):
    if lat_long_str and lat_long_str != '---':
        try:
            lat, long = lat_long_str.split('/')
            return float(lat), float(long)
        except ValueError:
            return None, None
    return None, None

def upload_csv_to_mongodb(csv_file_path, mongo_host='localhost', mongo_port=27017):
    try:
        # Connect to local MongoDB
        client = MongoClient(
            host=mongo_host,
            port=mongo_port,
            serverSelectionTimeoutMS=5000
        )
        # Test connection
        client.admin.command('ping')
        
        db = client['cdr_database']  # Database name
        collection = db['cdrs']  # Collection name
        
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
            # Insert records into MongoDB
            result = collection.insert_many(records)
            message = f"Successfully inserted {len(result.inserted_ids)} records into MongoDB."
            print(message)
            return True, message
        else:
            message = "No records found in the CSV file."
            print(message)
            return False, message
        
        # Close connection
        client.close()
    
    except Exception as e:
        error_msg = f"An error occurred: {e}"
        print(error_msg)
        return False, error_msg

def main():
    parser = argparse.ArgumentParser(description='Upload CSV data to MongoDB')
    parser.add_argument('csv_file', help='Path to the CSV file')
    args = parser.parse_args()
    
    upload_csv_to_mongodb(args.csv_file)

if __name__ == '__main__':
    main()