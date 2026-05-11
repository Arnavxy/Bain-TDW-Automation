import pandas as pd
from typing import List, Tuple, Optional
import os

class DataLoader:
    """Handles Excel file loading and sheet detection."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sheets = []
        self.current_sheet = None
        self.df = None
        
    def get_sheet_names(self) -> List[str]:
        """Get all sheet names from the Excel file."""
        try:
            xl = pd.ExcelFile(self.file_path)
            self.sheets = xl.sheet_names
            return self.sheets
        except Exception as e:
            raise Exception(f"Error reading Excel file: {str(e)}")
    
    def load_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Load a specific sheet into a DataFrame."""
        try:
            self.df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            self.current_sheet = sheet_name
            return self.df
        except Exception as e:
            raise Exception(f"Error loading sheet '{sheet_name}': {str(e)}")
    
    def get_columns(self) -> List[str]:
        """Get all column names from the loaded DataFrame."""
        if self.df is None:
            raise Exception("No sheet loaded. Call load_sheet() first.")
        return list(self.df.columns)
    
    def get_preview(self, n_rows: int = 5) -> pd.DataFrame:
        """Get first n rows for preview."""
        if self.df is None:
            raise Exception("No sheet loaded.")
        return self.df.head(n_rows)
    
    def get_shape(self) -> Tuple[int, int]:
        """Get DataFrame shape (rows, cols)."""
        if self.df is None:
            return (0, 0)
        return self.df.shape
    
    def get_unique_values(self, column: str) -> List:
        """Get unique values in a column."""
        if self.df is None:
            raise Exception("No sheet loaded.")
        if column not in self.df.columns:
            raise Exception(f"Column '{column}' not found.")
        return sorted(self.df[column].dropna().unique().tolist())
    
    def get_unique_count(self, column: str) -> int:
        """Get count of unique values in a column."""
        if self.df is None:
            raise Exception("No sheet loaded.")
        if column not in self.df.columns:
            raise Exception(f"Column '{column}' not found.")
        return self.df[column].nunique(dropna=True)
    
    def validate_required_columns(self, l2_column: str) -> bool:
        """Validate that required columns exist."""
        if self.df is None:
            raise Exception("No sheet loaded.")
        if l2_column not in self.df.columns:
            raise Exception(f"L2 Classification column '{l2_column}' not found.")
        return True
    
    def cleanup(self):
        """Remove uploaded file after processing."""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
        except:
            pass