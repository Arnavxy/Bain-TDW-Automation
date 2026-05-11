# TDW Cuts Automation Tool

## What is this?

A simple web-based tool that **automatically generates Thinker/Doer/Watcher (TDW) analysis cuts** from your Excel roster data. No coding knowledge required - just upload your file, select columns, and download the formatted output.

## Who is this for?

**Bain consultants and analysts** who need to:
- Generate TDW demographic cuts for presentations
- Create cross-tabulations (L1 vs demographics, L2 vs L1)
- Export think-cell-ready Excel files with live formulas
- Save hours of manual Excel work

## What does it do?

Upload your roster data and the tool automatically creates **8 standardized cuts**:

1. **Demographic Cut 1** - Summary by your first chosen demographic (e.g., Management Level)
2. **Demographic Cut 2** - Summary by your second chosen demographic (e.g., Sub-Division)
3. **Demographic Cut 3** - Summary by your third chosen demographic (e.g., Location Type)
4. **L1 Split** - Overall Thinker/Doer/Watcher/Admin distribution
5. **L2 vs L1 Cross Cut** - Matrix showing L2 categories across L1 types
6. **L1 vs Demographic 1** - L1 distribution across first demographic
7. **L1 vs Demographic 2** - L1 distribution across second demographic
8. **L1 vs Demographic 3** - L1 distribution across third demographic

All cuts include **live Excel formulas** - click any cell to see how the number was calculated!

## Quick Start (5 minutes)

### Option 1: One-Click Setup (Recommended for Mac/Linux)

```bash
# 1. Download the project
git clone https://github.com/Arnavxy/Bain-TDW-Automation.git
cd Bain-TDW-Automation

# 2. Run setup (installs everything automatically)
./setup.sh

# 3. Start the app
./run.sh
```

### Option 2: One-Click Setup (Windows)

```cmd
# 1. Download the project
git clone https://github.com/Arnavxy/Bain-TDW-Automation.git
cd Bain-TDW-Automation

# 2. Run setup (installs everything automatically)
setup.bat

# 3. Start the app
run.bat
```

### Option 3: Manual Setup (Any OS)

**Step 1: Install Python**
- Download from [python.org](https://www.python.org/downloads/)
- **Important:** Check "Add Python to PATH" during installation

**Step 2: Download the project**
```bash
git clone https://github.com/Arnavxy/Bain-TDW-Automation.git
cd Bain-TDW-Automation
```

**Step 3: Install dependencies**
```bash
# Mac/Linux:
pip3 install -r requirements.txt

# Windows:
pip install -r requirements.txt
```

**Step 4: Run the app**
```bash
# Mac/Linux:
python3 app.py

# Windows:
python app.py
```

## How to Use

### 1. Open the Tool
After running the app, open your browser and go to:
```
http://127.0.0.1:5000
```

### 2. Upload Your Data
- Click "Upload Data"
- Drag and drop your Excel file (.xlsx or .xls)
- Select the sheet containing your roster data

### 3. Validate Your Data
The tool checks for common issues:
- Empty rows
- Missing data
- Duplicate entries
- Leading/trailing spaces

**You can choose to ignore or auto-fix each issue.**

### 4. Map Your Columns
Select:
- **L2 Classification Column**: The column containing values like "Doers | Dev/ Eng"
- **Demographic 1, 2, 3**: Any columns you want to analyze (e.g., Management Level, Sub-Division, Location Type)
- **Include Percentages** (optional): Adds percentage columns to cuts

### 5. Review Anomalies
The tool flags any rows with invalid or missing L1/L2 data:
- Automatically categorizes as "Unknown | Unknown"
- You can override the categorization
- Shows which rows need attention

### 6. Generate Cuts
Click "Generate Cuts" and wait for processing. The tool will:
- Parse L1/L2 classifications
- Generate all 8 cuts with formulas
- Format everything for think-cell

### 7. Download Results
- Preview all 8 cuts on the results page
- Click "Download Excel File" to get your formatted output
- The file opens in both **Excel** and **LibreOffice Calc**

## Output Format

The downloaded Excel file contains:

### Sheet 1: Raw_Data
- All your original columns
- Plus parsed columns: L1_Parsed, L2_Parsed, L2_Full
- Formatted as an Excel Table

### Sheet 2: TDW_Cuts
- All 8 cuts formatted as clean blocks
- **Live formulas** - click any cell to see the formula
- Works in both Excel and LibreOffice
- Ready to link to think-cell

## Example Workflow

**Before:** Manually creating 8+ pivot tables and cross-tabs (30-60 minutes)

**After:** 
1. Upload file (30 seconds)
2. Select columns (1 minute)
3. Generate cuts (10 seconds)
4. Download and link to think-cell (1 minute)

**Total time: ~3 minutes** vs 30-60 minutes manually

## Requirements

- **Python 3.8+** (download from [python.org](https://www.python.org/downloads/))
- **Excel** or **LibreOffice Calc** (to open downloaded files)
- **Web browser** (Chrome, Firefox, Safari, Edge)

## Data Format

Your Excel file should have:
- One row per employee
- An L2 Classification column with format: `L1 | L2` (e.g., "Doers | Dev/ Eng")
- At least 3 demographic columns for analysis
- Standard Excel format (.xlsx or .xls)

## Troubleshooting

### "Python not found"
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python` (Mac/Linux)

### "Permission denied" when running setup.sh
- Run: `chmod +x setup.sh run.sh`
- Then try again

### Formulas show #NAME? or Err:504
- This happens when opening in LibreOffice with structured table references
- The tool now uses cross-compatible A1-style references
- Both Excel and LibreOffice should work correctly

### Port already in use
- If you see "Address already in use", another app is using port 5000
- Kill the existing process or restart your computer

## Support

For issues or questions:
- Check the **User Guide** in the app (click "User Guide" in sidebar)
- Report issues on GitHub: [Issues page](https://github.com/Arnavxy/Bain-TDW-Automation/issues)
- Contact: [Your Email]

## License

This tool is for internal Bain & Company use.

## Credits

Built for Bain consultants to automate TDW analysis workflows.

---

**Ready to save time?** Start with [Quick Start](#quick-start-5-minutes) above!