#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import sqlite3
import csv
from datetime import datetime
import os
import json
import math
from urllib import request as urlrequest, error as urlerror
from database.db_manager import DatabaseManager
from database.csv_importer import CSVImporter
from database.cell_tower_importer import CellTowerImporter

class CDRAnalysisTool:
    def __init__(self, root, case_name=None, db_path=None, current_user=None):
        self.root = root
        self.current_user = current_user
        self.root.title("CDR Analysis & Investigation Tool")
        self.root.geometry("1400x800")
        self.root.resizable(True, True)
        
        # Initialize attributes to avoid lint errors and runtime issues
        self.sidebar_collapsed = False
        self.header_vars = {}
        self.pages = {}
        self.metric_cards = {}
        
        # UI Frames
        self.home_frame = None
        self.search_frame = None
        self.groups_frame = None
        self.analytics_frame = None
        self.network_frame = None
        self.location_frame = None
        self.reports_frame = None
        self.database_frame = None
        self.settings_frame = None
        
        # Widgets
        self.risk_value_label = None
        self.risk_canvas = None
        self.activity_log = None
        self.case_status_var = None
        self.upload_tabs_notebook = None
        
        # Tab specific vars
        self.search_tree = None
        self.groups_tree = None
        self.db_tree = None
        self.location_tree = None
        self.network_view = None
        self.network_drag = None
        self.network_data = None
        self.network_canvas = None
        self.location_canvas = None
        self.location_summary = None
        self.analytics_text = None
        self.analytics_chart_canvas = None
        self.analytics_notebook = None
        self.analytics_tabs = None
        self.ai_summary_text = None
        self.ai_risk_label = None
        self.ai_behavior_label = None
        
        # Control vars
        self.search_a_party = None
        self.search_b_party = None
        self.search_date = None
        self.search_imei = None
        self.search_import_var = None
        self.search_import_combo = None
        
        self.analytics_target_var = None
        self.analytics_date_from = None
        self.analytics_date_to = None
        
        self.network_target_var = None
        self.network_date_from = None
        self.network_date_to = None
        self.network_min_freq = None
        self.network_min_duration = None
        
        self.location_target_var = None
        self.location_date_from = None
        self.location_date_to = None
        
        self.db_import_var = None
        self.db_import_combo = None
        
        self.report_include_charts = None
        self.report_include_ai = None
        self.report_include_network = None
        self.report_include_timeline = None
        self.report_include_contacts = None

        self._load_env()
        self._configure_style()
        
        self.db_path = db_path or "cdr_database.db"
        self.case_name = case_name
        self.db_manager = DatabaseManager(self.db_path)
        self.csv_importer = CSVImporter(self.db_manager)
        self.cell_tower_importer = CellTowerImporter(self.db_manager)
        self.import_batches = {}
        self.cell_tower_status_label = None
        self.setup_ui()

    def _load_env(self):
        if os.environ.get("GOOGLE_AI_API_KEY"):
            return
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(base_dir, ".env")
        if not os.path.exists(env_path):
            return
        try:
            with open(env_path, "r", encoding="utf-8") as env_file:
                for line in env_file:
                    raw = line.strip()
                    if not raw or raw.startswith("#") or "=" not in raw:
                        continue
                    key, value = raw.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    if key and value and not os.environ.get(key):
                        os.environ[key] = value
        except Exception:
            return
    
    def _configure_style(self):
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        
        # Light Theme Palette
        bg_color = "#f8fafc"      # Very light slate/white
        card_color = "#ffffff"    # Pure white
        sidebar_color = "#ffffff" # White sidebar
        header_color = "#f1f5f9"  # Light gray header
        text_color = "#0f172a"    # Dark slate
        muted_color = "#64748b"   # Slate-500
        accent_color = "#2563eb"  # Professional Blue
        
        style.configure("TFrame", background=bg_color)
        style.configure("Card.TFrame", background=card_color, relief="flat", borderwidth=1, bordercolor="#e2e8f0")
        style.configure("Sidebar.TFrame", background=sidebar_color)
        style.configure("Header.TFrame", background=header_color)
        
        style.configure("Accent.TButton", background=accent_color, foreground="#ffffff", borderwidth=0)
        style.map("Accent.TButton", background=[("active", "#1d4ed8")])
        
        style.configure("Muted.TLabel", foreground=muted_color, background=header_color)
        style.configure("Title.TLabel", foreground=text_color, background=header_color, font=("Helvetica", 16, "bold"))
        style.configure("Section.TLabel", foreground="#334155", background=card_color, font=("Helvetica", 11, "bold"))
        
        style.configure("StatValue.TLabel", foreground=text_color, background=card_color, font=("Helvetica", 18, "bold"))
        style.configure("StatTitle.TLabel", foreground=muted_color, background=card_color, font=("Helvetica", 9))
        
        style.configure("Badge.TLabel", foreground="#166534", background="#dcfce7", font=("Helvetica", 9, "bold"))
        style.configure("Danger.TLabel", foreground="#dc2626", background=card_color, font=("Helvetica", 9, "bold"))
        style.configure("Success.TLabel", foreground="#166534", background=card_color, font=("Helvetica", 9, "bold"))
        
        style.configure("TLabel", foreground=text_color, background=bg_color)
        style.configure("TButton", background="#e2e8f0", foreground=text_color)
        style.map("TButton", background=[("active", "#cbd5e1")])
        
        style.configure("TEntry", fieldbackground="#ffffff", foreground=text_color, borderwidth=1, relief="solid", bordercolor="#cbd5e1")
        style.configure("TCombobox", fieldbackground="#ffffff", foreground=text_color)
        
        style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground=text_color, bordercolor="#cbd5e1")
        style.configure("Treeview.Heading", background="#f1f5f9", foreground="#334155", font=("Helvetica", 9, "bold"))
        
        style.configure("TNotebook", background=bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#e2e8f0", foreground="#475569", padding=(10, 6))
        style.map("TNotebook.Tab", background=[("selected", "#ffffff")], foreground=[("selected", accent_color)])
        
        self.root.configure(background=bg_color)
    
    def setup_ui(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Upload CSV", command=self.upload_csv)
        file_menu.add_command(label="Change Database", command=self.change_database)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        shell = ttk.Frame(self.root, style="TFrame")
        shell.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)
        shell.columnconfigure(1, weight=1)
        shell.rowconfigure(1, weight=1)

        header = ttk.Frame(shell, style="Header.TFrame", padding=12)
        header.grid(row=0, column=0, columnspan=2, sticky="new", pady=(0, 10))
        header.columnconfigure(1, weight=1)

        sidebar = ttk.Frame(shell, width=240, style="Sidebar.TFrame", padding=12)
        sidebar.grid(row=1, column=0, sticky="nsw", padx=(0, 10))

        content = ttk.Frame(shell, style="TFrame")
        content.grid(row=1, column=1, sticky="nsew")
        content.rowconfigure(0, weight=1)
        content.columnconfigure(0, weight=1)

        self.sidebar_collapsed = False

        header_left = ttk.Frame(header, style="Header.TFrame")
        header_left.grid(row=0, column=0, sticky="w")

        header_center = ttk.Frame(header, style="Header.TFrame")
        header_center.grid(row=0, column=1, sticky="ew")
        header_center.columnconfigure(0, weight=1)

        header_actions = ttk.Frame(header, style="Header.TFrame")
        header_actions.grid(row=0, column=2, sticky="e")

        toggle_btn = ttk.Button(header_left, text="≡", width=3, command=lambda: self._toggle_sidebar(sidebar))
        toggle_btn.pack(side=tk.LEFT, padx=(0, 10))

        title = ttk.Label(header_left, text="Forensic Intelligence Console", style="Title.TLabel")
        title.pack(side=tk.LEFT)

        self.header_vars = {
            "case_id": tk.StringVar(),
            "case_name": tk.StringVar(),
            "target": tk.StringVar(),
            "date_range": tk.StringVar(),
            "records": tk.StringVar(),
            "contacts": tk.StringVar(),
            "imeis": tk.StringVar(),
            "risk": tk.StringVar(),
        }

        info_row = ttk.Frame(header_center, style="Header.TFrame")
        info_row.pack(fill=tk.X)

        def info_block(parent, label, var):
            block = ttk.Frame(parent, style="Header.TFrame")
            ttk.Label(block, text=label, style="Muted.TLabel").pack(anchor=tk.W)
            ttk.Label(block, textvariable=var, style="TLabel", font=("Helvetica", 11, "bold")).pack(anchor=tk.W)
            return block

        info_block(info_row, "Case ID", self.header_vars["case_id"]).pack(side=tk.LEFT, padx=(0, 14))
        info_block(info_row, "Case Name", self.header_vars["case_name"]).pack(side=tk.LEFT, padx=(0, 14))
        info_block(info_row, "Target", self.header_vars["target"]).pack(side=tk.LEFT, padx=(0, 14))
        info_block(info_row, "Date Range", self.header_vars["date_range"]).pack(side=tk.LEFT, padx=(0, 14))
        info_block(info_row, "Total Records", self.header_vars["records"]).pack(side=tk.LEFT, padx=(0, 14))
        info_block(info_row, "Unique Contacts", self.header_vars["contacts"]).pack(side=tk.LEFT, padx=(0, 14))
        info_block(info_row, "Unique IMEIs", self.header_vars["imeis"]).pack(side=tk.LEFT, padx=(0, 14))

        risk_frame = ttk.Frame(header_center, style="Header.TFrame")
        risk_frame.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(risk_frame, text="Risk Score", style="Muted.TLabel").pack(side=tk.LEFT, padx=(0, 8))
        self.risk_value_label = ttk.Label(risk_frame, textvariable=self.header_vars["risk"], font=("Helvetica", 11, "bold"))
        self.risk_value_label.pack(side=tk.LEFT, padx=(0, 8))
        self.risk_canvas = tk.Canvas(risk_frame, height=10, width=220, background="#0b1220", highlightthickness=0)
        self.risk_canvas.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(header_actions, text="Upload CDR", style="Accent.TButton", command=self.upload_csv, width=14).pack(side=tk.LEFT, padx=4)
        ttk.Button(header_actions, text="Generate Report", command=lambda: self.show_page("Reports"), width=16).pack(side=tk.LEFT, padx=4)
        ttk.Button(header_actions, text="Export PDF", command=self.export_to_csv, width=12).pack(side=tk.LEFT, padx=4)
        ttk.Button(header_actions, text="AI Re-analyze", command=lambda: self.get_analytics("ai_insights"), width=14).pack(side=tk.LEFT, padx=4)

        nav_title = ttk.Label(sidebar, text="Case Management", style="Section.TLabel")
        nav_title.pack(anchor=tk.W, pady=(0, 8))
        
        self.pages = {}
        self.home_frame = ttk.Frame(content, style="TFrame")
        self.search_frame = ttk.Frame(content, style="TFrame")
        self.groups_frame = ttk.Frame(content, style="TFrame")
        self.analytics_frame = ttk.Frame(content, style="TFrame")
        self.network_frame = ttk.Frame(content, style="TFrame")
        self.location_frame = ttk.Frame(content, style="TFrame")
        self.reports_frame = ttk.Frame(content, style="TFrame")
        self.database_frame = ttk.Frame(content, style="TFrame")
        self.settings_frame = ttk.Frame(content, style="TFrame")
        
        for key, frame in {
            "Dashboard": self.home_frame,
            "Search": self.search_frame,
            "Groups": self.groups_frame,
            "Analytics": self.analytics_frame,
            "Network": self.network_frame,
            "Location": self.location_frame,
            "Reports": self.reports_frame,
            "Database": self.database_frame,
            "Settings": self.settings_frame,
        }.items():
            frame.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = frame
        
        def add_nav_button(label, page_key):
            btn = ttk.Button(
                sidebar,
                text=label,
                style="Accent.TButton" if page_key == "Dashboard" else "TButton",
                command=lambda: self.show_page(page_key),
                width=18,
            )
            btn.pack(fill=tk.X, pady=2)

        add_nav_button("Dashboard", "Dashboard")
        add_nav_button("Upload CDR", "Search")
        add_nav_button("CDR Groups", "Groups")
        add_nav_button("Case Settings", "Settings")

        ttk.Label(sidebar, text="Analysis", style="Section.TLabel").pack(anchor=tk.W, pady=(12, 8))
        add_nav_button("Call Analytics", "Analytics")
        add_nav_button("IMEI Analysis", "Groups")
        add_nav_button("Contact Analysis", "Groups")
        add_nav_button("Location Analysis", "Location")
        add_nav_button("Network Graph", "Network")

        ttk.Label(sidebar, text="Intelligence", style="Section.TLabel").pack(anchor=tk.W, pady=(12, 8))
        add_nav_button("AI Insights", "Analytics")
        add_nav_button("Risk Scoring", "Analytics")
        add_nav_button("Anomaly Detection", "Analytics")

        ttk.Label(sidebar, text="Reports", style="Section.TLabel").pack(anchor=tk.W, pady=(12, 8))
        add_nav_button("Generate Report", "Reports")
        add_nav_button("Export Evidence", "Reports")
        add_nav_button("Audit Logs", "Reports")

        ttk.Label(sidebar, text="System", style="Section.TLabel").pack(anchor=tk.W, pady=(12, 8))
        add_nav_button("Database", "Database")
        add_nav_button("User Management", "Settings")
        add_nav_button("Settings", "Settings")
        
        self.create_home_tab()
        self.create_search_tab()
        self.create_groups_tab()
        self.create_analytics_tab()
        self.create_network_tab()
        self.create_location_tab()
        self.create_reports_tab()
        self.create_database_tab()
        self.create_settings_tab()
        self.refresh_import_sources()
        self._update_header_stats()
        self.show_page("Dashboard")
        self.root.bind_all("<MouseWheel>", self._on_global_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_global_mousewheel, add="+")
        self.root.bind_all("<Button-5>", self._on_global_mousewheel, add="+")
    
    def show_page(self, key):
        frame = self.pages.get(key)
        if frame is not None:
            frame.tkraise()

    def _toggle_sidebar(self, sidebar):
        if self.sidebar_collapsed:
            sidebar.grid()
            self.sidebar_collapsed = False
        else:
            sidebar.grid_remove()
            self.sidebar_collapsed = True

    def _update_header_stats(self):
        case_name = self.case_name or os.path.basename(self.db_path)
        self.header_vars["case_id"].set(f"CASE-{case_name[:6].upper()}")
        self.header_vars["case_name"].set(case_name)
        target, date_range, total, contacts, imeis, risk_score = self._get_header_metrics()
        self.header_vars["target"].set(target or "Unknown")
        self.header_vars["date_range"].set(date_range or "N/A")
        self.header_vars["records"].set(str(total))
        self.header_vars["contacts"].set(str(contacts))
        self.header_vars["imeis"].set(str(imeis))
        self.header_vars["risk"].set(f"{risk_score}/100")
        self._render_risk_bar(risk_score)

    def _get_header_metrics(self):
        target = None
        date_range = None
        total = 0
        contacts = 0
        imeis = 0
        risk_score = 0
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cdrs")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT b_party_no) FROM cdrs WHERE b_party_no IS NOT NULL")
            contacts = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT imei) FROM cdrs WHERE imei IS NOT NULL AND TRIM(imei) != ''")
            imeis = cursor.fetchone()[0]
            cursor.execute(
                "SELECT target_no, COUNT(*) AS c FROM cdrs WHERE target_no IS NOT NULL GROUP BY target_no ORDER BY c DESC LIMIT 1"
            )
            row = cursor.fetchone()
            if row:
                target = row[0]
            cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM cdrs WHERE datetime IS NOT NULL")
            row = cursor.fetchone()
            if row and row[0] and row[1]:
                date_range = f"{row[0][:10]} to {row[1][:10]}"
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM cdrs
                WHERE CAST(strftime('%H', datetime) AS INTEGER) >= 22
                   OR CAST(strftime('%H', datetime) AS INTEGER) < 6
                """
            )
            night_calls = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT imei
                    FROM cdrs
                    WHERE imei IS NOT NULL AND TRIM(imei) != ''
                    GROUP BY imei
                    HAVING COUNT(DISTINCT target_no) >= 2
                )
                """
            )
            shared_imeis = cursor.fetchone()[0]
            risk_score = min(100, int((night_calls / max(total, 1)) * 60 + shared_imeis * 5))
            conn.close()
        except Exception:
            pass
        return target, date_range, total, contacts, imeis, risk_score

    def _render_risk_bar(self, score):
        if not hasattr(self, "risk_canvas"):
            return
        canvas = self.risk_canvas
        canvas.delete("all")
        width = int(canvas.winfo_width() or 220)
        height = int(canvas.winfo_height() or 10)
        fill_width = int(width * max(0, min(score, 100)) / 100)
        color = "#22c55e" if score < 40 else ("#f59e0b" if score < 70 else "#ef4444")
        canvas.create_rectangle(0, 0, width, height, fill="#1f2937", outline="")
        canvas.create_rectangle(0, 0, fill_width, height, fill=color, outline="")

    def _refresh_dashboard_metrics(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM cdrs")
            total_records = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM cdrs WHERE call_type IS NOT NULL AND LOWER(call_type) LIKE '%sms%'")
            total_sms = cursor.fetchone()[0]
            total_calls = max(total_records - total_sms, 0)
            cursor.execute(
                """
                SELECT COUNT(DISTINCT number) FROM (
                    SELECT target_no AS number FROM cdrs WHERE target_no IS NOT NULL
                    UNION
                    SELECT b_party_no AS number FROM cdrs WHERE b_party_no IS NOT NULL
                )
                """
            )
            unique_contacts = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(DISTINCT imei) FROM cdrs WHERE imei IS NOT NULL AND TRIM(imei) != ''")
            unique_imeis = cursor.fetchone()[0]
            cursor.execute("SELECT AVG(duration_seconds) FROM cdrs WHERE duration_seconds IS NOT NULL")
            avg_duration = int(cursor.fetchone()[0] or 0)
            cursor.execute("SELECT MAX(duration_seconds) FROM cdrs WHERE duration_seconds IS NOT NULL")
            max_duration = int(cursor.fetchone()[0] or 0)
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT target_no, SUM(CASE WHEN CAST(strftime('%H', datetime) AS INTEGER) >= 22
                                              OR CAST(strftime('%H', datetime) AS INTEGER) < 6
                                              THEN 1 ELSE 0 END) AS night_calls,
                           COUNT(*) AS total_calls
                    FROM cdrs
                    WHERE target_no IS NOT NULL
                    GROUP BY target_no
                    HAVING total_calls >= 10 AND night_calls >= 3
                )
                """
            )
            suspicious_contacts = cursor.fetchone()[0]
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM (
                    SELECT imei
                    FROM cdrs
                    WHERE imei IS NOT NULL AND TRIM(imei) != ''
                    GROUP BY imei
                    HAVING COUNT(DISTINCT target_no) >= 2
                )
                """
            )
            imei_switching = cursor.fetchone()[0] > 0
            conn.close()
        except Exception:
            return

        def set_card(title, value, foot):
            if title in self.metric_cards:
                value_label, foot_label, _ = self.metric_cards[title]
                value_label.config(text=value)
                foot_label.config(text=foot)

        set_card("Total Calls", str(total_calls), "last 30 days")
        set_card("Total SMS", str(total_sms), "last 30 days")
        set_card("Unique Contacts", str(unique_contacts), "distinct numbers")
        set_card("Unique IMEIs", str(unique_imeis), "distinct devices")
        set_card("Avg Call Duration", f"{avg_duration}s", "overall average")
        set_card("Longest Call", f"{max_duration}s", "max duration")
        set_card("Suspicious Contacts", str(suspicious_contacts), "high-risk")
        set_card("IMEI Switching", "Yes" if imei_switching else "No", "device churn")
    
    def create_home_tab(self):
        frame = ttk.Frame(self.home_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)

        header_row = ttk.Frame(frame, style="TFrame")
        header_row.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(header_row, text="Investigation Overview", font=("Helvetica", 16, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_row, text="Upload CDR", style="Accent.TButton", command=self.upload_csv, width=14).pack(side=tk.RIGHT)

        metrics_grid = ttk.Frame(frame, style="TFrame")
        metrics_grid.grid(row=1, column=0, sticky="nsew")
        for col in range(4):
            metrics_grid.columnconfigure(col, weight=1, uniform="metric")

        self.metric_cards = {}
        card_defs = [
            ("Total Calls", "0", "last 30 days", "ok"),
            ("Total SMS", "0", "last 30 days", "ok"),
            ("Unique Contacts", "0", "distinct numbers", "ok"),
            ("Unique IMEIs", "0", "distinct devices", "ok"),
            ("Avg Call Duration", "0s", "overall average", "ok"),
            ("Longest Call", "0s", "max duration", "warn"),
            ("Suspicious Contacts", "0", "high-risk", "alert"),
            ("IMEI Switching", "No", "device churn", "alert"),
        ]

        for idx, (title, value, foot, tone) in enumerate(card_defs):
            card = ttk.Frame(metrics_grid, style="Card.TFrame", padding=12)
            card.grid(row=idx // 4, column=idx % 4, padx=8, pady=8, sticky="nsew")
            title_label = ttk.Label(card, text=title, style="StatTitle.TLabel")
            title_label.pack(anchor=tk.W)
            value_label = ttk.Label(card, text=value, style="StatValue.TLabel")
            value_label.pack(anchor=tk.W, pady=(4, 2))
            foot_style = "Muted.TLabel" if tone == "ok" else ("Danger.TLabel" if tone == "alert" else "Success.TLabel")
            foot_label = ttk.Label(card, text=foot, style=foot_style)
            foot_label.pack(anchor=tk.W)
            self.metric_cards[title] = (value_label, foot_label, card)

        activity_row = ttk.Frame(frame, style="TFrame")
        activity_row.grid(row=2, column=0, sticky="nsew", pady=(16, 0))
        activity_row.columnconfigure(0, weight=1)
        activity_row.columnconfigure(1, weight=1)

        left_panel = ttk.Frame(activity_row, style="Card.TFrame", padding=12)
        left_panel.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        ttk.Label(left_panel, text="Investigation Workflow", style="Section.TLabel").pack(anchor=tk.W, pady=(0, 8))
        ttk.Button(left_panel, text="Mark as Suspect", width=18).pack(anchor=tk.W, pady=4)
        ttk.Button(left_panel, text="Flag Evidence", width=18).pack(anchor=tk.W, pady=4)
        ttk.Button(left_panel, text="Add Investigator Notes", width=22).pack(anchor=tk.W, pady=4)
        self.case_status_var = tk.StringVar(value="Case Status: Open")
        ttk.Label(left_panel, textvariable=self.case_status_var, style="Muted.TLabel").pack(anchor=tk.W, pady=(10, 0))

        right_panel = ttk.Frame(activity_row, style="Card.TFrame", padding=12)
        right_panel.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        ttk.Label(right_panel, text="Activity Log", style="Section.TLabel").pack(anchor=tk.W, pady=(0, 8))
        self.activity_log = scrolledtext.ScrolledText(right_panel, height=6, wrap=tk.WORD, background="#0b1220", foreground="#e2e8f0", insertbackground="#e2e8f0")
        self.activity_log.pack(fill=tk.BOTH, expand=True)
        self.activity_log.insert(1.0, "• Case opened\n• Data sources validated\n• AI baseline risk computed\n")
        self.activity_log.config(state=tk.DISABLED)

        self._refresh_dashboard_metrics()
    
    def create_search_tab(self):
        frame = ttk.Frame(self.search_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        
        filters_card = ttk.Frame(frame, style="Card.TFrame", padding=16)
        filters_card.pack(fill=tk.X, pady=(0, 12))
        
        left_filters = ttk.Frame(filters_card)
        left_filters.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(left_filters, text="A Party (Caller):").grid(row=0, column=0, padx=(0, 8), pady=4, sticky=tk.W)
        self.search_a_party = ttk.Entry(left_filters, width=22)
        self.search_a_party.grid(row=0, column=1, padx=(0, 16), pady=4)
        
        ttk.Label(left_filters, text="B Party (Receiver):").grid(row=0, column=2, padx=(0, 8), pady=4, sticky=tk.W)
        self.search_b_party = ttk.Entry(left_filters, width=22)
        self.search_b_party.grid(row=0, column=3, padx=(0, 0), pady=4)
        
        ttk.Label(left_filters, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=(0, 8), pady=4, sticky=tk.W)
        self.search_date = ttk.Entry(left_filters, width=22)
        self.search_date.grid(row=1, column=1, padx=(0, 16), pady=4)
        
        ttk.Label(left_filters, text="IMEI:").grid(row=1, column=2, padx=(0, 8), pady=4, sticky=tk.W)
        self.search_imei = ttk.Entry(left_filters, width=22)
        self.search_imei.grid(row=1, column=3, padx=(0, 0), pady=4)

        ttk.Label(left_filters, text="Source CSV:").grid(row=2, column=0, padx=(0, 8), pady=4, sticky=tk.W)
        self.search_import_var = tk.StringVar()
        self.search_import_combo = ttk.Combobox(
            left_filters,
            textvariable=self.search_import_var,
            width=22,
            state="readonly",
            values=["All files"],
        )
        self.search_import_combo.grid(row=2, column=1, padx=(0, 16), pady=4, sticky=tk.W)
        self.search_import_combo.set("All files")
        
        actions_frame = ttk.Frame(filters_card)
        actions_frame.grid(row=0, column=1, rowspan=2, sticky=tk.NE)

        ttk.Label(actions_frame, text="Group:").pack(anchor=tk.W, pady=(0, 2))
        self.search_group_var = tk.StringVar(value="All groups")
        self.search_group_combo = ttk.Combobox(
            actions_frame,
            textvariable=self.search_group_var,
            width=18,
            state="readonly",
            values=["All groups"],
        )
        self.search_group_combo.pack(anchor=tk.W, pady=(0, 8))
        self._search_group_ids = {"All groups": None}
        
        ttk.Button(actions_frame, text="Search", style="Accent.TButton", command=self.search_records, width=14).pack(anchor=tk.W, pady=(0, 4))
        ttk.Button(actions_frame, text="Clear", command=self.clear_search, width=10).pack(anchor=tk.W)

        tabs_card = ttk.Frame(frame, style="Card.TFrame", padding=8)
        tabs_card.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(tabs_card, text="Uploaded CDR Files", style="Section.TLabel").pack(anchor=tk.W, padx=6, pady=(0, 6))
        self.upload_tabs_notebook = ttk.Notebook(tabs_card)
        self.upload_tabs_notebook.pack(fill=tk.X)
        self.upload_tabs_notebook.bind("<<NotebookTabChanged>>", lambda event: self._on_upload_tab_change())
        
        table_card = ttk.Frame(frame, style="Card.TFrame", padding=12)
        table_card.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        
        table_frame = ttk.Frame(table_card)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        all_cols = (
            "A_PARTY", "CALL_TYPE", "TOC", "B_PARTY", "LRN_NO", "LRN_TSP_LSA",
            "DATE", "TIME", "DURATION", "FIRST_CGI_LATLONG", "FIRST_CGI",
            "FIRST_TOWER_ADDR",
            "LAST_CGI_LATLONG", "LAST_CGI", "LAST_TOWER_ADDR",
            "SMSC_NO", "SERVICE_TYPE",
            "IMEI", "IMSI", "CALL_FOW_NO", "ROAM_NW", "SW_MSC_ID",
            "IN_TG", "OUT_TG", "VOWIFI_FIRST_UE_IP", "PORT1",
            "VOWIFI_LAST_UE_IP", "PORT2",
        )
        self.search_tree = ttk.Treeview(table_frame, columns=all_cols,
                                        yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.search_tree.yview)
        hsb.config(command=self.search_tree.xview)
        
        self.search_tree.column("#0", width=60, minwidth=60, stretch=False)
        col_headings = {
            "A_PARTY": ("Target No", 110), "CALL_TYPE": ("Call Type", 80),
            "TOC": ("TOC", 50), "B_PARTY": ("B Party No", 120),
            "LRN_NO": ("LRN No", 80), "LRN_TSP_LSA": ("LRN TSP-LSA", 100),
            "DATE": ("Date", 90), "TIME": ("Time", 80),
            "DURATION": ("Dur(s)", 60), "FIRST_CGI_LATLONG": ("First CGI Lat/Long", 150),
            "FIRST_CGI": ("First CGI", 160),
            "FIRST_TOWER_ADDR": ("First Tower Address", 200),
            "LAST_CGI_LATLONG": ("Last CGI Lat/Long", 150),
            "LAST_CGI": ("Last CGI", 160),
            "LAST_TOWER_ADDR": ("Last Tower Address", 200),
            "SMSC_NO": ("SMSC No", 120),
            "SERVICE_TYPE": ("Service Type", 90), "IMEI": ("IMEI", 150),
            "IMSI": ("IMSI", 140), "CALL_FOW_NO": ("Call Fow No", 100),
            "ROAM_NW": ("Roam Nw", 80), "SW_MSC_ID": ("SW & MSC ID", 120),
            "IN_TG": ("IN TG", 60), "OUT_TG": ("OUT TG", 60),
            "VOWIFI_FIRST_UE_IP": ("VoWiFi First UE IP", 140), "PORT1": ("Port1", 60),
            "VOWIFI_LAST_UE_IP": ("VoWiFi Last UE IP", 140), "PORT2": ("Port2", 60),
        }
        for col_id in all_cols:
            heading, width = col_headings[col_id]
            self.search_tree.column(col_id, width=width, minwidth=width, stretch=False)
            self.search_tree.heading(col_id, text=heading, anchor=tk.W)
        self.search_tree.heading("#0", text="ID", anchor=tk.W)
        
        self.search_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.search_tree.bind("<MouseWheel>", lambda event: self._on_tree_mousewheel(self.search_tree, event))
        self.search_tree.bind("<Button-4>", lambda event: self._on_tree_mousewheel(self.search_tree, event))
        self.search_tree.bind("<Button-5>", lambda event: self._on_tree_mousewheel(self.search_tree, event))
    
    def create_groups_tab(self):
        frame = ttk.Frame(self.groups_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(1, weight=1)

        # Header
        header = ttk.Frame(frame, style="TFrame")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        ttk.Label(header, text="CDR File Groups", font=("Helvetica", 15, "bold")).pack(side=tk.LEFT)

        # ── Left Panel: Group List ──
        left_panel = ttk.Frame(frame, style="Card.TFrame", padding=12, width=260)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0, 10))
        left_panel.grid_propagate(False)
        left_panel.columnconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)

        ttk.Label(left_panel, text="Groups", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))

        self.group_listbox = tk.Listbox(
            left_panel, background="#0b1220", foreground="#e2e8f0",
            selectbackground="#3b82f6", selectforeground="#ffffff",
            highlightthickness=0, borderwidth=0, font=("Helvetica", 11),
        )
        self.group_listbox.grid(row=1, column=0, sticky="nsew")
        self.group_listbox.bind("<<ListboxSelect>>", lambda e: self._on_group_select())

        grp_btn_frame = ttk.Frame(left_panel)
        grp_btn_frame.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(grp_btn_frame, text="+ New Group", style="Accent.TButton",
                   command=self._create_group, width=12).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(grp_btn_frame, text="Rename", command=self._rename_group, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(grp_btn_frame, text="Delete", command=self._delete_group, width=8).pack(side=tk.LEFT)

        # ── Right Panel: Group Details ──
        right_panel = ttk.Frame(frame, style="Card.TFrame", padding=12)
        right_panel.grid(row=1, column=1, sticky="nsew")
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(2, weight=1)

        self.group_detail_label = ttk.Label(right_panel, text="Select a group", style="Section.TLabel")
        self.group_detail_label.grid(row=0, column=0, sticky="w", pady=(0, 4))

        self.group_stats_label = ttk.Label(right_panel, text="", style="Muted.TLabel")
        self.group_stats_label.grid(row=1, column=0, sticky="w", pady=(0, 8))

        # Files Treeview
        files_frame = ttk.Frame(right_panel)
        files_frame.grid(row=2, column=0, sticky="nsew")
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(0, weight=1)

        self.group_files_tree = ttk.Treeview(
            files_frame, columns=("FILE", "RECORDS", "DATE"),
            height=12,
        )
        self.group_files_tree.heading("#0", text="#", anchor=tk.W)
        self.group_files_tree.column("#0", width=40, minwidth=40, stretch=False)
        self.group_files_tree.heading("FILE", text="CDR File", anchor=tk.W)
        self.group_files_tree.column("FILE", width=300, minwidth=200)
        self.group_files_tree.heading("RECORDS", text="Records", anchor=tk.W)
        self.group_files_tree.column("RECORDS", width=80, minwidth=60)
        self.group_files_tree.heading("DATE", text="Imported", anchor=tk.W)
        self.group_files_tree.column("DATE", width=150, minwidth=120)

        vsb = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.group_files_tree.yview)
        self.group_files_tree.configure(yscrollcommand=vsb.set)
        self.group_files_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # Action buttons
        action_frame = ttk.Frame(right_panel)
        action_frame.grid(row=3, column=0, sticky="ew", pady=(8, 0))
        ttk.Button(action_frame, text="Add CDR Files", style="Accent.TButton",
                   command=self._add_files_to_group, width=14).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="Remove Selected",
                   command=self._remove_file_from_group, width=14).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(action_frame, text="View Group CDRs",
                   command=self._view_group_cdrs, width=14).pack(side=tk.RIGHT)

        self._group_ids = []
        self._refresh_group_list()
    
    def create_analytics_tab(self):
        frame = ttk.Frame(self.analytics_frame, padding=12)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)

        header = ttk.Frame(frame, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="Advanced Analytics", font=("Helvetica", 15, "bold")).grid(row=0, column=0, sticky="w")

        filter_row = ttk.Frame(frame, style="TFrame")
        filter_row.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(filter_row, text="Target Number:").pack(side=tk.LEFT, padx=(0, 6))
        self.analytics_target_var = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.analytics_target_var, width=18).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(filter_row, text="Date From:").pack(side=tk.LEFT, padx=(0, 6))
        self.analytics_date_from = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.analytics_date_from, width=12).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(filter_row, text="Date To:").pack(side=tk.LEFT, padx=(0, 6))
        self.analytics_date_to = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.analytics_date_to, width=12).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(filter_row, text="Refresh", style="Accent.TButton", command=self.refresh_analytics_dashboard, width=12).pack(side=tk.RIGHT)

        body = ttk.Frame(frame, style="TFrame")
        body.grid(row=2, column=0, sticky="nsew")
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left_panel = ttk.Frame(body, style="TFrame")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        left_panel.rowconfigure(0, weight=1)
        left_panel.rowconfigure(1, weight=1)
        left_panel.columnconfigure(0, weight=1)

        self.analytics_notebook = ttk.Notebook(left_panel)
        self.analytics_notebook.grid(row=0, column=0, sticky="nsew")

        self.analytics_tabs = {}
        for tab_name in [
            "Call Volume Trend",
            "Hourly Activity Heatmap",
            "IMEI Switching Timeline",
            "Top Contacts",
            "Duration Buckets",
        ]:
            tab = ttk.Frame(self.analytics_notebook, padding=8)
            self.analytics_notebook.add(tab, text=tab_name)
            canvas = tk.Canvas(tab, height=260, background="#0b1220", highlightthickness=0)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.analytics_tabs[tab_name] = canvas

        self.analytics_chart_canvas = self.analytics_tabs["Call Volume Trend"]

        self.analytics_notebook.bind("<<NotebookTabChanged>>", lambda event: self.refresh_analytics_dashboard())

        summary_card = ttk.Frame(left_panel, style="Card.TFrame", padding=10)
        summary_card.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        ttk.Label(summary_card, text="Investigation Notes", style="Section.TLabel").pack(anchor=tk.W, pady=(0, 6))
        self.analytics_text = scrolledtext.ScrolledText(summary_card, height=8, wrap=tk.WORD, background="#0b1220", foreground="#e2e8f0", insertbackground="#e2e8f0")
        self.analytics_text.pack(fill=tk.BOTH, expand=True)
        self.analytics_text.insert(1.0, "• Risk patterns and anomalies will appear here after refresh.\n")
        self.analytics_text.config(state=tk.DISABLED)

        right_panel = ttk.Frame(body, style="Card.TFrame", padding=12)
        right_panel.grid(row=0, column=1, sticky="nsew")
        right_panel.rowconfigure(6, weight=1)
        ttk.Label(right_panel, text="AI Intelligence Summary", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 10))
        self.ai_risk_label = ttk.Label(right_panel, text="Risk Score: 0", font=("Helvetica", 14, "bold"))
        self.ai_risk_label.grid(row=1, column=0, sticky="w", pady=(0, 6))
        self.ai_behavior_label = ttk.Label(right_panel, text="Behavior: Undetermined", style="Muted.TLabel")
        self.ai_behavior_label.grid(row=2, column=0, sticky="w", pady=(0, 6))
        self.ai_summary_text = scrolledtext.ScrolledText(right_panel, height=12, wrap=tk.WORD, background="#0b1220", foreground="#e2e8f0", insertbackground="#e2e8f0")
        self.ai_summary_text.grid(row=3, column=0, sticky="nsew", pady=(0, 8))
        ttk.Button(right_panel, text="Explain Insight", width=16).grid(row=4, column=0, sticky="w", pady=(0, 6))
        ttk.Button(right_panel, text="Mark as Evidence", width=18).grid(row=5, column=0, sticky="w")

        self.refresh_analytics_dashboard()
    
    def create_database_tab(self):
        frame = ttk.Frame(self.database_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # ── CDR Controls Row ──
        control_card = ttk.Frame(frame, style="Card.TFrame", padding=12)
        control_card.pack(fill=tk.X, pady=(0, 8))
        
        left_controls = ttk.Frame(control_card)
        left_controls.pack(side=tk.LEFT, padx=(0, 8))
        
        ttk.Button(left_controls, text="Upload CSV", style="Accent.TButton", command=self.upload_csv, width=14).pack(side=tk.LEFT, padx=(0, 8), pady=4)
        ttk.Button(left_controls, text="View All", command=self.view_all_records, width=12).pack(side=tk.LEFT, padx=(0, 8), pady=4)
        
        right_controls = ttk.Frame(control_card)
        right_controls.pack(side=tk.RIGHT)

        ttk.Label(right_controls, text="Source CSV:").pack(side=tk.LEFT, padx=(0, 4), pady=4)
        self.db_import_var = tk.StringVar()
        self.db_import_combo = ttk.Combobox(
            right_controls,
            textvariable=self.db_import_var,
            width=20,
            state="readonly",
            values=["All files"],
        )
        self.db_import_combo.pack(side=tk.LEFT, padx=(0, 8), pady=4)
        self.db_import_combo.set("All files")
        
        ttk.Button(right_controls, text="Export CSV", command=self.export_to_csv, width=12).pack(side=tk.LEFT, padx=(0, 8), pady=4)
        ttk.Button(right_controls, text="Clear Database", command=self.clear_database, width=14).pack(side=tk.LEFT, pady=4)

        # ── Cell Tower Database Row ──
        ct_card = ttk.Frame(frame, style="Card.TFrame", padding=10)
        ct_card.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(ct_card, text="Cell Tower Database", style="Section.TLabel").pack(side=tk.LEFT)
        self.cell_tower_status_label = ttk.Label(ct_card, text="No towers loaded")
        self.cell_tower_status_label.pack(side=tk.LEFT, padx=(16, 0))

        ct_buttons = ttk.Frame(ct_card)
        ct_buttons.pack(side=tk.RIGHT)
        ttk.Button(ct_buttons, text="Upload Tower CSV", style="Accent.TButton",
                   command=self.upload_cell_tower_csv, width=16).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(ct_buttons, text="Clear Towers",
                   command=self.clear_cell_towers, width=12).pack(side=tk.LEFT)

        self._refresh_cell_tower_status()
        
        # ── Records Treeview ──
        records_card = ttk.Frame(frame, style="Card.TFrame", padding=12)
        records_card.pack(fill=tk.BOTH, expand=True)
        
        table_frame = ttk.Frame(records_card)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        hsb = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        db_cols = (
            "A_PARTY", "CALL_TYPE", "TOC", "B_PARTY", "LRN_NO", "LRN_TSP_LSA",
            "DATE", "TIME", "DURATION", "FIRST_CGI_LATLONG", "FIRST_CGI",
            "FIRST_TOWER_ADDR",
            "LAST_CGI_LATLONG", "LAST_CGI", "LAST_TOWER_ADDR",
            "SMSC_NO", "SERVICE_TYPE",
            "IMEI", "IMSI", "CALL_FOW_NO", "ROAM_NW", "SW_MSC_ID",
            "IN_TG", "OUT_TG", "VOWIFI_FIRST_UE_IP", "PORT1",
            "VOWIFI_LAST_UE_IP", "PORT2",
        )
        self.db_tree = ttk.Treeview(table_frame, columns=db_cols,
                                    yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.config(command=self.db_tree.yview)
        hsb.config(command=self.db_tree.xview)
        
        self.db_tree.column("#0", width=60, minwidth=60, stretch=False)
        db_col_headings = {
            "A_PARTY": ("Target No", 110), "CALL_TYPE": ("Call Type", 80),
            "TOC": ("TOC", 50), "B_PARTY": ("B Party No", 120),
            "LRN_NO": ("LRN No", 80), "LRN_TSP_LSA": ("LRN TSP-LSA", 100),
            "DATE": ("Date", 90), "TIME": ("Time", 80),
            "DURATION": ("Dur(s)", 60), "FIRST_CGI_LATLONG": ("First CGI Lat/Long", 150),
            "FIRST_CGI": ("First CGI", 160),
            "FIRST_TOWER_ADDR": ("First Tower Address", 200),
            "LAST_CGI_LATLONG": ("Last CGI Lat/Long", 150),
            "LAST_CGI": ("Last CGI", 160),
            "LAST_TOWER_ADDR": ("Last Tower Address", 200),
            "SMSC_NO": ("SMSC No", 120),
            "SERVICE_TYPE": ("Service Type", 90), "IMEI": ("IMEI", 150),
            "IMSI": ("IMSI", 140), "CALL_FOW_NO": ("Call Fow No", 100),
            "ROAM_NW": ("Roam Nw", 80), "SW_MSC_ID": ("SW & MSC ID", 120),
            "IN_TG": ("IN TG", 60), "OUT_TG": ("OUT TG", 60),
            "VOWIFI_FIRST_UE_IP": ("VoWiFi First UE IP", 140), "PORT1": ("Port1", 60),
            "VOWIFI_LAST_UE_IP": ("VoWiFi Last UE IP", 140), "PORT2": ("Port2", 60),
        }
        for col_id in db_cols:
            heading, width = db_col_headings[col_id]
            self.db_tree.column(col_id, width=width, minwidth=width, stretch=False)
            self.db_tree.heading(col_id, text=heading, anchor=tk.W)
        self.db_tree.heading("#0", text="ID", anchor=tk.W)
        
        self.db_tree.grid(row=0, column=0, sticky=tk.NSEW)
        vsb.grid(row=0, column=1, sticky=tk.NS)
        hsb.grid(row=1, column=0, sticky=tk.EW)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)
        self.db_tree.bind("<MouseWheel>", lambda event: self._on_tree_mousewheel(self.db_tree, event))
        self.db_tree.bind("<Button-4>", lambda event: self._on_tree_mousewheel(self.db_tree, event))
        self.db_tree.bind("<Button-5>", lambda event: self._on_tree_mousewheel(self.db_tree, event))

    def create_network_tab(self):
        frame = ttk.Frame(self.network_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        header = ttk.Frame(frame, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text="Network Analysis", font=("Helvetica", 15, "bold"))
        title.grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(header, style="Card.TFrame", padding=10)
        controls.grid(row=0, column=1, sticky="e")
        ttk.Label(controls, text="Target").pack(side=tk.LEFT, padx=(0, 6))
        self.network_target_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.network_target_var, width=18).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(controls, text="Date From").pack(side=tk.LEFT, padx=(0, 6))
        self.network_date_from = tk.StringVar()
        ttk.Entry(controls, textvariable=self.network_date_from, width=12).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(controls, text="Date To").pack(side=tk.LEFT, padx=(0, 6))
        self.network_date_to = tk.StringVar()
        ttk.Entry(controls, textvariable=self.network_date_to, width=12).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(controls, text="Min Frequency").pack(side=tk.LEFT, padx=(0, 6))
        self.network_min_freq = tk.StringVar(value="3")
        ttk.Entry(controls, textvariable=self.network_min_freq, width=6).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Label(controls, text="Min Duration").pack(side=tk.LEFT, padx=(0, 6))
        self.network_min_duration = tk.StringVar(value="60")
        ttk.Entry(controls, textvariable=self.network_min_duration, width=6).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls, text="Reset View", width=12, command=self.reset_network_view).pack(side=tk.RIGHT, padx=(0, 6))
        ttk.Button(controls, text="Refresh", style="Accent.TButton", width=12, command=self.refresh_network_graph).pack(side=tk.RIGHT, padx=(0, 8))

        graph_card = ttk.Frame(frame, style="Card.TFrame", padding=10)
        graph_card.grid(row=1, column=0, sticky="nsew")
        graph_card.rowconfigure(0, weight=1)
        graph_card.columnconfigure(0, weight=1)
        self.network_canvas = tk.Canvas(graph_card, background="#0b1220", highlightthickness=0)
        self.network_canvas.grid(row=0, column=0, sticky="nsew")
        self.network_canvas.bind("<ButtonPress-1>", self._on_network_press)
        self.network_canvas.bind("<B1-Motion>", self._on_network_drag)
        self.network_canvas.bind("<MouseWheel>", self._on_network_zoom)
        self.network_canvas.bind("<Button-4>", self._on_network_zoom)
        self.network_canvas.bind("<Button-5>", self._on_network_zoom)
        self.network_view = {"scale": 1.0, "offset_x": 0, "offset_y": 0}
        self.network_data = {"target": "", "edges": []}
        self.refresh_network_graph()

    def create_location_tab(self):
        frame = ttk.Frame(self.location_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        header = ttk.Frame(frame, style="TFrame")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text="Location Intelligence", font=("Helvetica", 15, "bold"))
        title.grid(row=0, column=0, sticky="w")

        controls = ttk.Frame(header, style="Card.TFrame", padding=10)
        controls.grid(row=0, column=1, sticky="e")
        ttk.Label(controls, text="Target").pack(side=tk.LEFT, padx=(0, 6))
        self.location_target_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.location_target_var, width=18).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(controls, text="Date From").pack(side=tk.LEFT, padx=(0, 6))
        self.location_date_from = tk.StringVar()
        ttk.Entry(controls, textvariable=self.location_date_from, width=12).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Label(controls, text="Date To").pack(side=tk.LEFT, padx=(0, 6))
        self.location_date_to = tk.StringVar()
        ttk.Entry(controls, textvariable=self.location_date_to, width=12).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(controls, text="Refresh", style="Accent.TButton", width=12, command=self.refresh_location_analysis).pack(side=tk.RIGHT)

        body = ttk.Frame(frame, style="TFrame")
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        map_card = ttk.Frame(body, style="Card.TFrame", padding=10)
        map_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        map_card.rowconfigure(0, weight=1)
        map_card.columnconfigure(0, weight=1)
        self.location_canvas = tk.Canvas(map_card, background="#0b1220", highlightthickness=0)
        self.location_canvas.grid(row=0, column=0, sticky="nsew")

        side_card = ttk.Frame(body, style="Card.TFrame", padding=10)
        side_card.grid(row=0, column=1, sticky="nsew")
        side_card.rowconfigure(1, weight=1)
        ttk.Label(side_card, text="Tower Frequency", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.location_tree = ttk.Treeview(side_card, columns=("LAT", "LON", "COUNT"), height=8)
        self.location_tree.heading("#0", text="Rank", anchor=tk.W)
        self.location_tree.heading("LAT", text="Lat", anchor=tk.W)
        self.location_tree.heading("LON", text="Lon", anchor=tk.W)
        self.location_tree.heading("COUNT", text="Count", anchor=tk.W)
        self.location_tree.column("#0", width=40, minwidth=40)
        self.location_tree.column("LAT", width=90, minwidth=90)
        self.location_tree.column("LON", width=90, minwidth=90)
        self.location_tree.column("COUNT", width=60, minwidth=60)
        self.location_tree.grid(row=1, column=0, sticky="nsew")
        self.location_summary = scrolledtext.ScrolledText(side_card, height=6, wrap=tk.WORD, background="#0b1220", foreground="#e2e8f0", insertbackground="#e2e8f0")
        self.location_summary.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        self.location_summary.insert(1.0, "• Location summary will appear here after refresh.\n")
        self.location_summary.config(state=tk.DISABLED)
        self.refresh_location_analysis()

    def create_reports_tab(self):
        frame = ttk.Frame(self.reports_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)

        title = ttk.Label(frame, text="Report Builder", font=("Helvetica", 15, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        builder = ttk.Frame(frame, style="Card.TFrame", padding=12)
        builder.grid(row=1, column=0, sticky="ew")
        ttk.Label(builder, text="Include Sections", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 8))
        self.report_include_charts = tk.BooleanVar(value=True)
        self.report_include_ai = tk.BooleanVar(value=True)
        self.report_include_network = tk.BooleanVar(value=True)
        self.report_include_timeline = tk.BooleanVar(value=True)
        self.report_include_contacts = tk.BooleanVar(value=True)
        ttk.Checkbutton(builder, text="Charts", variable=self.report_include_charts).grid(row=1, column=0, sticky="w")
        ttk.Checkbutton(builder, text="AI Summary", variable=self.report_include_ai).grid(row=2, column=0, sticky="w")
        ttk.Checkbutton(builder, text="Network Graph", variable=self.report_include_network).grid(row=3, column=0, sticky="w")
        ttk.Checkbutton(builder, text="Timeline", variable=self.report_include_timeline).grid(row=4, column=0, sticky="w")
        ttk.Checkbutton(builder, text="Contact Table", variable=self.report_include_contacts).grid(row=5, column=0, sticky="w")
        ttk.Button(builder, text="Preview Report", width=16).grid(row=6, column=0, pady=(8, 0), sticky="w")
        ttk.Button(builder, text="Export PDF", width=16).grid(row=6, column=1, padx=(8, 0), pady=(8, 0), sticky="w")
        ttk.Button(builder, text="Export DOCX", width=16).grid(row=6, column=2, padx=(8, 0), pady=(8, 0), sticky="w")
        ttk.Button(builder, text="Export JSON", width=16).grid(row=6, column=3, padx=(8, 0), pady=(8, 0), sticky="w")

    def create_settings_tab(self):
        frame = ttk.Frame(self.settings_frame, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)

        title = ttk.Label(frame, text="System Settings", font=("Helvetica", 15, "bold"))
        title.grid(row=0, column=0, sticky="w", pady=(0, 10))

        settings_card = ttk.Frame(frame, style="Card.TFrame", padding=12)
        settings_card.grid(row=1, column=0, sticky="ew")
        ttk.Label(settings_card, text="User Management", style="Section.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ttk.Button(settings_card, text="Add User", width=14).grid(row=1, column=0, sticky="w", pady=2)
        ttk.Button(settings_card, text="Roles & Permissions", width=18).grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(settings_card, text="Session Management", style="Section.TLabel").grid(row=3, column=0, sticky="w", pady=(10, 6))
        ttk.Button(settings_card, text="View Active Sessions", width=20).grid(row=4, column=0, sticky="w", pady=2)
        ttk.Label(settings_card, text="Appearance", style="Section.TLabel").grid(row=5, column=0, sticky="w", pady=(10, 6))
        ttk.Button(settings_card, text="Toggle Dark/Light", width=18).grid(row=6, column=0, sticky="w", pady=2)
    
    def upload_csv(self):
        file_paths = filedialog.askopenfilenames(
            title="Select CSV Files",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_paths:
            return
        
        # Create progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Uploading Files")
        progress_window.geometry("400x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        progress_label = ttk.Label(progress_window, text="Preparing upload...")
        progress_label.pack(pady=10)
        
        progress_bar = ttk.Progressbar(progress_window, orient=tk.HORIZONTAL, length=300, mode='determinate')
        progress_bar.pack(pady=10)
        
        file_progress_label = ttk.Label(progress_window, text="")
        file_progress_label.pack(pady=5)
        
        self.root.update()
        
        total_count = 0
        processed_files = 0
        errors = []
        
        try:
            total_files = len(file_paths)
            
            for i, file_path in enumerate(file_paths):
                file_name = os.path.basename(file_path)
                progress_label.config(text=f"Processing file {i+1}/{total_files}: {file_name}")
                progress_bar['value'] = 0
                self.root.update()
                
                def update_progress(percent, count):
                    progress_bar['value'] = percent
                    file_progress_label.config(text=f"Imported {count} records...")
                    progress_window.update()
                
                success, msg, count = self.csv_importer.import_csv(file_path, progress_callback=update_progress)
                
                if success:
                    total_count += count
                    processed_files += 1
                else:
                    errors.append(f"{file_name}: {msg}")
            
            progress_window.destroy()
            
            result_msg = f"Uploaded {total_count} records from {processed_files} files successfully!"
            if errors:
                result_msg += "\n\nErrors:\n" + "\n".join(errors)
                messagebox.showwarning("Upload Completed with Errors", result_msg)
            else:
                messagebox.showinfo("Success", result_msg)
                
            self.view_all_records()
            self.refresh_import_sources()
            self._refresh_after_upload()
        
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"Error uploading file: {str(e)}")
    
    def _map_row_to_values(self, row, tower_map=None):
        """Map a full CDR database row to treeview display values.
        
        SQL column order:
        0:id, 1:target_no, 2:call_type, 3:toc, 4:b_party_no, 5:lrn_no,
        6:lrn_tsp_lsa, 7:datetime, 8:duration_seconds, 9:first_cgi_lat,
        10:first_cgi_long, 11:first_cgi, 12:last_cgi_lat, 13:last_cgi_long,
        14:last_cgi, 15:smsc_no, 16:service_type, 17:imei, 18:imsi,
        19:call_fow_no, 20:roam_nw, 21:sw_msc_id, 22:in_tg, 23:out_tg,
        24:vowifi_first_ue_ip, 25:port1, 26:vowifi_last_ue_ip, 27:port2
        """
        if tower_map is None:
            tower_map = {}
        c = self._clean_value
        dt_value = c(row[7])
        date_str = dt_value[:10] if dt_value else ""
        time_str = dt_value[11:19] if dt_value else ""
        
        first_latlong = ""
        if row[9] is not None and row[10] is not None:
            first_latlong = f"{row[9]}/{row[10]}"
        last_latlong = ""
        if row[12] is not None and row[13] is not None:
            last_latlong = f"{row[12]}/{row[13]}"

        # Tower address lookup
        first_cgi_val = c(row[11])
        last_cgi_val = c(row[14])
        first_tower_info = tower_map.get(first_cgi_val, {}) if first_cgi_val else {}
        last_tower_info = tower_map.get(last_cgi_val, {}) if last_cgi_val else {}
        first_tower_addr = first_tower_info.get("address", "") or ""
        last_tower_addr = last_tower_info.get("address", "") or ""
        
        return (
            c(row[1]),           # Target No (A_PARTY)
            c(row[2]),           # Call Type
            c(row[3]),           # TOC
            c(row[4]),           # B Party No
            c(row[5]),           # LRN No
            c(row[6]),           # LRN TSP-LSA
            date_str,            # Date
            time_str,            # Time
            c(row[8]),           # Duration
            first_latlong,       # First CGI Lat/Long
            c(row[11]),          # First CGI
            first_tower_addr,    # First Tower Address
            last_latlong,        # Last CGI Lat/Long
            c(row[14]),          # Last CGI
            last_tower_addr,     # Last Tower Address
            c(row[15]),          # SMSC No
            c(row[16]),          # Service Type
            c(row[17]),          # IMEI
            c(row[18]),          # IMSI
            c(row[19]),          # Call Fow No
            c(row[20]),          # Roam Nw
            c(row[21]),          # SW & MSC ID
            c(row[22]),          # IN TG
            c(row[23]),          # OUT TG
            c(row[24]),          # VoWiFi First UE IP
            c(row[25]),          # Port1
            c(row[26]),          # VoWiFi Last UE IP
            c(row[27]),          # Port2
        )

    def search_records(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, target_no, call_type, toc, b_party_no, lrn_no, lrn_tsp_lsa, datetime, duration_seconds, first_cgi_lat, first_cgi_long, first_cgi, last_cgi_lat, last_cgi_long, last_cgi, smsc_no, service_type, imei, imsi, call_fow_no, roam_nw, sw_msc_id, in_tg, out_tg, vowifi_first_ue_ip, port1, vowifi_last_ue_ip, port2 FROM cdrs WHERE 1=1"
            params = []
            
            a_party = self.search_a_party.get().strip()
            b_party = self.search_b_party.get().strip()
            date_val = self.search_date.get().strip()
            imei_val = self.search_imei.get().strip()
            import_label = self.search_import_var.get().strip() if hasattr(self, "search_import_var") else ""
            
            if a_party:
                query += " AND target_no LIKE ?"
                params.append(f"%{a_party}%")
            if b_party:
                query += " AND b_party_no LIKE ?"
                params.append(f"%{b_party}%")
            if date_val:
                query += " AND DATE(datetime) = ?"
                params.append(date_val)
            if imei_val:
                query += " AND imei LIKE ?"
                params.append(f"%{imei_val}%")

            if import_label and import_label != "All files":
                batch_id = None
                if hasattr(self, "import_batches"):
                    batch_id = self.import_batches.get(import_label)
                if batch_id is not None:
                    query += " AND import_batch_id = ?"
                    params.append(int(batch_id))

            # Group filter
            group_label = self.search_group_var.get().strip() if hasattr(self, "search_group_var") else ""
            if group_label and group_label != "All groups" and hasattr(self, "_search_group_ids"):
                group_id = self._search_group_ids.get(group_label)
                if group_id is not None:
                    batch_ids = self.db_manager.get_group_batch_ids(group_id)
                    if batch_ids:
                        placeholders = ",".join("?" * len(batch_ids))
                        query += f" AND import_batch_id IN ({placeholders})"
                        params.extend(batch_ids)
                    else:
                        query += " AND 1=0"  # no batches in group → no results
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            for item in self.search_tree.get_children():
                self.search_tree.delete(item)

            # Batch CGI lookup for tower matching
            tower_map = {}
            cgi_set = set()
            for row in results:
                f_cgi = self._clean_value(row[11])
                l_cgi = self._clean_value(row[14])
                if f_cgi: cgi_set.add(f_cgi)
                if l_cgi: cgi_set.add(l_cgi)
            if cgi_set:
                tower_map = self.db_manager.lookup_towers_by_cgis(list(cgi_set))

            for row in results:
                values = self._map_row_to_values(row, tower_map)
                self.search_tree.insert("", tk.END, text=str(row[0]), values=values)
            
            messagebox.showinfo("Search", f"Found {len(results)} records")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Search error: {str(e)}")
    
    def clear_search(self):
        self.search_a_party.delete(0, tk.END)
        self.search_b_party.delete(0, tk.END)
        self.search_date.delete(0, tk.END)
        self.search_imei.delete(0, tk.END)
        if hasattr(self, "search_group_combo"):
            self.search_group_combo.set("All groups")
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
        if hasattr(self, "analytics_chart_canvas"):
            self.analytics_chart_canvas.delete("all")
        self.analytics_text.config(state=tk.NORMAL)
        self.analytics_text.delete(1.0, tk.END)
        filter_sql, params = self._analytics_filter_sql(include_target=True)
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if analytics_type == "max_duration":
                cursor.execute(
                    f"SELECT target_no, b_party_no, duration_seconds FROM cdrs WHERE duration_seconds IS NOT NULL {filter_sql} ORDER BY duration_seconds DESC LIMIT 10",
                    params,
                )
                results = cursor.fetchall()
                text = "Top 10 Max Call Duration Records:\n\n"
                for row in results:
                    text += f"A Party: {row[0]}\nB Party: {row[1]}\nDuration: {row[2]} seconds\n\n"
                self.analytics_text.insert(1.0, text)
                
                data = [(str(row[0]) or "Unknown", int(row[2] or 0)) for row in results]
                if data:
                    self._draw_bar_chart(data, "Top Call Durations (seconds)")
            
            elif analytics_type == "max_imei":
                cursor.execute(
                    f"SELECT imei, COUNT(*) FROM cdrs WHERE imei IS NOT NULL {filter_sql} GROUP BY imei ORDER BY COUNT(*) DESC LIMIT 10",
                    params,
                )
                results = cursor.fetchall()
                text = "Top 10 Most Used IMEI:\n\n"
                for row in results:
                    text += f"IMEI: {row[0]}\nUsage Count: {row[1]}\n\n"
                self.analytics_text.insert(1.0, text)
                
                data = [(str(row[0]) or "Unknown", int(row[1] or 0)) for row in results]
                if data:
                    self._draw_bar_chart(data, "Top IMEI Usage")
            
            elif analytics_type == "total_records":
                cursor.execute(f"SELECT COUNT(*) FROM cdrs WHERE 1=1 {filter_sql}", params)
                count = cursor.fetchone()[0]
                cursor.execute(f"SELECT COUNT(DISTINCT target_no) FROM cdrs WHERE target_no IS NOT NULL {filter_sql}", params)
                unique_a_party = cursor.fetchone()[0]
                cursor.execute(f"SELECT COUNT(DISTINCT b_party_no) FROM cdrs WHERE b_party_no IS NOT NULL {filter_sql}", params)
                unique_b_party = cursor.fetchone()[0]
                
                text = f"Database Statistics:\n\n"
                text += f"Total Records: {count}\n"
                text += f"Unique A Party Numbers: {unique_a_party}\n"
                text += f"Unique B Party Numbers: {unique_b_party}\n"
                self.analytics_text.insert(1.0, text)
                
                data = [
                    ("A Party", unique_a_party),
                    ("B Party", unique_b_party),
                ]
                self._draw_bar_chart(data, "Unique Numbers by Role")
            
            elif analytics_type == "call_stats":
                cursor.execute(
                    f"SELECT call_type, COUNT(*) FROM cdrs WHERE call_type IS NOT NULL {filter_sql} GROUP BY call_type",
                    params,
                )
                results = cursor.fetchall()
                text = "Call Type Statistics:\n\n"
                for row in results:
                    text += f"Call Type: {row[0]}\nCount: {row[1]}\n\n"
                self.analytics_text.insert(1.0, text)
                
                data = [(str(row[0]) or "Unknown", int(row[1])) for row in results]
                if data:
                    if len(data) <= 8:
                        self._draw_pie_chart(data, "Call Type Distribution")
                    else:
                        self._draw_bar_chart(data, "Call Type Distribution")
            
            elif analytics_type == "hourly_activity":
                cursor.execute(
                    f"""
                    SELECT CAST(strftime('%H', datetime) AS INTEGER) AS hour, COUNT(*)
                    FROM cdrs
                    WHERE datetime IS NOT NULL
                    {filter_sql}
                    GROUP BY hour
                    ORDER BY hour ASC
                    """,
                    params,
                )
                results = cursor.fetchall()
                text = "Hourly Call Activity:\n\n"
                for row in results:
                    text += f"Hour {row[0]:02d}: {row[1]} calls\n"
                self.analytics_text.insert(1.0, text)
                
                hour_map = {int(row[0]): int(row[1]) for row in results}
                data = [(f"{h:02d}", hour_map.get(h, 0)) for h in range(24)]
                self._draw_line_chart(data, "Hourly Call Activity")
            
            elif analytics_type == "duration_buckets":
                cursor.execute(
                    f"""
                    SELECT
                        CASE
                            WHEN duration_seconds < 30 THEN '<30s'
                            WHEN duration_seconds < 60 THEN '30-59s'
                            WHEN duration_seconds < 120 THEN '1-2m'
                            WHEN duration_seconds < 300 THEN '2-5m'
                            WHEN duration_seconds < 600 THEN '5-10m'
                            WHEN duration_seconds < 1800 THEN '10-30m'
                            ELSE '30m+'
                        END AS bucket,
                        COUNT(*)
                    FROM cdrs
                    WHERE duration_seconds IS NOT NULL
                    {filter_sql}
                    GROUP BY bucket
                    """,
                    params,
                )
                results = cursor.fetchall()
                text = "Call Duration Buckets:\n\n"
                for row in results:
                    text += f"{row[0]}: {row[1]} calls\n"
                self.analytics_text.insert(1.0, text)
                
                bucket_order = ["<30s", "30-59s", "1-2m", "2-5m", "5-10m", "10-30m", "30m+"]
                bucket_map = {row[0]: int(row[1]) for row in results}
                data = [(label, bucket_map.get(label, 0)) for label in bucket_order]
                self._draw_bar_chart(data, "Duration Distribution")
            
            elif analytics_type == "top_b_party":
                cursor.execute(
                    f"""
                    SELECT b_party_no, COUNT(*)
                    FROM cdrs
                    WHERE b_party_no IS NOT NULL
                    {filter_sql}
                    GROUP BY b_party_no
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                    """,
                    params,
                )
                results = cursor.fetchall()
                text = "Top 10 B Party Numbers:\n\n"
                for row in results:
                    text += f"B Party: {row[0]}\nCount: {row[1]}\n\n"
                self.analytics_text.insert(1.0, text)
                
                data = [(str(row[0]) or "Unknown", int(row[1] or 0)) for row in results]
                if data:
                    self._draw_bar_chart(data, "Top B Party Numbers")
            
            elif analytics_type == "ai_insights":
                cursor.execute(
                    f"""
                    SELECT target_no,
                           COUNT(*) AS total_calls,
                           SUM(
                               CASE
                                   WHEN CAST(strftime('%H', datetime) AS INTEGER) >= 22
                                        OR CAST(strftime('%H', datetime) AS INTEGER) < 6
                                   THEN 1
                                   ELSE 0
                               END
                           ) AS night_calls
                    FROM cdrs
                    WHERE target_no IS NOT NULL {filter_sql}
                    GROUP BY target_no
                    HAVING total_calls >= 10 AND night_calls >= 3
                    ORDER BY night_calls DESC
                    LIMIT 10
                    """,
                    params,
                )
                night_results = cursor.fetchall()
                
                cursor.execute(
                    f"""
                    SELECT imei,
                           COUNT(DISTINCT target_no) AS numbers,
                           COUNT(*) AS total_calls
                    FROM cdrs
                    WHERE imei IS NOT NULL AND TRIM(imei) != ''
                    {filter_sql}
                    GROUP BY imei
                    HAVING numbers >= 2
                    ORDER BY numbers DESC, total_calls DESC
                    LIMIT 10
                    """,
                    params,
                )
                imei_results = cursor.fetchall()
                
                text_lines = []
                text_lines.append("AI-style Insights (rule-based):\n")
                
                if night_results:
                    text_lines.append("Numbers with high night-call activity:\n")
                    for row in night_results:
                        number = row[0]
                        total_calls = row[1]
                        night_calls = row[2]
                        text_lines.append(f"- {number}: {night_calls} night calls out of {total_calls} total calls")
                    text_lines.append("")
                else:
                    text_lines.append("No strong night-call patterns detected.\n")
                
                if imei_results:
                    text_lines.append("IMEI used by multiple numbers (possible shared devices or SIM swaps):\n")
                    for row in imei_results:
                        imei = row[0]
                        numbers = row[1]
                        total_calls = row[2]
                        text_lines.append(f"- IMEI {imei}: {numbers} numbers, {total_calls} calls")
                    text_lines.append("")
                else:
                    text_lines.append("No IMEI shared by multiple numbers found with current thresholds.\n")
                
                base_summary = "\n".join(text_lines)
                self.analytics_text.insert(1.0, base_summary)
                
                ai_extra = self._gemini_suggest(base_summary)
                if ai_extra:
                    if ai_extra.startswith("__ERROR__:"):
                        err_text = ai_extra.replace("__ERROR__:", "", 1).strip()
                        self.analytics_text.insert(tk.END, f"\n\nAI suggestions (Gemini) error: {err_text}")
                    else:
                        self.analytics_text.insert(tk.END, "\n\nAI suggestions (Gemini):\n")
                        self.analytics_text.insert(tk.END, ai_extra)
                else:
                    self.analytics_text.insert(tk.END, "\n\nAI suggestions (Gemini) unavailable (check API key / network).")
                
                if night_results:
                    data = [(str(row[0]), int(row[2])) for row in night_results]
                    self._draw_bar_chart(data, "Night Calls by Number")
            
            conn.close()
        except Exception as e:
            self.analytics_text.insert(1.0, f"Error: {str(e)}")
        
        self.analytics_text.config(state=tk.DISABLED)

    def _draw_bar_chart(self, data, title, orientation="vertical", canvas=None):
        target_canvas = canvas or getattr(self, "analytics_chart_canvas", None)
        if target_canvas is None:
            return
        if not data:
            return
        canvas = target_canvas
        canvas.delete("all")
        width = int(canvas.winfo_width() or 720)
        height = int(canvas.winfo_height() or 260)
        margin_left = 70
        margin_right = 30
        margin_top = 30
        margin_bottom = 55
        area_width = width - margin_left - margin_right
        area_height = height - margin_top - margin_bottom
        labels, values = zip(*data)
        max_val = max(values) if values else 0
        if max_val <= 0:
            return
        canvas.create_text(width // 2, margin_top - 12, text=title, font=("Helvetica", 11, "bold"), fill="#e2e8f0")
        canvas.create_rectangle(margin_left, margin_top, margin_left + area_width, margin_top + area_height, fill="#0b1220", outline="#1f2937")
        ticks = 5
        for i in range(ticks + 1):
            value = int(max_val * i / ticks)
            y = margin_top + area_height - (area_height * i / ticks)
            canvas.create_line(margin_left, y, margin_left + area_width, y, fill="#1f2937")
            canvas.create_text(margin_left - 8, y, text=str(value), anchor=tk.E, font=("Helvetica", 8), fill="#94a3b8")
        count = len(values)
        bar_space = area_width / max(count, 1)
        bar_width = max(bar_space * 0.6, 6)
        palette = ["#0f766e", "#2563eb", "#7c3aed", "#f97316", "#ef4444", "#22c55e", "#eab308", "#06b6d4", "#db2777", "#94a3b8"]
        for idx, (label, value) in enumerate(zip(labels, values)):
            x_center = margin_left + bar_space * idx + bar_space / 2
            bar_height = (value / max_val) * area_height
            x0 = x_center - bar_width / 2
            y0 = margin_top + area_height - bar_height
            x1 = x_center + bar_width / 2
            y1 = margin_top + area_height
            color = palette[idx % len(palette)]
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            if count <= 12:
                canvas.create_text(x_center, height - margin_bottom + 15, text=str(label)[:10], angle=35, anchor=tk.N, font=("Helvetica", 8))
            if bar_height >= 18:
                canvas.create_text(x_center, y0 - 8, text=str(value), font=("Helvetica", 8), fill="#e2e8f0")
    
    def _draw_line_chart(self, data, title, canvas=None):
        target_canvas = canvas or getattr(self, "analytics_chart_canvas", None)
        if target_canvas is None:
            return
        if not data:
            return
        canvas = target_canvas
        canvas.delete("all")
        width = int(canvas.winfo_width() or 720)
        height = int(canvas.winfo_height() or 260)
        margin_left = 70
        margin_right = 30
        margin_top = 30
        margin_bottom = 45
        area_width = width - margin_left - margin_right
        area_height = height - margin_top - margin_bottom
        labels, values = zip(*data)
        max_val = max(values) if values else 0
        if max_val <= 0:
            return
        canvas.create_text(width // 2, margin_top - 12, text=title, font=("Helvetica", 11, "bold"), fill="#e2e8f0")
        canvas.create_rectangle(margin_left, margin_top, margin_left + area_width, margin_top + area_height, fill="#0b1220", outline="#1f2937")
        ticks = 5
        for i in range(ticks + 1):
            value = int(max_val * i / ticks)
            y = margin_top + area_height - (area_height * i / ticks)
            canvas.create_line(margin_left, y, margin_left + area_width, y, fill="#1f2937")
            canvas.create_text(margin_left - 8, y, text=str(value), anchor=tk.E, font=("Helvetica", 8), fill="#94a3b8")
        count = len(values)
        points = []
        for idx, (label, value) in enumerate(zip(labels, values)):
            x = margin_left + (area_width * idx / max(count - 1, 1))
            y = margin_top + area_height - ((value / max_val) * area_height)
            points.append((x, y, label, value))
        for idx in range(len(points) - 1):
            canvas.create_line(points[idx][0], points[idx][1], points[idx + 1][0], points[idx + 1][1], fill="#2563eb", width=2)
        for idx, (x, y, label, value) in enumerate(points):
            canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#2563eb", outline="")
            if count <= 24 and idx % 2 == 0:
                canvas.create_text(x, height - margin_bottom + 10, text=str(label), anchor=tk.N, font=("Helvetica", 8), fill="#94a3b8")
    
    def _draw_pie_chart(self, data, title, canvas=None):
        target_canvas = canvas or getattr(self, "analytics_chart_canvas", None)
        if target_canvas is None:
            return
        if not data:
            return
        canvas = target_canvas
        canvas.delete("all")
        width = int(canvas.winfo_width() or 720)
        height = int(canvas.winfo_height() or 260)
        margin_top = 30
        canvas.create_text(width // 2, margin_top - 12, text=title, font=("Helvetica", 11, "bold"), fill="#e2e8f0")
        total = sum(value for _, value in data)
        if total <= 0:
            return
        radius = min(110, height // 2 - 20)
        center_x = 170
        center_y = height // 2 + 10
        palette = ["#0f766e", "#2563eb", "#7c3aed", "#f97316", "#ef4444", "#22c55e", "#eab308", "#06b6d4", "#db2777", "#94a3b8"]
        start = 0
        for idx, (label, value) in enumerate(data):
            extent = (value / total) * 360
            color = palette[idx % len(palette)]
            canvas.create_arc(center_x - radius, center_y - radius, center_x + radius, center_y + radius, start=start, extent=extent, fill=color, outline="#ffffff")
            start += extent
        legend_x = center_x + radius + 30
        legend_y = center_y - radius + 10
        for idx, (label, value) in enumerate(data):
            color = palette[idx % len(palette)]
            percent = (value / total) * 100
            canvas.create_rectangle(legend_x, legend_y + idx * 18, legend_x + 12, legend_y + idx * 18 + 12, fill=color, outline="")
            canvas.create_text(legend_x + 18, legend_y + idx * 18 + 6, text=f"{label} ({percent:.1f}%)", anchor=tk.W, font=("Helvetica", 8), fill="#e2e8f0")

    def _draw_heatmap(self, data, title, canvas=None):
        target_canvas = canvas or getattr(self, "analytics_chart_canvas", None)
        if target_canvas is None:
            return
        if not data:
            return
        canvas = target_canvas
        canvas.delete("all")
        width = int(canvas.winfo_width() or 720)
        height = int(canvas.winfo_height() or 260)
        margin_left = 70
        margin_right = 20
        margin_top = 30
        margin_bottom = 40
        area_width = width - margin_left - margin_right
        area_height = height - margin_top - margin_bottom
        days = list(data.keys())
        hours = list(range(24))
        max_val = max(max(day.values()) for day in data.values()) if data else 0
        if max_val <= 0:
            return
        canvas.create_text(width // 2, margin_top - 12, text=title, font=("Helvetica", 11, "bold"), fill="#e2e8f0")
        cell_w = area_width / max(len(hours), 1)
        cell_h = area_height / max(len(days), 1)
        for row_idx, day in enumerate(days):
            y0 = margin_top + row_idx * cell_h
            canvas.create_text(margin_left - 6, y0 + cell_h / 2, text=day[5:], anchor=tk.E, font=("Helvetica", 8), fill="#94a3b8")
            for col_idx, hour in enumerate(hours):
                value = data[day].get(hour, 0)
                intensity = value / max_val
                color = self._blend_color("#0b1220", "#3b82f6", intensity)
                x0 = margin_left + col_idx * cell_w
                y1 = y0 + cell_h
                x1 = x0 + cell_w
                canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="#111827")
        for col_idx, hour in enumerate(hours):
            if hour % 4 == 0:
                x = margin_left + col_idx * cell_w + cell_w / 2
                canvas.create_text(x, height - margin_bottom + 10, text=f"{hour:02d}", anchor=tk.N, font=("Helvetica", 8), fill="#94a3b8")

    def _draw_timeline(self, segments, title, canvas=None):
        target_canvas = canvas or getattr(self, "analytics_chart_canvas", None)
        if target_canvas is None:
            return
        if not segments:
            return
        canvas = target_canvas
        canvas.delete("all")
        width = int(canvas.winfo_width() or 720)
        height = int(canvas.winfo_height() or 260)
        margin_left = 70
        margin_right = 30
        margin_top = 30
        margin_bottom = 40
        area_width = width - margin_left - margin_right
        area_height = height - margin_top - margin_bottom
        canvas.create_text(width // 2, margin_top - 12, text=title, font=("Helvetica", 11, "bold"), fill="#e2e8f0")
        min_ts = min(seg["start"] for seg in segments)
        max_ts = max(seg["end"] for seg in segments)
        span = max(max_ts - min_ts, 1)
        row_height = area_height / max(len(segments), 1)
        palette = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#06b6d4"]
        for idx, seg in enumerate(segments):
            y0 = margin_top + idx * row_height + 4
            y1 = y0 + row_height - 8
            x0 = margin_left + ((seg["start"] - min_ts) / span) * area_width
            x1 = margin_left + ((seg["end"] - min_ts) / span) * area_width
            color = palette[idx % len(palette)]
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")
            canvas.create_text(margin_left - 6, (y0 + y1) / 2, text=seg["label"], anchor=tk.E, font=("Helvetica", 8), fill="#94a3b8")

    def _blend_color(self, base, top, alpha):
        def to_rgb(hex_color):
            return tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
        def to_hex(rgb):
            return "#%02x%02x%02x" % rgb
        alpha = max(0.0, min(1.0, alpha))
        r1, g1, b1 = to_rgb(base)
        r2, g2, b2 = to_rgb(top)
        mixed = (
            int(r1 + (r2 - r1) * alpha),
            int(g1 + (g2 - g1) * alpha),
            int(b1 + (b2 - b1) * alpha),
        )
        return to_hex(mixed)

    def _safe_int(self, value, default):
        try:
            return int(str(value).strip())
        except Exception:
            return default

    def _clean_value(self, value):
        if value is None:
            return ""
        text = str(value)
        if text.strip().lower() in {"none", "null", "nan"}:
            return ""
        return text

    def _on_tree_mousewheel(self, tree, event):
        delta = getattr(event, "delta", 0)
        if delta == 0:
            if getattr(event, "num", 0) == 4:
                delta = 120
            elif getattr(event, "num", 0) == 5:
                delta = -120
        if delta == 0:
            return
        tree.yview_scroll(int(-1 * (delta / 120)), "units")

    def _on_global_mousewheel(self, event):
        widget = event.widget
        while widget is not None and not isinstance(widget, ttk.Treeview):
            widget = widget.master
        if widget is None:
            return
        if hasattr(self, "search_tree") and widget is self.search_tree:
            self._on_tree_mousewheel(self.search_tree, event)
        elif hasattr(self, "db_tree") and widget is self.db_tree:
            self._on_tree_mousewheel(self.db_tree, event)

    def _build_filter_sql(self, target_value, date_from, date_to, include_target=True, target_field="target_no"):
        clauses = []
        params = []
        if include_target and target_value:
            clauses.append(f"{target_field} = ?")
            params.append(target_value)
        if date_from:
            clauses.append("datetime >= ?")
            params.append(f"{date_from} 00:00:00")
        if date_to:
            clauses.append("datetime <= ?")
            params.append(f"{date_to} 23:59:59")
        sql = f" AND {' AND '.join(clauses)}" if clauses else ""
        return sql, params

    def reset_network_view(self):
        self.network_view = {"scale": 1.0, "offset_x": 0, "offset_y": 0}
        self._draw_network_graph()

    def _on_network_press(self, event):
        self.network_drag = (event.x, event.y)

    def _on_network_drag(self, event):
        if not hasattr(self, "network_drag"):
            return
        dx = event.x - self.network_drag[0]
        dy = event.y - self.network_drag[1]
        self.network_view["offset_x"] += dx
        self.network_view["offset_y"] += dy
        self.network_drag = (event.x, event.y)
        self._draw_network_graph()

    def _on_network_zoom(self, event):
        delta = getattr(event, "delta", 0)
        if delta == 0:
            if getattr(event, "num", 0) == 4:
                delta = 120
            elif getattr(event, "num", 0) == 5:
                delta = -120
        scale = 1.1 if delta > 0 else 0.9
        current = self.network_view.get("scale", 1.0)
        self.network_view["scale"] = max(0.6, min(2.5, current * scale))
        self._draw_network_graph()

    def refresh_network_graph(self):
        if not hasattr(self, "network_canvas"):
            return
        target = (self.network_target_var.get() or "").strip()
        if not target:
            target = self._get_primary_target()
            if target:
                self.network_target_var.set(target)
        min_freq = self._safe_int(self.network_min_freq.get(), 3) if hasattr(self, "network_min_freq") else 3
        min_dur = self._safe_int(self.network_min_duration.get(), 0) if hasattr(self, "network_min_duration") else 0
        date_from = (self.network_date_from.get() or "").strip() if hasattr(self, "network_date_from") else ""
        date_to = (self.network_date_to.get() or "").strip() if hasattr(self, "network_date_to") else ""
        if not target:
            self.network_data = {"target": "", "edges": []}
            self._draw_network_graph()
            return

        filter_sql, params = self._build_filter_sql(target, date_from, date_to, include_target=True)
        out_where = f"target_no = ? AND b_party_no IS NOT NULL AND TRIM(b_party_no) != ''{filter_sql}"
        in_where = f"b_party_no = ? AND target_no IS NOT NULL AND TRIM(target_no) != ''{filter_sql}"
        out_params = [target] + params
        in_params = [target] + params
        sql = f"""
            SELECT contact_no, COUNT(*) AS calls, SUM(COALESCE(duration_seconds, 0)) AS total_duration,
                   MIN(datetime) AS first_dt, MAX(datetime) AS last_dt
            FROM (
                SELECT b_party_no AS contact_no, duration_seconds, datetime FROM cdrs WHERE {out_where}
                UNION ALL
                SELECT target_no AS contact_no, duration_seconds, datetime FROM cdrs WHERE {in_where}
            )
            WHERE contact_no IS NOT NULL AND TRIM(contact_no) != '' AND contact_no != ?
            GROUP BY contact_no
            HAVING calls >= ? AND total_duration >= ?
            ORDER BY calls DESC, total_duration DESC
            LIMIT 18
        """
        edges = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql, out_params + in_params + [target, min_freq, min_dur])
            for contact_no, calls, total_duration, first_dt, last_dt in cursor.fetchall():
                edges.append(
                    {
                        "contact": str(contact_no),
                        "calls": int(calls or 0),
                        "duration": int(total_duration or 0),
                        "first": first_dt,
                        "last": last_dt,
                    }
                )
            conn.close()
        except Exception:
            edges = []
        self.network_data = {"target": target, "edges": edges}
        self._draw_network_graph()

    def _draw_network_graph(self):
        canvas = getattr(self, "network_canvas", None)
        if canvas is None:
            return
        canvas.delete("all")
        width = int(canvas.winfo_width() or 900)
        height = int(canvas.winfo_height() or 520)
        data = getattr(self, "network_data", {"target": "", "edges": []})
        target = data.get("target")
        edges = data.get("edges", [])
        if not target:
            canvas.create_text(width // 2, height // 2, text="No target data available", fill="#94a3b8", font=("Helvetica", 12))
            return
        offset_x = self.network_view.get("offset_x", 0)
        offset_y = self.network_view.get("offset_y", 0)
        scale = self.network_view.get("scale", 1.0)
        center_x = width / 2 + offset_x
        center_y = height / 2 + offset_y
        radius = min(width, height) * 0.32 * scale

        canvas.create_oval(center_x - 24, center_y - 24, center_x + 24, center_y + 24, fill="#1d4ed8", outline="")
        canvas.create_text(center_x, center_y + 36, text=str(target)[-8:], fill="#e2e8f0", font=("Helvetica", 9, "bold"))

        count = len(edges)
        for idx, edge in enumerate(edges):
            angle = (2 * math.pi * idx) / max(count, 1)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            calls = edge["calls"]
            color = "#ef4444" if calls >= 20 else ("#f59e0b" if calls >= 10 else "#22c55e")
            line_width = max(1, min(6, int(1 + calls / 5)))
            node_size = max(10, min(20, int(10 + calls / 3)))
            canvas.create_line(center_x, center_y, x, y, fill=color, width=line_width)
            canvas.create_oval(x - node_size, y - node_size, x + node_size, y + node_size, fill=color, outline="")
            canvas.create_text(x, y + node_size + 10, text=str(edge["contact"])[-8:], fill="#e2e8f0", font=("Helvetica", 8))
            canvas.create_text(x, y - node_size - 10, text=str(calls), fill="#94a3b8", font=("Helvetica", 7))

    def refresh_location_analysis(self):
        if not hasattr(self, "location_canvas"):
            return
        target = (self.location_target_var.get() or "").strip()
        if not target:
            target = self._get_primary_target()
            if target:
                self.location_target_var.set(target)
        date_from = (self.location_date_from.get() or "").strip()
        date_to = (self.location_date_to.get() or "").strip()
        filter_sql, params = self._build_filter_sql(target, date_from, date_to, include_target=bool(target))
        sql = f"""
            SELECT first_cgi_lat, first_cgi_long, last_cgi_lat, last_cgi_long
            FROM cdrs
            WHERE ((first_cgi_lat IS NOT NULL AND first_cgi_long IS NOT NULL)
                OR (last_cgi_lat IS NOT NULL AND last_cgi_long IS NOT NULL))
            {filter_sql}
        """
        points = {}
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(sql, params)
            for first_lat, first_lon, last_lat, last_lon in cursor.fetchall():
                if first_lat is not None and first_lon is not None:
                    key = (round(float(first_lat), 4), round(float(first_lon), 4))
                    points[key] = points.get(key, 0) + 1
                if last_lat is not None and last_lon is not None:
                    key = (round(float(last_lat), 4), round(float(last_lon), 4))
                    points[key] = points.get(key, 0) + 1
            conn.close()
        except Exception:
            points = {}
        self._draw_location_map(points)

        if hasattr(self, "location_tree"):
            for item in self.location_tree.get_children():
                self.location_tree.delete(item)
            ranked = sorted(points.items(), key=lambda item: item[1], reverse=True)[:20]
            for idx, ((lat, lon), count) in enumerate(ranked, start=1):
                self.location_tree.insert("", tk.END, text=str(idx), values=(f"{lat:.4f}", f"{lon:.4f}", str(count)))

        if hasattr(self, "location_summary"):
            self.location_summary.config(state=tk.NORMAL)
            self.location_summary.delete(1.0, tk.END)
            total_hits = sum(points.values())
            unique = len(points)
            if points:
                lats = [lat for (lat, _), _ in points.items()]
                lons = [lon for (_, lon), _ in points.items()]
                summary = [
                    f"Total points: {unique}",
                    f"Total sightings: {total_hits}",
                    f"Lat range: {min(lats):.4f} to {max(lats):.4f}",
                    f"Lon range: {min(lons):.4f} to {max(lons):.4f}",
                ]
            else:
                summary = ["No location coordinates available in the current filters."]
            self.location_summary.insert(tk.END, "\n".join(f"• {line}" for line in summary))
            self.location_summary.config(state=tk.DISABLED)

    def _draw_location_map(self, points):
        canvas = getattr(self, "location_canvas", None)
        if canvas is None:
            return
        canvas.delete("all")
        width = int(canvas.winfo_width() or 900)
        height = int(canvas.winfo_height() or 520)
        if not points:
            canvas.create_text(width // 2, height // 2, text="No location data available", fill="#94a3b8", font=("Helvetica", 12))
            return
        padding = 40
        lats = [lat for (lat, _), _ in points.items()]
        lons = [lon for (_, lon), _ in points.items()]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        if min_lat == max_lat:
            min_lat -= 0.01
            max_lat += 0.01
        if min_lon == max_lon:
            min_lon -= 0.01
            max_lon += 0.01
        max_count = max(points.values()) if points else 1

        for (lat, lon), count in points.items():
            x = padding + ((lon - min_lon) / (max_lon - min_lon)) * (width - padding * 2)
            y = padding + ((max_lat - lat) / (max_lat - min_lat)) * (height - padding * 2)
            intensity = count / max_count
            color = self._blend_color("#0b1220", "#22c55e", intensity)
            size = 4 + min(10, int(count / 2))
            canvas.create_oval(x - size, y - size, x + size, y + size, fill=color, outline="")

    def _analytics_filter_sql(self, include_target=True):
        clauses = []
        params = []
        target_number = (self.analytics_target_var.get() or "").strip() if hasattr(self, "analytics_target_var") else ""
        date_from = (self.analytics_date_from.get() or "").strip() if hasattr(self, "analytics_date_from") else ""
        date_to = (self.analytics_date_to.get() or "").strip() if hasattr(self, "analytics_date_to") else ""
        if include_target and target_number:
            clauses.append("target_no = ?")
            params.append(target_number)
        if date_from:
            clauses.append("DATE(datetime) >= ?")
            params.append(date_from)
        if date_to:
            clauses.append("DATE(datetime) <= ?")
            params.append(date_to)
        sql = f" AND {' AND '.join(clauses)}" if clauses else ""
        return sql, params

    def refresh_analytics_dashboard(self):
        tab = self.analytics_notebook.tab(self.analytics_notebook.select(), "text") if hasattr(self, "analytics_notebook") else ""
        target_number = (self.analytics_target_var.get() or "").strip()
        date_from = (self.analytics_date_from.get() or "").strip()
        date_to = (self.analytics_date_to.get() or "").strip()
        if not target_number:
            target_number = self._get_primary_target()

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if tab == "Call Volume Trend":
                filter_sql, params = self._analytics_filter_sql(include_target=True)
                cursor.execute(
                    f"""
                    SELECT DATE(datetime), COUNT(*)
                    FROM cdrs
                    WHERE datetime IS NOT NULL {filter_sql}
                    GROUP BY DATE(datetime)
                    ORDER BY DATE(datetime)
                    """,
                    params,
                )
                results = cursor.fetchall()
                data = [(row[0][5:] if row[0] else "N/A", int(row[1])) for row in results[-30:]]
                self._draw_line_chart(data, "Call Volume Trend", canvas=self.analytics_tabs[tab])
            elif tab == "Hourly Activity Heatmap":
                filter_sql, params = self._analytics_filter_sql(include_target=True)
                cursor.execute(
                    f"""
                    SELECT DATE(datetime) AS day, CAST(strftime('%H', datetime) AS INTEGER) AS hour, COUNT(*)
                    FROM cdrs
                    WHERE datetime IS NOT NULL {filter_sql}
                    GROUP BY day, hour
                    ORDER BY day ASC
                    """,
                    params,
                )
                results = cursor.fetchall()
                days = sorted({row[0] for row in results})[-7:]
                heatmap = {day: {h: 0 for h in range(24)} for day in days}
                for day, hour, count in results:
                    if day in heatmap:
                        heatmap[day][int(hour)] = int(count)
                self._draw_heatmap(heatmap, "Hourly Activity Heatmap", canvas=self.analytics_tabs[tab])
            elif tab == "IMEI Switching Timeline":
                if target_number:
                    filter_sql, params = self._analytics_filter_sql(include_target=True)
                    cursor.execute(
                        f"""
                        SELECT imei, MIN(datetime), MAX(datetime)
                        FROM cdrs
                        WHERE imei IS NOT NULL AND TRIM(imei) != '' {filter_sql}
                        GROUP BY imei
                        ORDER BY MIN(datetime)
                        """,
                        params,
                    )
                    results = cursor.fetchall()
                else:
                    results = []
                segments = []
                for imei, start_dt, end_dt in results:
                    if not start_dt or not end_dt:
                        continue
                    try:
                        start_ts = datetime.fromisoformat(start_dt).timestamp()
                        end_ts = datetime.fromisoformat(end_dt).timestamp()
                    except ValueError:
                        continue
                    segments.append({"label": str(imei)[-6:], "start": start_ts, "end": end_ts})
                self._draw_timeline(segments, "IMEI Switching Timeline", canvas=self.analytics_tabs[tab])
            elif tab == "Top Contacts":
                filter_sql, params = self._analytics_filter_sql(include_target=True)
                cursor.execute(
                    f"""
                    SELECT b_party_no, COUNT(*)
                    FROM cdrs
                    WHERE b_party_no IS NOT NULL {filter_sql}
                    GROUP BY b_party_no
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                    """,
                    params,
                )
                results = cursor.fetchall()
                data = [(str(row[0])[-8:], int(row[1])) for row in results]
                self._draw_bar_chart(data, "Top Contacts", canvas=self.analytics_tabs[tab])
            elif tab == "Duration Buckets":
                filter_sql, params = self._analytics_filter_sql(include_target=True)
                cursor.execute(
                    f"""
                    SELECT
                        CASE
                            WHEN duration_seconds < 30 THEN '<30s'
                            WHEN duration_seconds < 120 THEN '30-120s'
                            WHEN duration_seconds < 300 THEN '2-5m'
                            WHEN duration_seconds < 600 THEN '5-10m'
                            ELSE '10m+'
                        END AS bucket,
                        COUNT(*)
                    FROM cdrs
                    WHERE duration_seconds IS NOT NULL {filter_sql}
                    GROUP BY bucket
                    """,
                    params,
                )
                results = cursor.fetchall()
                bucket_order = ["<30s", "30-120s", "2-5m", "5-10m", "10m+"]
                bucket_map = {row[0]: int(row[1]) for row in results}
                data = [(label, bucket_map.get(label, 0)) for label in bucket_order]
                self._draw_pie_chart(data, "Duration Buckets", canvas=self.analytics_tabs[tab])
            conn.close()
        except Exception:
            pass

        self._render_ai_summary(target_number, date_from, date_to)

    def _get_primary_target(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT target_no, COUNT(*) AS c FROM cdrs WHERE target_no IS NOT NULL GROUP BY target_no ORDER BY c DESC LIMIT 1"
            )
            row = cursor.fetchone()
            conn.close()
            if row:
                return row[0]
        except Exception:
            return ""
        return ""

    def _render_ai_summary(self, target_number, date_from, date_to):
        if not hasattr(self, "ai_summary_text"):
            return
        self.ai_summary_text.config(state=tk.NORMAL)
        self.ai_summary_text.delete(1.0, tk.END)
        risk_score = 0
        behavior = "Undetermined"
        notes = []
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            filter_sql, params = self._analytics_filter_sql(include_target=True)
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM cdrs
                WHERE CAST(strftime('%H', datetime) AS INTEGER) >= 22
                   OR CAST(strftime('%H', datetime) AS INTEGER) < 6
                {filter_sql}
                """,
                params,
            )
            night_calls = cursor.fetchone()[0]
            cursor.execute(f"SELECT COUNT(*) FROM cdrs WHERE 1=1 {filter_sql}", params)
            total_calls = cursor.fetchone()[0]
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM (
                    SELECT imei
                    FROM cdrs
                    WHERE imei IS NOT NULL AND TRIM(imei) != ''
                    {filter_sql}
                    GROUP BY imei
                    HAVING COUNT(DISTINCT target_no) >= 2
                )
                """,
                params,
            )
            shared_imeis = cursor.fetchone()[0]
            cursor.execute(
                f"""
                SELECT b_party_no, COUNT(*)
                FROM cdrs
                WHERE b_party_no IS NOT NULL
                {filter_sql}
                GROUP BY b_party_no
                ORDER BY COUNT(*) DESC
                LIMIT 1
                """,
                params,
            )
            row = cursor.fetchone()
            frequent_contact = row[0] if row else "Unknown"
            risk_score = min(100, int((night_calls / max(total_calls, 1)) * 60 + shared_imeis * 5))
            behavior = "Elevated" if risk_score >= 60 else ("Moderate" if risk_score >= 35 else "Low")
            notes.append(f"Suspicious time windows: {night_calls} late-night calls")
            notes.append(f"IMEI change patterns: {shared_imeis} shared devices detected")
            notes.append(f"Most frequent associate: {frequent_contact}")
            if target_number:
                notes.append(f"Target focus: {target_number}")
            conn.close()
        except Exception:
            notes.append("AI summary unavailable due to missing data.")

        self.ai_risk_label.config(text=f"Risk Score: {risk_score}")
        self.ai_behavior_label.config(text=f"Behavior: {behavior}")
        self.ai_summary_text.insert(tk.END, "\n".join(f"• {note}" for note in notes))
        self.ai_summary_text.config(state=tk.DISABLED)

    def _gemini_suggest(self, summary_text):
        api_key = os.environ.get("GOOGLE_AI_API_KEY")
        if not api_key:
            return "__ERROR__: Missing GOOGLE_AI_API_KEY."
        available_models = self._get_gemini_models(api_key)
        prompt = (
            "You are a telecom CDR investigation assistant. "
            "Based only on the patterns below, write short bullet-point insights and "
            "practical next-step recommendations for an investigator. "
            "Keep it concise and investigation-focused.\n\n"
            f"{summary_text}\n\n"
        )
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        data = json.dumps(payload).encode("utf-8")
        model_candidates = available_models or [
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash-001",
            "gemini-1.5-pro",
            "gemini-1.5-pro-latest",
        ]
        def model_score(name):
            lowered = name.lower()
            if "flash" in lowered:
                return (0, name)
            if "pro" in lowered:
                return (1, name)
            return (2, name)
        model_candidates = sorted(model_candidates, key=model_score)
        last_error = None
        for model in model_candidates:
            url = (
                "https://generativelanguage.googleapis.com/v1/"
                f"models/{model}:generateContent"
                f"?key={api_key}"
            )
            req = urlrequest.Request(
                url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            try:
                with urlrequest.urlopen(req, timeout=25) as resp:
                    body = resp.read().decode("utf-8")
                obj = json.loads(body)
                candidates = obj.get("candidates") or []
                if not candidates:
                    last_error = "Empty response from Gemini."
                    continue
                content = candidates[0].get("content") or {}
                parts = content.get("parts") or []
                texts = [p.get("text", "") for p in parts if isinstance(p, dict)]
                combined = "\n".join(t for t in texts if t).strip()
                if not combined:
                    last_error = "Gemini returned no text."
                    continue
                return combined
            except urlerror.HTTPError as exc:
                try:
                    body = exc.read().decode("utf-8")
                    obj = json.loads(body)
                    message = obj.get("error", {}).get("message") or body
                except Exception:
                    message = str(exc)
                last_error = message
                continue
            except urlerror.URLError as exc:
                return f"__ERROR__: {exc.reason}"
            except (json.JSONDecodeError, TimeoutError, KeyError):
                last_error = "Invalid response or timeout."
                continue
        if last_error:
            return f"__ERROR__: {last_error}"
        return "__ERROR__: Gemini request failed."

    def _get_gemini_models(self, api_key):
        url = f"https://generativelanguage.googleapis.com/v1/models?key={api_key}"
        req = urlrequest.Request(url, headers={"Content-Type": "application/json"})
        try:
            with urlrequest.urlopen(req, timeout=15) as resp:
                body = resp.read().decode("utf-8")
            obj = json.loads(body)
            models = obj.get("models") or []
            supported = []
            for model in models:
                name = model.get("name") or ""
                methods = model.get("supportedGenerationMethods") or []
                if "generateContent" in methods and name.startswith("models/"):
                    supported.append(name.replace("models/", ""))
            return supported
        except Exception:
            return []
    
    def view_all_records(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT id, target_no, call_type, toc, b_party_no, lrn_no, lrn_tsp_lsa, datetime, duration_seconds, first_cgi_lat, first_cgi_long, first_cgi, last_cgi_lat, last_cgi_long, last_cgi, smsc_no, service_type, imei, imsi, call_fow_no, roam_nw, sw_msc_id, in_tg, out_tg, vowifi_first_ue_ip, port1, vowifi_last_ue_ip, port2 FROM cdrs"
            params = []

            import_label = self.db_import_var.get().strip() if hasattr(self, "db_import_var") else ""
            if import_label and import_label != "All files":
                batch_id = None
                if hasattr(self, "import_batches"):
                    batch_id = self.import_batches.get(import_label)
                if batch_id is not None:
                    query += " WHERE import_batch_id = ?"
                    params.append(int(batch_id))

            query += " LIMIT 1000"

            cursor.execute(query, params)
            results = cursor.fetchall()
            
            for item in self.db_tree.get_children():
                self.db_tree.delete(item)

            # Batch CGI lookup for tower matching
            tower_map = {}
            cgi_set = set()
            for row in results:
                f_cgi = self._clean_value(row[11])
                l_cgi = self._clean_value(row[14])
                if f_cgi: cgi_set.add(f_cgi)
                if l_cgi: cgi_set.add(l_cgi)
            if cgi_set:
                tower_map = self.db_manager.lookup_towers_by_cgis(list(cgi_set))

            for row in results:
                values = self._map_row_to_values(row, tower_map)
                self.db_tree.insert("", tk.END, text=str(row[0]), values=values)
            
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
            
            query = "SELECT * FROM cdrs"
            params = []

            import_label = self.db_import_var.get().strip() if hasattr(self, "db_import_var") else ""
            if import_label and import_label != "All files":
                batch_id = None
                if hasattr(self, "import_batches"):
                    batch_id = self.import_batches.get(import_label)
                if batch_id is not None:
                    query += " WHERE import_batch_id = ?"
                    params.append(int(batch_id))

            cursor.execute(query, params)
            results = cursor.fetchall()
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([description[0] for description in cursor.description])
                writer.writerows(results)
            
            messagebox.showinfo("Success", f"Exported {len(results)} records to {file_path}")
            conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"Export error: {str(e)}")

    def _on_upload_tab_change(self):
        if not hasattr(self, "upload_tabs_notebook"):
            return
        selected = self.upload_tabs_notebook.tab(self.upload_tabs_notebook.select(), "text")
        if hasattr(self, "search_import_var"):
            self.search_import_var.set(selected)
        if hasattr(self, "search_import_combo"):
            self.search_import_combo.set(selected)

    def refresh_import_tabs(self):
        if not hasattr(self, "upload_tabs_notebook"):
            return
        notebook = self.upload_tabs_notebook
        for tab_id in notebook.tabs():
            notebook.forget(tab_id)
        labels = ["All files"] + list(self.import_batches.keys())
        for label in labels:
            tab = ttk.Frame(notebook)
            notebook.add(tab, text=label)
        selected = self.search_import_var.get().strip() if hasattr(self, "search_import_var") else "All files"
        if selected not in labels:
            selected = "All files"
        for tab_id in notebook.tabs():
            if notebook.tab(tab_id, "text") == selected:
                notebook.select(tab_id)
                break

    def _refresh_after_upload(self):
        self._update_header_stats()
        self._refresh_dashboard_metrics()
        if hasattr(self, "analytics_notebook"):
            self.refresh_analytics_dashboard()
        if hasattr(self, "network_canvas"):
            self.refresh_network_graph()
        if hasattr(self, "location_canvas"):
            self.refresh_location_analysis()

    def refresh_import_sources(self):
        try:
            batches = self.db_manager.get_import_batches()
        except Exception:
            batches = []

        self.import_batches = {}
        labels = ["All files"]
        for row in batches:
            label = f"{row['file_name']} ({row['record_count']})"
            self.import_batches[label] = row["id"]
            labels.append(label)

        if hasattr(self, "search_import_combo"):
            self.search_import_combo["values"] = labels
            current = self.search_import_var.get().strip() if hasattr(self, "search_import_var") else ""
            self.search_import_combo.set(current if current in labels else "All files")

        if hasattr(self, "db_import_combo"):
            self.db_import_combo["values"] = labels
            current = self.db_import_var.get().strip() if hasattr(self, "db_import_var") else ""
            self.db_import_combo.set(current if current in labels else "All files")
        self.refresh_import_tabs()

    # ── Cell Tower Methods ──────────────────────────────────────────

    def _refresh_cell_tower_status(self):
        """Update the cell tower status label with current count."""
        try:
            count = self.db_manager.get_cell_tower_count()
            if self.cell_tower_status_label:
                if count > 0:
                    self.cell_tower_status_label.config(text=f"✓ {count} towers loaded")
                else:
                    self.cell_tower_status_label.config(text="No towers loaded")
        except Exception:
            pass

    def upload_cell_tower_csv(self):
        """Upload a cell tower CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select Cell Tower CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Importing Cell Towers")
        progress_window.geometry("400x120")
        progress_window.transient(self.root)
        progress_window.grab_set()

        ttk.Label(progress_window, text="Importing cell tower data...",
                  font=("Helvetica", 11)).pack(pady=(16, 8))
        progress_var = tk.IntVar(value=0)
        progress_bar = ttk.Progressbar(progress_window, variable=progress_var,
                                        maximum=100, length=350)
        progress_bar.pack(pady=4, padx=20)
        status_label = ttk.Label(progress_window, text="Starting...")
        status_label.pack(pady=4)

        def on_progress(pct, count):
            progress_var.set(pct)
            status_label.config(text=f"{count} towers imported ({pct}%)")
            progress_window.update_idletasks()

        try:
            success, msg, count = self.cell_tower_importer.import_csv(
                file_path, progress_callback=on_progress
            )
            progress_window.destroy()

            if success:
                messagebox.showinfo("Success", msg)
                self._refresh_cell_tower_status()
                # Refresh CDR views to show matched tower info
                try:
                    self.view_all_records()
                except Exception:
                    pass
            else:
                messagebox.showwarning("Import Warning", msg)
        except Exception as e:
            progress_window.destroy()
            messagebox.showerror("Error", f"Import failed: {str(e)}")

    def clear_cell_towers(self):
        """Clear all cell tower data from the database."""
        if not messagebox.askyesno("Confirm", "Clear all cell tower data?"):
            return
        try:
            self.db_manager.clear_cell_towers()
            self._refresh_cell_tower_status()
            messagebox.showinfo("Success", "Cell tower data cleared.")
            try:
                self.view_all_records()
            except Exception:
                pass
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing towers: {str(e)}")

    # ── Group Management Methods ─────────────────────────────────────

    def _refresh_group_list(self):
        """Reload the group listbox from DB."""
        if not hasattr(self, "group_listbox"):
            return
        self.group_listbox.delete(0, tk.END)
        groups = self.db_manager.get_all_groups()
        self._group_ids = []
        for gid, name, _ in groups:
            file_count = len(self.db_manager.get_group_imports(gid))
            cdr_count = self.db_manager.get_group_cdr_count(gid)
            self.group_listbox.insert(tk.END, f"{name}  ({file_count} files · {cdr_count} CDRs)")
            self._group_ids.append(gid)
        # Also refresh group filter in search tab
        self._refresh_search_group_filter()

    def _refresh_search_group_filter(self):
        """Update the group dropdown on the search tab."""
        if not hasattr(self, "search_group_combo"):
            return
        groups = self.db_manager.get_all_groups()
        labels = ["All groups"]
        self._search_group_ids = {"All groups": None}
        for gid, name, _ in groups:
            labels.append(name)
            self._search_group_ids[name] = gid
        self.search_group_combo["values"] = labels
        current = self.search_group_var.get().strip()
        if current not in labels:
            self.search_group_combo.set("All groups")

    def _get_selected_group_id(self):
        """Return the currently selected group ID or None."""
        if not hasattr(self, "group_listbox"):
            return None
        sel = self.group_listbox.curselection()
        if not sel:
            return None
        idx = sel[0]
        if idx < len(self._group_ids):
            return self._group_ids[idx]
        return None

    def _on_group_select(self):
        """Handle group selection — populate right panel."""
        gid = self._get_selected_group_id()
        if gid is None:
            if hasattr(self, "group_detail_label"):
                self.group_detail_label.config(text="Select a group")
                self.group_stats_label.config(text="")
            if hasattr(self, "group_files_tree"):
                for item in self.group_files_tree.get_children():
                    self.group_files_tree.delete(item)
            return

        # Get group name
        groups = self.db_manager.get_all_groups()
        name = ""
        for g in groups:
            if g[0] == gid:
                name = g[1]
                break

        imports = self.db_manager.get_group_imports(gid)
        cdr_count = self.db_manager.get_group_cdr_count(gid)

        if hasattr(self, "group_detail_label"):
            self.group_detail_label.config(text=f"Group: {name}")
            self.group_stats_label.config(text=f"{len(imports)} CDR files · {cdr_count} total records")

        if hasattr(self, "group_files_tree"):
            for item in self.group_files_tree.get_children():
                self.group_files_tree.delete(item)
            for idx, imp in enumerate(imports, 1):
                imp_id, fname, imported_at, rec_count = imp
                self.group_files_tree.insert(
                    "", tk.END, text=str(idx),
                    values=(fname, rec_count or 0, str(imported_at or "")),
                    tags=(str(imp_id),),
                )

    def _create_group(self):
        """Prompt user to create a new group."""
        from tkinter import simpledialog
        name = simpledialog.askstring("New Group", "Enter group name:", parent=self.root)
        if not name or not name.strip():
            return
        try:
            self.db_manager.create_group(name.strip())
            self._refresh_group_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not create group: {str(e)}")

    def _rename_group(self):
        """Rename the selected group."""
        gid = self._get_selected_group_id()
        if gid is None:
            messagebox.showinfo("Info", "Select a group to rename.")
            return
        from tkinter import simpledialog
        new_name = simpledialog.askstring("Rename Group", "Enter new name:", parent=self.root)
        if not new_name or not new_name.strip():
            return
        try:
            self.db_manager.rename_group(gid, new_name.strip())
            self._refresh_group_list()
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename group: {str(e)}")

    def _delete_group(self):
        """Delete the selected group (CDR records are NOT deleted)."""
        gid = self._get_selected_group_id()
        if gid is None:
            messagebox.showinfo("Info", "Select a group to delete.")
            return
        if not messagebox.askyesno("Confirm", "Delete this group? CDR files will NOT be removed from the database."):
            return
        try:
            self.db_manager.delete_group(gid)
            self._refresh_group_list()
            if hasattr(self, "group_detail_label"):
                self.group_detail_label.config(text="Select a group")
                self.group_stats_label.config(text="")
            if hasattr(self, "group_files_tree"):
                for item in self.group_files_tree.get_children():
                    self.group_files_tree.delete(item)
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete group: {str(e)}")

    def _add_files_to_group(self):
        """Show dialog to add existing CDR imports to the selected group."""
        gid = self._get_selected_group_id()
        if gid is None:
            messagebox.showinfo("Info", "Select a group first.")
            return

        # Get all imports
        try:
            all_imports = self.db_manager.get_import_batches()
        except Exception:
            all_imports = []

        if not all_imports:
            messagebox.showinfo("Info", "No CDR files have been imported yet. Upload CDR files first.")
            return

        # Already assigned to this group
        already = set()
        for imp in self.db_manager.get_group_imports(gid):
            already.add(imp[0])

        # Build a selection dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add CDR Files to Group")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.grab_set()

        ttk.Label(dialog, text="Select CDR files to add:", font=("Helvetica", 12, "bold")).pack(padx=12, pady=(12, 8))

        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=12)

        sb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        lb = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, yscrollcommand=sb.set,
                        background="#0b1220", foreground="#e2e8f0",
                        selectbackground="#3b82f6", selectforeground="#ffffff",
                        font=("Helvetica", 11))
        sb.config(command=lb.yview)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        sb.pack(side=tk.RIGHT, fill=tk.Y)

        available_ids = []
        for imp in all_imports:
            imp_id = imp["id"]
            if imp_id not in already:
                fname = imp["file_name"]
                count = imp["record_count"]
                lb.insert(tk.END, f"{fname}  ({count} records)")
                available_ids.append(imp_id)

        if not available_ids:
            lb.insert(tk.END, "(All files already in this group)")

        def do_add():
            selections = lb.curselection()
            for i in selections:
                if i < len(available_ids):
                    self.db_manager.assign_import_to_group(available_ids[i], gid)
            dialog.destroy()
            self._refresh_group_list()
            self._on_group_select()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=tk.X, padx=12, pady=12)
        ttk.Button(btn_frame, text="Add Selected", style="Accent.TButton", command=do_add, width=14).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy, width=10).pack(side=tk.LEFT)

    def _remove_file_from_group(self):
        """Remove the selected file from the current group."""
        gid = self._get_selected_group_id()
        if gid is None:
            messagebox.showinfo("Info", "Select a group first.")
            return
        if not hasattr(self, "group_files_tree"):
            return
        sel = self.group_files_tree.selection()
        if not sel:
            messagebox.showinfo("Info", "Select a file to remove from the group.")
            return
        for item_id in sel:
            tags = self.group_files_tree.item(item_id, "tags")
            if tags:
                import_batch_id = int(tags[0])
                self.db_manager.remove_import_from_group(import_batch_id, gid)
        self._refresh_group_list()
        self._on_group_select()

    def _view_group_cdrs(self):
        """Switch to Search tab and filter by the selected group."""
        gid = self._get_selected_group_id()
        if gid is None:
            messagebox.showinfo("Info", "Select a group first.")
            return
        # Find group name
        groups = self.db_manager.get_all_groups()
        name = ""
        for g in groups:
            if g[0] == gid:
                name = g[1]
                break
        # Switch to Search page and set group filter
        self.show_page("Search")
        if hasattr(self, "search_group_combo") and hasattr(self, "search_group_var"):
            self.search_group_var.set(name)
        self.search_records()

    def change_database(self):
        db_path = filedialog.asksaveasfilename(
            defaultextension=".db",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")]
        )
        if db_path:
            self.db_path = db_path
            self.db_manager = DatabaseManager(self.db_path)
            self.csv_importer = CSVImporter(self.db_manager)
            self.cell_tower_importer = CellTowerImporter(self.db_manager)
            messagebox.showinfo("Success", f"Database changed to: {db_path}")
            self._refresh_cell_tower_status()
            self.view_all_records()

if __name__ == "__main__":
    root = tk.Tk()
    app = CDRAnalysisTool(root)
    root.mainloop()
