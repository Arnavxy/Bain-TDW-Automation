import pandas as pd
from typing import List, Dict, Tuple, Optional
from config import L1_CATEGORIES

class L1L2Parser:
    """Parses L1 and L2 from the classification column."""
    
    def __init__(self, df: pd.DataFrame, l2_column: str):
        self.df = df.copy()
        self.l2_column = l2_column
        self.anomalies = []
        self.l1_column = 'L1_Parsed'
        self.l2_parsed_column = 'L2_Parsed'
        
    def parse(self) -> pd.DataFrame:
        """Parse L1 and L2 from the classification column."""
        # Initialize parsed columns
        self.df[self.l1_column] = None
        self.df[self.l2_parsed_column] = None
        
        for idx, row in self.df.iterrows():
            l2_value = str(row[self.l2_column]) if pd.notna(row[self.l2_column]) else ''
            
            # Check for anomalies
            if not l2_value or l2_value.strip() == '' or l2_value.lower() == 'nan':
                self._flag_anomaly(idx, l2_value, 'Blank or missing value')
                self.df.at[idx, self.l1_column] = 'Unknown'
                self.df.at[idx, self.l2_parsed_column] = 'Unknown'
            elif '|' not in l2_value:
                self._flag_anomaly(idx, l2_value, 'Missing separator (|)')
                self.df.at[idx, self.l1_column] = 'Unknown'
                self.df.at[idx, self.l2_parsed_column] = 'Unknown'
            else:
                # Split on |
                parts = l2_value.split('|', 1)
                l1 = parts[0].strip()
                l2 = parts[1].strip() if len(parts) > 1 else 'Unknown'
                
                # Validate L1
                if l1 not in L1_CATEGORIES:
                    self._flag_anomaly(idx, l2_value, f'Invalid L1 category: {l1}')
                    l1 = 'Unknown'
                    l2 = 'Unknown'
                
                self.df.at[idx, self.l1_column] = l1
                self.df.at[idx, self.l2_parsed_column] = l2
        
        return self.df
    
    def _flag_anomaly(self, idx: int, original_value: str, reason: str):
        """Flag an anomalous row."""
        row_data = self.df.loc[idx].to_dict()
        self.anomalies.append({
            'row_index': idx,
            'row_number': idx + 2,  # Excel row number (1-based + header)
            'original_value': original_value,
            'reason': reason,
            'job_title': row_data.get('Job Title', ''),
            'job_profile': row_data.get('Job Profile', ''),
            'suggested_l1': 'Unknown',
            'suggested_l2': 'Unknown'
        })
    
    def get_anomalies(self) -> List[Dict]:
        """Get list of anomalies."""
        return self.anomalies
    
    def has_anomalies(self) -> bool:
        """Check if any anomalies were found."""
        return len(self.anomalies) > 0
    
    def update_anomaly(self, row_index: int, l1: str, l2: str):
        """Update an anomaly with user-provided values."""
        # Update the DataFrame
        self.df.at[row_index, self.l1_column] = l1
        self.df.at[row_index, self.l2_parsed_column] = l2
        
        # Update anomaly record
        for anomaly in self.anomalies:
            if anomaly['row_index'] == row_index:
                anomaly['suggested_l1'] = l1
                anomaly['suggested_l2'] = l2
                anomaly['reason'] += ' (User override)'
                break
    
    def get_l1_counts(self) -> Dict[str, int]:
        """Get counts of each L1 category."""
        if self.l1_column not in self.df.columns:
            raise Exception("L1 not parsed yet. Call parse() first.")
        return self.df[self.l1_column].value_counts().to_dict()
    
    def get_l2_counts(self) -> Dict[str, int]:
        """Get counts of each L2 category."""
        if self.l2_parsed_column not in self.df.columns:
            raise Exception("L2 not parsed yet. Call parse() first.")
        return self.df[self.l2_parsed_column].value_counts().to_dict()
    
    def get_parsed_df(self) -> pd.DataFrame:
        """Get the parsed DataFrame."""
        return self.df
    
    def get_l1_l2_combinations(self) -> pd.DataFrame:
        """Get all L1-L2 combinations."""
        if self.l1_column not in self.df.columns or self.l2_parsed_column not in self.df.columns:
            raise Exception("L1/L2 not parsed yet.")
        return self.df.groupby([self.l1_column, self.l2_parsed_column]).size().reset_index(name='Count')