import pandas as pd
from typing import List, Dict, Tuple
from config import L1_CATEGORIES

class CutGenerator:
    """Generates all 8 TDW cuts."""
    
    def __init__(self, df: pd.DataFrame, l1_column: str, l2_column: str, 
                 demo1: str, demo2: str, demo3: str):
        self.df = df.copy()
        self.l1_column = l1_column
        self.l2_column = l2_column
        self.demo1 = demo1
        self.demo2 = demo2
        self.demo3 = demo3
        self.cuts = {}
        
    def generate_all_cuts(self) -> Dict:
        """Generate all 8 cuts."""
        self.cuts['cut1'] = self._generate_demographic_cut(self.demo1)
        self.cuts['cut2'] = self._generate_demographic_cut(self.demo2)
        self.cuts['cut3'] = self._generate_demographic_cut(self.demo3)
        self.cuts['cut4'] = self._generate_l1_split()
        self.cuts['cut5'] = self._generate_l2_vs_l1()
        self.cuts['cut6'] = self._generate_l1_vs_demographic(self.demo1)
        self.cuts['cut7'] = self._generate_l1_vs_demographic(self.demo2)
        self.cuts['cut8'] = self._generate_l1_vs_demographic(self.demo3)
        return self.cuts
    
    def _generate_demographic_cut(self, column: str) -> Dict:
        """Generate a demographic summary cut (Cuts 1-3)."""
        # Count by category
        counts = self.df[column].value_counts()
        
        # Separate blanks and non-blanks
        non_blank = counts[counts.index.notna()]
        blank_count = counts.get('', 0) + counts.get(None, 0)
        
        # Sort non-blank descending
        non_blank = non_blank.sort_values(ascending=False)
        
        # Build result
        categories = non_blank.index.tolist()
        values = non_blank.values.tolist()
        
        # Add blank at the end if exists
        if blank_count > 0:
            categories.append('(Blank)')
            values.append(blank_count)
        
        return {
            'title': f'Cut - {column}',
            'column_name': column,
            'categories': categories,
            'values': values,
            'total': sum(values),
            'is_demographic': True
        }
    
    def _generate_l1_split(self) -> Dict:
        """Generate L1 split (Cut 4)."""
        counts = self.df[self.l1_column].value_counts()
        
        # Ensure all L1 categories exist (even if count is 0)
        values = []
        for cat in L1_CATEGORIES:
            values.append(int(counts.get(cat, 0)))
        
        return {
            'title': 'Cut - L1 Split',
            'column_name': 'L1 Category',
            'categories': L1_CATEGORIES.copy(),
            'values': values,
            'total': sum(values),
            'is_demographic': True
        }
    
    def _generate_l2_vs_l1(self) -> Dict:
        """Generate L2 vs L1 cross cut (Cut 5)."""
        # Create L2 full string (L1 | L2)
        self.df['L2_Full'] = self.df[self.l1_column] + ' | ' + self.df[self.l2_column]
        
        # Pivot table
        pivot = self.df.groupby(['L2_Full', self.l1_column]).size().unstack(fill_value=0)
        
        # Ensure all L1 columns exist
        for cat in L1_CATEGORIES:
            if cat not in pivot.columns:
                pivot[cat] = 0
        
        # Reorder columns
        pivot = pivot[L1_CATEGORIES]
        
        # Sort rows by total count descending
        pivot['Total'] = pivot.sum(axis=1)
        pivot = pivot.sort_values('Total', ascending=False)
        pivot = pivot.drop('Total', axis=1)
        
        return {
            'title': 'Cut - L2 vs L1 Cross Cut',
            'rows': pivot.index.tolist(),
            'columns': L1_CATEGORIES.copy(),
            'data': pivot.values.tolist(),
            'total': int(pivot.values.sum()),
            'is_demographic': False
        }
    
    def _generate_l1_vs_demographic(self, demo_column: str) -> Dict:
        """Generate L1 vs Demographic cross cut (Cuts 6-8)."""
        # Pivot table
        pivot = self.df.groupby([self.l1_column, demo_column]).size().unstack(fill_value=0)
        
        # Ensure all L1 rows exist
        for cat in L1_CATEGORIES:
            if cat not in pivot.index:
                pivot.loc[cat] = 0
        
        # Reorder rows
        pivot = pivot.reindex(L1_CATEGORIES)
        
        # Handle columns: sort by total count descending, move blanks to end
        col_totals = pivot.sum()
        
        # Separate blank and non-blank columns
        non_blank_cols = []
        blank_cols = []
        for col in col_totals.index:
            if col == '' or col is None or str(col).lower() == 'nan':
                blank_cols.append(col)
            else:
                non_blank_cols.append(col)
        
        # Sort non-blank by total descending
        non_blank_totals = col_totals[non_blank_cols].sort_values(ascending=False)
        sorted_cols = non_blank_totals.index.tolist() + blank_cols
        
        # Reorder columns
        pivot = pivot[sorted_cols]
        
        # Rename blank column
        new_columns = []
        for col in pivot.columns:
            if col == '' or col is None or str(col).lower() == 'nan':
                new_columns.append('(Blank)')
            else:
                new_columns.append(str(col))
        
        return {
            'title': f'Cut - L1 vs {demo_column}',
            'rows': L1_CATEGORIES.copy(),
            'columns': new_columns,
            'data': pivot.values.tolist(),
            'total': int(pivot.values.sum()),
            'is_demographic': False
        }
    
    def get_cuts(self) -> Dict:
        """Get all generated cuts."""
        return self.cuts