# Case Management System - Quick Guide

## 🎯 Overview

The CDR Analysis Tool now includes a **Case Management System** that allows you to:
- Create separate cases for different investigations
- Upload multiple CSV files per case
- Keep each case's data isolated
- Track case history and statistics

## 🚀 How to Use

### 1. Starting the Application

Run the application:
```bash
python3 main.py
```

### 2. Case Selection Window

When you start the application, you'll see the **Case Selection Window** with:

- **List of existing cases** with details:
  - Case Name
  - Case Number
  - Investigating Officer
  - Created Date
  - Last Accessed Date
  - Status (Active/Closed/Archived)
  - Number of Records

- **Action Buttons**:
  - Create New Case
  - Open Selected Case
  - Delete Selected Case
  - Refresh

### 3. Creating a New Case

1. Click **"Create New Case"** button
2. Fill in the case details:
   - **Case Name*** (Required) - e.g., "Murder Investigation 2024"
   - **Case Number** (Optional) - e.g., "FIR-123/2024"
   - **Investigating Officer** (Optional) - e.g., "Inspector Sharma"
   - **Description** (Optional) - Brief case description
3. Click **"Create Case"**
4. The new case will appear in the list

### 4. Opening a Case

- **Double-click** on a case in the list, OR
- **Select** a case and click **"Open Selected Case"**

The main analysis window will open with the selected case's data.

### 5. Working with Cases

Once a case is opened:

#### Upload CSV Files
- Go to **File → Upload CSV** or click "Upload CSV File"
- Select your CDR CSV file
- The data will be added to this case's database
- You can upload **multiple CSV files** to the same case

#### Analyze Data
All analysis features work normally:
- **Search**: Find specific records
- **Groups**: Analyze patterns
- **Reports**: Generate statistics
- **Tower CDR**: Common/Uncommon analysis

#### Case Information
- The case name is displayed in the window title
- Home tab shows current case details

### 6. Managing Cases

#### Delete a Case
1. Select the case in Case Selection Window
2. Click **"Delete Selected Case"**
3. Confirm deletion
4. ⚠️ **Warning**: This will delete all data - cannot be undone!

#### View Case Statistics
In the Case Selection Window, you can see:
- Total number of records
- Last accessed date
- Case status

## 📁 File Structure

```
data/
├── cases.db              # Master database of all cases
├── case_Case1.db         # Database for "Case1"
├── case_Case2.db         # Database for "Case2"
└── ...
```

Each case has its own SQLite database file, keeping data completely isolated.

## 💡 Best Practices

1. **Descriptive Names**: Use clear case names like "Robbery_2024_01" instead of "Case1"
2. **Case Numbers**: Always include official case/FIR numbers for reference
3. **Multiple Uploads**: You can upload multiple CSV files to the same case - they'll all be merged
4. **Regular Backups**: Backup the entire `data/` folder regularly
5. **Case Status**: Update case status when investigation is complete

## 🔍 Example Workflow

```
1. Start Application
   ↓
2. Create Case: "Theft Case - FIR 456/2024"
   - Case Number: FIR 456/2024
   - Officer: Inspector Kumar
   ↓
3. Open the case
   ↓
4. Upload first CDR file (suspect's number)
   ↓
5. Analyze initial data
   ↓
6. Upload second CDR file (victim's number)
   ↓
7. Perform cross-analysis using Groups tab
   ↓
8. Generate reports
   ↓
9. Export findings to CSV
```

## ⚙️ Technical Details

- **Database**: SQLite (one per case)
- **Isolation**: Each case has completely separate data
- **Performance**: No impact on performance with multiple cases
- **Storage**: Each case database grows based on uploaded data

## 🆘 Troubleshooting

**Case list is empty:**
- This is normal on first run
- Create your first case to get started

**Cannot open case:**
- Check if database file exists in `data/` folder
- Try refreshing the case list

**Case already exists error:**
- Each case name must be unique
- Choose a different name or delete the existing case

## 📝 Notes

- Case databases are stored in the `data/` folder
- Each case maintains its own upload history
- You can work on multiple cases (one at a time)
- Last accessed date updates automatically when you open a case

---

**Need Help?** Contact the development team for support.
