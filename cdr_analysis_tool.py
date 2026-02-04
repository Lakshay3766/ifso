#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sqlite3
import csv
from datetime import datetime
import os
from io import StringIO

class CDRAnalysisTool:
    def __init__(self, root):
        self.root = root
        self.root.title("CDR Analysis & Investigation Tool")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        
        self.db_path = "cdr_database.db"
        self.setup_ui()
    
    def setup_ui(self):
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Upload CSV", command=self.upload_csv)
        file_menu.add_command(label="Change Database", command=self.change_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self.home_frame = ttk.Frame(self.notebook)
        self.search_frame = ttk.Frame(self.notebook)
        self.groups_frame = ttk.Frame(self.notebook)
        self.analytics_frame = ttk.Frame(self.notebook)
        self.database_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.home_frame, text="Home")
        self.notebook.add(self.search_frame, text="Search")
        self.notebook.add(self.groups_frame, text="Groups")
        self.notebook.add(self.analytics_frame, text="Analytics")
        self.notebook.add(self.database_frame, text="Database")
        
        self.create_home_tab()
        self.create_search_tab()
        self.create_groups_tab()
        self.create_analytics_tab()
        self.create_database_tab()
    
    def create_home_tab(self):
        frame = ttk.Frame(self.home_frame, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(frame, text="CDR Analysis & Investigation Tool", 
                         font=("Helvetica", 18, "bold"))
        title.pack(pady=20)
        
        # Quick stats
        stats_frame = ttk.LabelFrame(frame, text="Quick Statistics", padding="15")
        stats_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(stats_frame, text="Upload CSV File", command=self.upload_csv).pack(pady=10)
        
        info_text = scrolledtext.ScrolledText(frame, height=15, width=100, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True, pady=10)
        
        info = """
Welcome to CDR Analysis & Investigation Tool

This application provides comprehensive analysis of Call Data Records (CDR).

Features:
- Upload CSV files to SQLite database
- Search and filter CDR records
- Analyze groups and patterns
- Generate detailed analytics and reports
- View and manage database records

Quick Start:
1. Go to File menu and click "Upload CSV"
2. Select your CSV file
3. Use Search tab to find records
4. Use Analytics tab for detailed analysis
5. Use Groups tab for pattern analysis

The tool stores all data in a local SQLite database for offline access.
        """
        
        info_text.insert(1.0, info)
        info_text.config(state=tk.DISABLED)
    
    def create_search_tab(self):
        frame = ttk.Frame(self.search_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Search controls
        search_frame = ttk.LabelFrame(frame, text="Search Filters", padding="10")
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="A Party (Caller):").grid(row=0, column=0, padx=5, pady=5)
        self.search_a_party = ttk.Entry(search_frame, width=20)
        self.search_a_party.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(search_frame, text="B Party (Receiver):").grid(row=0, column=2, padx=5, pady=5)
        self.search_b_party = ttk.Entry(search_frame, width=20)
        self.search_b_party.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.search_date = ttk.Entry(search_frame, width=20)
        self.search_date.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(search_frame, text="IMEI:").grid(row=1, column=2, padx=5, pady=5)
        self.search_imei = ttk.Entry(search_frame, width=20)
        self.search_imei.grid(row=1, column=3, padx=5, pady=5)
        
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Search", command=self.search_records).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        # Results table
        table_frame = ttk.LabelFrame(frame, text="Search Results", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        self.search_tree = ttk.Treeview(table_frame, columns=("A_PARTY", "B_PARTY", "DATE", "TIME", "DURATION", "CALL_TYPE", "IMEI"), 
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.search_tree.yview)
        hsb.config(command=self.search_tree.xview)
        
        self.search_tree.column("#0", width=80, minwidth=80)
        self.search_tree.column("A_PARTY", width=100, minwidth=100)
        self.search_tree.column("B_PARTY", width=100, minwidth=100)
        self.search_tree.column("DATE", width=100, minwidth=100)
        self.search_tree.column("TIME", width=80, minwidth=80)
        self.search_tree.column("DURATION", width=80, minwidth=80)
        self.search_tree.column("CALL_TYPE", width=80, minwidth=80)
        self.search_tree.column("IMEI", width=150, minwidth=150)
        
        self.search_tree.heading("#0", text="ID", anchor=tk.W)
        self.search_tree.heading("A_PARTY", text="A Party", anchor=tk.W)
        self.search_tree.heading("B_PARTY", text="B Party", anchor=tk.W)
        self.search_tree.heading("DATE", text="Date", anchor=tk.W)
        self.search_tree.heading("TIME", text="Time", anchor=tk.W)
        self.search_tree.heading("DURATION", text="Duration", anchor=tk.W)
        self.search_tree.heading("CALL_TYPE", text="Call Type", anchor=tk.W)
        self.search_tree.heading("IMEI", text="IMEI", anchor=tk.W)
        
        self.search_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def create_groups_tab(self):
        frame = ttk.Frame(self.groups_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(frame, text="Groups Analysis", font=("Helvetica", 14, "bold"))
        title.pack(pady=10)
        
        # Group analysis options
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Number (A+B)", command=lambda: self.analyze_group("number")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="IMEI", command=lambda: self.analyze_group("imei")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Call Type", command=lambda: self.analyze_group("call_type")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Service Type", command=lambda: self.analyze_group("service_type")).pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.LabelFrame(frame, text="Group Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        vsb = ttk.Scrollbar(results_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL)
        
        self.groups_tree = ttk.Treeview(results_frame, columns=("VALUE", "COUNT"), 
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.groups_tree.yview)
        hsb.config(command=self.groups_tree.xview)
        
        self.groups_tree.column("#0", width=200, minwidth=200)
        self.groups_tree.column("VALUE", width=300, minwidth=300)
        self.groups_tree.column("COUNT", width=100, minwidth=100)
        
        self.groups_tree.heading("#0", text="Group Type", anchor=tk.W)
        self.groups_tree.heading("VALUE", text="Value", anchor=tk.W)
        self.groups_tree.heading("COUNT", text="Count", anchor=tk.W)
        
        self.groups_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def create_analytics_tab(self):
        frame = ttk.Frame(self.analytics_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        title = ttk.Label(frame, text="Analytics & Reports", font=("Helvetica", 14, "bold"))
        title.pack(pady=10)
        
        # Analytics buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Max Call Duration", command=lambda: self.get_analytics("max_duration")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Max IMEI Used", command=lambda: self.get_analytics("max_imei")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Total Records", command=lambda: self.get_analytics("total_records")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Call Statistics", command=lambda: self.get_analytics("call_stats")).pack(side=tk.LEFT, padx=5)
        
        # Results
        results_frame = ttk.LabelFrame(frame, text="Analytics Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.analytics_text = scrolledtext.ScrolledText(results_frame, height=20, width=100, wrap=tk.WORD)
        self.analytics_text.pack(fill=tk.BOTH, expand=True)
    
    def create_database_tab(self):
        frame = ttk.Frame(self.database_frame, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Database controls
        control_frame = ttk.LabelFrame(frame, text="Database Management", padding="10")
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="Upload CSV File", command=self.upload_csv).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="View All Records", command=self.view_all_records).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Clear Database", command=self.clear_database).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Export to CSV", command=self.export_to_csv).pack(side=tk.LEFT, padx=5, pady=5)
        
        # Records table
        table_frame = ttk.LabelFrame(frame, text="Database Records", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        self.db_tree = ttk.Treeview(table_frame, columns=("A_PARTY", "B_PARTY", "DATE", "TIME", "DURATION", "CALL_TYPE", "IMEI"), 
                                    yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.db_tree.yview)
        hsb.config(command=self.db_tree.xview)
        
        self.db_tree.column("#0", width=80, minwidth=80)
        self.db_tree.column("A_PARTY", width=100, minwidth=100)
        self.db_tree.column("B_PARTY", width=100, minwidth=100)
        self.db_tree.column("DATE", width=100, minwidth=100)
        self.db_tree.column("TIME", width=80, minwidth=80)
        self.db_tree.column("DURATION", width=80, minwidth=80)
        self.db_tree.column("CALL_TYPE", width=80, minwidth=80)
        self.db_tree.column("IMEI", width=150, minwidth=150)
        
        self.db_tree.heading("#0", text="ID", anchor=tk.W)
        self.db_tree.heading("A_PARTY", text="A Party", anchor=tk.W)
        self.db_tree.heading("B_PARTY", text="B Party", anchor=tk.W)
        self.db_tree.heading("DATE", text="Date", anchor=tk.W)
        self.db_tree.heading("TIME", text="Time", anchor=tk.W)
        self.db_tree.heading("DURATION", text="Duration", anchor=tk.W)
        self.db_tree.heading("CALL_TYPE", text="Call Type", anchor=tk.W)
        self.db_tree.heading("IMEI", text="IMEI", anchor=tk.W)
        
        self.db_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
    
    def upload_csv(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create table if not exists
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
            
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                lines = csvfile.readlines()
                header_index = None
                for i, line in enumerate(lines):
                    if 'Target No' in line:
                        header_index = i
                        break
                
                if header_index is None:
                    messagebox.showerror("Error", "Header line not found in CSV file.")
                    return
                
                csv_data = StringIO(''.join(lines[header_index:]))
                reader = csv.DictReader(csv_data)
                count = 0
                
                for row in reader:
                    cleaned_row = {k: v for k, v in row.items() if k is not None}
                    
                    try:
                        date_str = cleaned_row.get('Date', '')
                        if date_str:
                            date_str = date_str.strip("'")
                        time_str = cleaned_row.get('Time', '')
                        
                        datetime_obj = None
                        if date_str and time_str:
                            try:
                                datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
                            except:
                                pass
                        
                        cursor.execute('''
                        INSERT INTO cdrs (target_no, call_type, toc, b_party_no, lrn_no, lrn_tsp_lsa,
                                        datetime, duration_seconds, first_cgi_lat, first_cgi_long, first_cgi,
                                        last_cgi_lat, last_cgi_long, last_cgi, smsc_no, service_type,
                                        imei, imsi, call_fow_no, roam_nw, sw_msc_id, in_tg, out_tg,
                                        vowifi_first_ue_ip, port1, vowifi_last_ue_ip, port2)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            cleaned_row.get('Target No'),
                            cleaned_row.get('Call Type'),
                            cleaned_row.get('TOC'),
                            cleaned_row.get('B Party No'),
                            cleaned_row.get('LRN No'),
                            cleaned_row.get('LRN TSP-LSA'),
                            datetime_obj,
                            int(cleaned_row.get('Dur(s)', 0)) if cleaned_row.get('Dur(s)') else None,
                            None, None,
                            cleaned_row.get('First CGI'),
                            None, None,
                            cleaned_row.get('Last CGI'),
                            cleaned_row.get('SMSC No'),
                            cleaned_row.get('Service Type'),
                            cleaned_row.get('IMEI'),
                            cleaned_row.get('IMSI'),
                            cleaned_row.get('Call Fow No'),
                            cleaned_row.get('Roam Nw'),
                            cleaned_row.get('SW & MSC ID'),
                            cleaned_row.get('IN TG'),
                            cleaned_row.get('OUT TG'),
                            cleaned_row.get('Vowifi First UE IP'),
                            cleaned_row.get('Port1'),
                            cleaned_row.get('Vowifi Last UE IP'),
                            cleaned_row.get('Port2')
                        ))
                        count += 1
                    except Exception as e:
                        continue
                
                conn.commit()
                messagebox.showinfo("Success", f"Uploaded {count} records successfully!")
                self.view_all_records()
        
        except Exception as e:
            messagebox.showerror("Error", f"Error uploading file: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def search_records(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, target_no, b_party_no, datetime, duration_seconds, call_type, imei FROM cdrs WHERE 1=1"
            
            if self.search_a_party.get():
                query += f" AND target_no LIKE '%{self.search_a_party.get()}%'"
            if self.search_b_party.get():
                query += f" AND b_party_no LIKE '%{self.search_b_party.get()}%'"
            if self.search_date.get():
                query += f" AND DATE(datetime) = '{self.search_date.get()}'"
            if self.search_imei.get():
                query += f" AND imei LIKE '%{self.search_imei.get()}%'"
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)
            
            for row in results:
                date_str = row[3][:10] if row[3] else ""
                time_str = row[3][11:19] if row[3] else ""
                self.search_tree.insert("", tk.END, text=str(row[0]), 
                                       values=(row[1], row[2], date_str, time_str, row[4], row[5], row[6]))
            
            messagebox.showinfo("Search", f"Found {len(results)} records")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {str(e)}")
    
    def clear_search(self):
        self.search_a_party.delete(0, tk.END)
        self.search_b_party.delete(0, tk.END)
        self.search_date.delete(0, tk.END)
        self.search_imei.delete(0, tk.END)
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)
    
    def analyze_group(self, group_type):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in self.groups_tree.get_children():
                self.groups_tree.delete(item)
            
            if group_type == "number":
                cursor.execute("SELECT target_no, COUNT(*) FROM cdrs WHERE target_no IS NOT NULL GROUP BY target_no ORDER BY COUNT(*) DESC LIMIT 50")
            elif group_type == "imei":
                cursor.execute("SELECT imei, COUNT(*) FROM cdrs WHERE imei IS NOT NULL GROUP BY imei ORDER BY COUNT(*) DESC LIMIT 50")
            elif group_type == "call_type":
                cursor.execute("SELECT call_type, COUNT(*) FROM cdrs WHERE call_type IS NOT NULL GROUP BY call_type")
            elif group_type == "service_type":
                cursor.execute("SELECT service_type, COUNT(*) FROM cdrs WHERE service_type IS NOT NULL GROUP BY service_type")
            
            results = cursor.fetchall()
            
            for i, (value, count) in enumerate(results):
                self.groups_tree.insert("", tk.END, text=f"{group_type}_{i}", 
                                       values=(str(value)[:50], count))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Analysis error: {str(e)}")
    
    def get_analytics(self, analytics_type):
        self.analytics_text.config(state=tk.NORMAL)
        self.analytics_text.delete(1.0, tk.END)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if analytics_type == "max_duration":
                cursor.execute("SELECT target_no, b_party_no, duration_seconds FROM cdrs WHERE duration_seconds IS NOT NULL ORDER BY duration_seconds DESC LIMIT 10")
                results = cursor.fetchall()
                text = "Top 10 Max Call Duration Records:\n\n"
                for row in results:
                    text += f"A Party: {row[0]}\nB Party: {row[1]}\nDuration: {row[2]} seconds\n\n"
                self.analytics_text.insert(1.0, text)
            
            elif analytics_type == "max_imei":
                cursor.execute("SELECT imei, COUNT(*) FROM cdrs WHERE imei IS NOT NULL GROUP BY imei ORDER BY COUNT(*) DESC LIMIT 10")
                results = cursor.fetchall()
                text = "Top 10 Most Used IMEI:\n\n"
                for row in results:
                    text += f"IMEI: {row[0]}\nUsage Count: {row[1]}\n\n"
                self.analytics_text.insert(1.0, text)
            
            elif analytics_type == "total_records":
                cursor.execute("SELECT COUNT(*) FROM cdrs")
                count = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(DISTINCT target_no) FROM cdrs")
                unique_a_party = cursor.fetchone()[0]
                cursor.execute("SELECT COUNT(DISTINCT b_party_no) FROM cdrs")
                unique_b_party = cursor.fetchone()[0]
                
                text = f"Database Statistics:\n\n"
                text += f"Total Records: {count}\n"
                text += f"Unique A Party Numbers: {unique_a_party}\n"
                text += f"Unique B Party Numbers: {unique_b_party}\n"
                self.analytics_text.insert(1.0, text)
            
            elif analytics_type == "call_stats":
                cursor.execute("SELECT call_type, COUNT(*) FROM cdrs WHERE call_type IS NOT NULL GROUP BY call_type")
                results = cursor.fetchall()
                text = "Call Type Statistics:\n\n"
                for row in results:
                    text += f"Call Type: {row[0]}\nCount: {row[1]}\n\n"
                self.analytics_text.insert(1.0, text)
            
            conn.close()
        except Exception as e:
            self.analytics_text.insert(1.0, f"Error: {str(e)}")
        
        self.analytics_text.config(state=tk.DISABLED)
    
    def view_all_records(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, target_no, b_party_no, datetime, duration_seconds, call_type, imei FROM cdrs LIMIT 1000")
            results = cursor.fetchall()
            
            for item in self.db_tree.get_children():
                self.db_tree.delete(item)
            
            for row in results:
                date_str = row[3][:10] if row[3] else ""
                time_str = row[3][11:19] if row[3] else ""
                self.db_tree.insert("", tk.END, text=str(row[0]), 
                                   values=(row[1], row[2], date_str, time_str, row[4], row[5], row[6]))
            
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error loading records: {str(e)}")
    
    def clear_database(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all database records?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM cdrs")
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Database cleared successfully!")
                self.view_all_records()
            except Exception as e:
                messagebox.showerror("Error", f"Error clearing database: {str(e)}")
    
    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM cdrs")
            results = cursor.fetchall()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([description[0] for description in cursor.description])
                writer.writerows(results)
            
            messagebox.showinfo("Success", f"Exported {len(results)} records to {file_path}")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Export error: {str(e)}")
    
    def change_database(self):
        db_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if db_path:
            self.db_path = db_path
            messagebox.showinfo("Success", f"Database changed to: {db_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CDRAnalysisTool(root)
    root.mainloop()
