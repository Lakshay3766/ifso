# CDR Analysis & Investigation Tool

A comprehensive Python application for analyzing Call Detail Records (CDR) with advanced search, grouping, and reporting capabilities. Designed for law enforcement and investigative purposes.

## 🎯 Features

- **Data Management**
  - Upload CSV files to SQLite database
  - Fast batch import with progress updates
  - Support for multiple CDR formats
  - Database export functionality

- **Search & Analysis**
  - Search by caller (A Party) and receiver (B Party)
  - Filter by date/time range, duration range, IMEI/IMSI, CGI
  - Filter by Call Type and Service Type (dropdown)
  - Advanced multi-criteria search
  - Pagination + sortable columns + record details panel
  - Export current results view

- **Group Analysis**
  - Group by A Party / B Party
  - Group by IMEI / IMSI
  - Group by Call Type / Service Type
  - Group by TOC / Roam NW / First CGI / Last CGI

- **Reports**
  - Summary (totals, unique numbers/devices, date range)
  - Top call durations (optionally for a number/date range)
  - Top IMEI (optionally for a date range)
  - Call Type + Service Type distributions

- **User Interface**
  - Modern tabbed interface
  - Background import (GUI stays responsive)
  - Detailed logging
  - Right-click context menu for quick investigation
  - Export to CSV

## 📋 Prerequisites

- Python 3.7 or higher
- Tkinter (usually comes with Python)
- SQLite3 (built-in with Python)

## 🚀 Installation

1. Clone or download this repository

2. Make sure Python 3.7+ is installed:
   ```bash
   python3 --version
   ```

3. Tkinter installation (if needed):
   ```bash
   # macOS
   brew install python-tk
   
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # Windows (usually pre-installed)
   ```

## 💻 Usage

### Full Analysis Tool

Run the complete CDR Analysis application:

```bash
python3 main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### Uploader Only

Run just the uploader application:

```bash
python3 uploader.py
```

### Legacy Applications

The original files are still available:
```bash
python3 legacy/cdr_analysis_tool.py  # Original analysis tool
python3 legacy/cdr_uploader.py       # Original uploader
```

## 📁 Project Structure

```
IFSO Special Cell/
│
├── main.py                 # Main application entry point
├── uploader.py             # Standalone uploader entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── Dockerfile             # Docker configuration
│
├── src/                   # Source code directory
│   ├── __init__.py
│   │
│   ├── database/          # Database operations
│   │   ├── __init__.py
│   │   ├── db_manager.py  # SQLite database manager
│   │   └── csv_importer.py # CSV import functionality
│   │
│   ├── gui/               # GUI components
│   │   ├── __init__.py
│   │   ├── main_window.py # Main analysis window
│   │   └── uploader_window.py # Uploader window
│   │
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── helpers.py     # Helper functions
│       └── validators.py  # Validation functions
│
├── data/                  # Data directory
│   └── cdr_database.db   # SQLite database (created on first run)
│
└── legacy/                # Original files (for reference)
    ├── cdr_analysis_tool.py
    ├── cdr_uploader.py
    └── simple_gui.py
```

## 📊 CSV Format

The application expects CSV files with the following columns:

- **Target No** - Primary phone number (A Party)
- **Call Type** - Type of call (Voice, SMS, Data, etc.)
- **TOC** - Type of Connection
- **B Party No** - Called number (B Party)
- **LRN No** - Location Routing Number
- **LRN TSP-LSA** - TSP and LSA information
- **Date** - Call date (DD/MM/YYYY)
- **Time** - Call time (HH:MM:SS)
- **Dur(s)** - Duration in seconds
- **First CGI** - First Cell Global Identity
- **Last CGI** - Last Cell Global Identity
- **SMSC No** - SMS Center number
- **Service Type** - Type of service
- **IMEI** - Device IMEI number
- **IMSI** - SIM IMSI number
- **Call Fow No** - Call forward number
- **Roam Nw** - Roaming network
- **SW & MSC ID** - Switching and MSC ID
- **IN TG, OUT TG** - Trunk groups
- **VoWiFi details** - WiFi calling information

## 🔍 How to Use

### 1. Upload Data

1. Launch the application: `python3 main.py`
2. Go to **File → Upload CSV** or click "Upload CSV File"
3. Select your CDR CSV file
4. Wait for the upload to complete
5. Check the Database tab to verify records

### 2. Search Records

1. Go to the **Search** tab
2. Enter search criteria:
   - A Party / B Party
   - Date From/To (YYYY-MM-DD)
   - Time From/To (HH:MM:SS)
   - Duration Min/Max (seconds)
   - IMEI / IMSI
   - Call Type / Service Type (dropdown)
   - CGI (matches First CGI or Last CGI)
3. Click **Search**
4. Use **Prev/Next** for pagination
5. Click a row to view the full **Record Details**
6. Right-click a row for quick investigation shortcuts
7. Export the current results view if needed

### 3. Investigation & Link Analysis

1. Go to the **Investigation** tab
2. Use:
   - **Top Contacts** (most frequent contacts for a number)
   - **Mutual Contacts** (common contacts between two numbers)
   - **Direct Link** (calls directly between two numbers + call type breakdown)
   - **Timeline** (daily/hourly activity)
   - **IMEI / IMSI** (IMEI→Numbers and Number→IMEI)
3. Export any table to CSV as needed

### 4. Group Analysis

1. Go to the **Groups** tab
2. Select a group-by field (A Party, B Party, IMEI, IMSI, Call Type, Service Type, TOC, Roam NW, First CGI, Last CGI)
3. Export results if needed

### 5. Generate Reports

1. Go to the **Reports** tab
2. Use:
   - **Summary** (totals, unique numbers/devices, date range)
   - **Top Durations** (optionally filter by number/date range)
   - **Top IMEI** (optionally filter by date range)
   - **Call Types** + **Service Types** distributions
3. Export results if needed

### 6. Tower / CGI Analysis

1. Go to the **Tower/CGI** tab
2. Use **Top CGI** to see most frequent First/Last CGI (optionally filtered by a number/date range)
3. Use **CGI → Numbers** to list numbers seen on a given CGI
4. Export results if needed

## ⚠️ Troubleshooting

**Application won't start:**
- Ensure Python 3.7+ is installed: `python3 --version`
- Check if tkinter is available: `python3 -c "import tkinter"`
- Install tkinter if missing (see Prerequisites)

**CSV upload fails:**
- Verify CSV has "Target No" in the header row
- Check file encoding (should be UTF-8)
- Ensure date format is DD/MM/YYYY
- Make sure you have write permissions in the directory

**Database errors:**
- Check if database file is not corrupted
- Ensure you have write permissions
- Try creating a new database file

**Search returns no results:**
- Verify data is uploaded (check Database tab)
- Use correct date format: YYYY-MM-DD
- Try partial searches (don't include full numbers)

## 🏗️ Development

### Project Architecture

The application follows a modular architecture:

- **database/**: Handles all database operations
  - `db_manager.py`: Core database CRUD operations
  - `csv_importer.py`: CSV file parsing and import

- **gui/**: All GUI components
  - `main_window.py`: Main application window
  - `uploader_window.py`: Standalone uploader

- **utils/**: Utility functions
  - `helpers.py`: Common helper functions
  - `validators.py`: Input validation

### Adding New Features

1. Database operations go in `src/database/db_manager.py`
2. GUI components go in `src/gui/`
3. Utility functions go in `src/utils/`
4. Update imports in `__init__.py` files

## 🔒 Security Notes

- This tool is designed for authorized investigative use only
- All data is stored locally in SQLite database
- No cloud services or external connections
- Sensitive data should be handled according to regulations
- Always backup important data before clearing database

## 📝 License

This project is licensed for use by authorized personnel only.

## 👨‍💻 Support

For support or questions, contact the development team.

---

**Version:** 1.0.0  
**Last Updated:** February 2026  
**Licensed to:** Manoj Dube 9819194961
