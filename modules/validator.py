import pandas as pd
from typing import List, Dict, Tuple, Optional
import os

class DataValidator:
    """Validates uploaded Excel files and suggests fixes."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.issues = []
        self.warnings = []
        self.df = None
        self.sheet_name = None
        
    def validate_file(self) -> Tuple[bool, List[Dict]]:
        """Validate file format and basic properties."""
        # Check file exists
        if not os.path.exists(self.file_path):
            return False, [{'type': 'error', 'message': 'File not found'}]
        
        # Check file size
        size = os.path.getsize(self.file_path)
        if size > 16 * 1024 * 1024:
            return False, [{'type': 'error', 'message': 'File too large (max 16MB)'}]
        
        # Check extension
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext not in ['.xlsx', '.xls']:
            return False, [{'type': 'error', 'message': 'Invalid file type. Use .xlsx or .xls'}]
        
        # Try to read
        try:
            xl = pd.ExcelFile(self.file_path)
            if len(xl.sheet_names) == 0:
                return False, [{'type': 'error', 'message': 'Excel file has no sheets'}]
            return True, []
        except Exception as e:
            return False, [{'type': 'error', 'message': f'Cannot read Excel file: {str(e)}'}]
    
    def validate_sheet(self, sheet_name: str) -> Tuple[bool, List[Dict]]:
        """Validate selected sheet."""
        try:
            self.df = pd.read_excel(self.file_path, sheet_name=sheet_name)
            self.sheet_name = sheet_name
            
            issues = []
            
            # Check if empty
            if len(self.df) == 0:
                issues.append({
                    'type': 'error',
                    'message': 'Sheet is empty (no data rows)',
                    'auto_fixable': False
                })
                return False, issues
            
            # Check minimum rows
            if len(self.df) < 2:
                issues.append({
                    'type': 'warning',
                    'message': f'Only {len(self.df)} data row(s). Minimum recommended: 10',
                    'auto_fixable': False
                })
            
            # Check minimum columns
            if len(self.df.columns) < 3:
                issues.append({
                    'type': 'error',
                    'message': f'Only {len(self.df.columns)} columns. Minimum required: 3',
                    'auto_fixable': False
                })
                return False, issues
            
            # Check for empty rows at bottom
            empty_rows = self._count_empty_rows()
            if empty_rows > 0:
                issues.append({
                    'type': 'warning',
                    'message': f'{empty_rows} empty row(s) at bottom of sheet',
                    'auto_fixable': True,
                    'fix_action': 'remove_empty_rows'
                })
            
            # Check for completely empty columns
            empty_cols = self._count_empty_columns()
            if empty_cols > 0:
                issues.append({
                    'type': 'warning',
                    'message': f'{empty_cols} completely empty column(s)',
                    'auto_fixable': True,
                    'fix_action': 'remove_empty_columns'
                })
            
            # Check for duplicate rows
            dupes = self.df.duplicated().sum()
            if dupes > 0:
                issues.append({
                    'type': 'warning',
                    'message': f'{dupes} duplicate row(s) found',
                    'auto_fixable': True,
                    'fix_action': 'remove_duplicates'
                })
            
            # Check for leading/trailing spaces in headers
            spaced_headers = self._check_header_spaces()
            if spaced_headers:
                issues.append({
                    'type': 'warning',
                    'message': f'{len(spaced_headers)} column header(s) have leading/trailing spaces',
                    'auto_fixable': True,
                    'fix_action': 'trim_headers',
                    'details': spaced_headers
                })
            
            self.issues = issues
            return len([i for i in issues if i['type'] == 'error']) == 0, issues
            
        except Exception as e:
            return False, [{'type': 'error', 'message': f'Error reading sheet: {str(e)}'}]
    
    def validate_columns(self, l2_column: str, demo_columns: List[str]) -> Tuple[bool, List[Dict]]:
        """Validate selected columns."""
        if self.df is None:
            return False, [{'type': 'error', 'message': 'No sheet loaded'}]
        
        issues = []
        
        # Check L2 column exists
        if l2_column not in self.df.columns:
            issues.append({
                'type': 'error',
                'message': f'L2 Classification column "{l2_column}" not found',
                'auto_fixable': False
            })
            return False, issues
        
        # Check demographic columns exist
        for col in demo_columns:
            if col not in self.df.columns:
                issues.append({
                    'type': 'error',
                    'message': f'Demographic column "{col}" not found',
                    'auto_fixable': False
                })
        
        if issues:
            return False, issues
        
        # Check L2 column has data
        l2_data = self.df[l2_column].dropna()
        if len(l2_data) == 0:
            issues.append({
                'type': 'error',
                'message': f'L2 Classification column "{l2_column}" is entirely empty',
                'auto_fixable': False
            })
            return False, issues
        
        # Check L2 format (should contain | in most rows)
        has_pipe = l2_data.astype(str).str.contains('\|').sum()
        pipe_pct = has_pipe / len(l2_data) * 100
        if pipe_pct < 50:
            issues.append({
                'type': 'warning',
                'message': f'Only {pipe_pct:.0f}% of L2 values contain "|" separator. Expected format: "L1 | L2"',
                'auto_fixable': False
            })
        
        # Check demographic column uniqueness
        for col in demo_columns:
            unique_count = self.df[col].nunique(dropna=True)
            if unique_count > 50:
                issues.append({
                    'type': 'warning',
                    'message': f'"{col}" has {unique_count} unique values. Recommended: < 10 for readable charts',
                    'auto_fixable': False
                })
            elif unique_count == 1:
                issues.append({
                    'type': 'warning',
                    'message': f'"{col}" has only 1 unique value. Not useful for analysis',
                    'auto_fixable': False
                })
        
        # Check for blanks in demographics
        for col in demo_columns:
            blank_count = self.df[col].isna().sum() + (self.df[col] == '').sum()
            if blank_count > 0:
                issues.append({
                    'type': 'info',
                    'message': f'"{col}" has {blank_count} blank value(s). Will show as "(Blank)"',
                    'auto_fixable': False
                })
        
        return True, issues
    
    def apply_fix(self, fix_action: str) -> pd.DataFrame:
        """Apply an auto-fix and return cleaned DataFrame."""
        if self.df is None:
            raise Exception('No data loaded')
        
        df_clean = self.df.copy()
        
        if fix_action == 'remove_empty_rows':
            # Remove rows where all values are NaN or empty
            df_clean = df_clean.dropna(how='all')
            df_clean = df_clean[~(df_clean.astype(str).apply(lambda x: x.str.strip()) == '').all(axis=1)]
        
        elif fix_action == 'remove_empty_columns':
            # Remove columns where all values are NaN
            df_clean = df_clean.dropna(axis=1, how='all')
        
        elif fix_action == 'remove_duplicates':
            df_clean = df_clean.drop_duplicates()
        
        elif fix_action == 'trim_headers':
            df_clean.columns = [str(col).strip() for col in df_clean.columns]
        
        elif fix_action == 'trim_all_strings':
            # Trim leading/trailing spaces from all string cells
            for col in df_clean.columns:
                if df_clean[col].dtype == 'object':
                    df_clean[col] = df_clean[col].astype(str).str.strip()
                    df_clean[col] = df_clean[col].replace('nan', pd.NA)
                    df_clean[col] = df_clean[col].replace('', pd.NA)
        
        self.df = df_clean
        return df_clean
    
    def get_dataframe(self) -> pd.DataFrame:
        """Get current DataFrame."""
        return self.df
    
    def _count_empty_rows(self) -> int:
        """Count empty rows at bottom."""
        if self.df is None:
            return 0
        empty = self.df.isna().all(axis=1)
        # Count trailing empty rows
        count = 0
        for i in range(len(empty) - 1, -1, -1):
            if empty.iloc[i]:
                count += 1
            else:
                break
        return count
    
    def _count_empty_columns(self) -> int:
        """Count completely empty columns."""
        if self.df is None:
            return 0
        return self.df.isna().all().sum()
    
    def _check_header_spaces(self) -> List[str]:
        """Check for headers with leading/trailing spaces."""
        spaced = []
        for col in self.df.columns:
            col_str = str(col)
            if col_str != col_str.strip():
                spaced.append(col_str)
        return spaced
    
    def get_preview(self, n_rows: int = 5) -> pd.DataFrame:
        """Get preview of data."""
        if self.df is None:
            return pd.DataFrame()
        return self.df.head(n_rows)