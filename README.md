# CDR MongoDB Uploader

A Python application for uploading Call Detail Records (CDR) from CSV files to a local MongoDB database with a user-friendly GUI.

## Features

- ✅ Local MongoDB support (no cloud dependencies)
- 🎨 Modern tkinter GUI interface
- 📊 Real-time upload progress tracking
- 📝 Detailed logging of upload operations
- ⚙️ Configurable MongoDB host and port
- 🔄 Threaded uploads (non-blocking UI)

## Prerequisites

- Python 3.7+
- MongoDB installed and running locally
- Required packages (install via requirements.txt)

## Installation

1. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure MongoDB is running locally:
   ```bash
   # On macOS (if installed via Homebrew)
   brew services start mongodb-community
   
   # Or manually
   mongod --dbpath /path/to/your/data/directory
   ```

## Usage

### GUI Mode (Recommended)

Run the GUI application:
```bash
python cdr_gui.py
```

The GUI allows you to:
1. Configure MongoDB connection (host and port)
2. Browse and select CSV file
3. Upload data with progress tracking
4. View real-time logs

### Command Line Mode

You can still use the command-line interface:
```bash
python cdr_uploader.py /path/to/your/cdr_file.csv
```

## MongoDB Configuration

Default settings:
- **Host**: localhost
- **Port**: 27017
- **Database**: cdr_database
- **Collection**: cdrs

You can change the host and port in the GUI or by modifying the code.

## CSV Format

The CSV file should contain the following columns:
- Target No, Call Type, TOC, B Party No, LRN No, LRN TSP-LSA
- Date, Time, Dur(s)
- First CGI Lat/Long, First CGI
- Last CGI Lat/Long, Last CGI
- SMSC No, Service Type, IMEI, IMSI
- Call Fow No, Roam Nw, SW & MSC ID
- IN TG, OUT TG
- Vowifi First UE IP, Port1, Vowifi Last UE IP, Port2

## Troubleshooting

**MongoDB Connection Error:**
- Ensure MongoDB is running: `brew services list` (macOS) or `systemctl status mongod` (Linux)
- Check if the port is correct (default: 27017)
- Verify no firewall is blocking the connection

**File Format Error:**
- Ensure the CSV has the proper header row with 'Target No'
- Check file encoding (should be UTF-8)

## License

MIT License
   ```
   docker build -t cdr-uploader .
   ```

2. Run the container with your CSV file mounted:
   ```
   docker run -v /path/to/your/cdr_file.csv:/app/cdr_file.csv cdr-uploader python cdr_uploader.py /app/cdr_file.csv
   ```

Replace `/path/to/your/cdr_file.csv` with the actual path to your CSV file on the host machine.

## Troubleshooting

- Ensure the CSV file exists and is readable.
- Check MongoDB connection string and credentials.
- Verify CSV format (comma-separated, headers in first row).
- If insertion fails, check for duplicate keys or MongoDB permissions.# ifso
