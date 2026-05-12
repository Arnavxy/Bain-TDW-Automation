# TDW Cuts Automation Tool - Configuration

# Bain Brand Colors
BAIN_RED = '#CC0000'
BAIN_RED_DARK = '#990000'
BAIN_DARK_GREY = '#333333'
BAIN_MEDIUM_GREY = '#808080'
BAIN_LIGHT_GREY = '#F5F5F5'
BAIN_WHITE = '#FFFFFF'
BAIN_BORDER_GREY = '#E0E0E0'

# L1 Categories (fixed order)
L1_CATEGORIES = ['Doers', 'Watchers', 'Thinkers', 'Admin']

# L1 Color coding for charts (optional)
L1_COLORS = {
    'Doers': '#CC0000',
    'Watchers': '#808080',
    'Thinkers': '#333333',
    'Admin': '#E0E0E0'
}

# Excel Formatting
TITLE_FONT = 'Calibri'
TITLE_SIZE = 12
TITLE_BOLD = True

HEADER_FONT = 'Calibri'
HEADER_SIZE = 11
HEADER_BOLD = True

DATA_FONT = 'Calibri'
DATA_SIZE = 11

# Grey italic for categories in cuts 1-3
CATEGORY_FONT = 'Calibri'
CATEGORY_SIZE = 11
CATEGORY_ITALIC = True
CATEGORY_COLOR = '808080'  # Grey

# Block spacing in Excel
BLOCK_GAP_ROWS = 2

# Upload settings
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
UPLOAD_FOLDER = 'uploads'

# App settings
APP_NAME = 'TDW Cuts Automation Tool'
APP_VERSION = '1.0.0'
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'tdw-automation-secret-key-2024')