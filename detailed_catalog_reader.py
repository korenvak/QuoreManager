#!/usr/bin/env python3
"""
Detailed Catalog Reader - Understand exact structure
"""

import pandas as pd
import os

def analyze_catalog_detailed(file_path):
    """Detailed analysis of catalog structure"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📁 Analyzing: {file_path}")
    print("=" * 80)
    
    try:
        excel_file = pd.ExcelFile(file_path)
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n📋 SHEET: {sheet_name}")
            print("-" * 50)
            
            # Read more rows to find the actual data structure
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, nrows=20)
            
            print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
            
            # Show all rows to understand the structure
            for idx, row in df.iterrows():
                non_empty_values = [str(val) for val in row if pd.notna(val) and str(val).strip() != '']
                if non_empty_values:  # Only show rows with data
                    print(f"Row {idx:2d}: {non_empty_values[:10]}")  # First 10 non-empty values
                    
                    # Check if this row contains the new format headers
                    row_lower = [str(val).lower().strip() for val in row if pd.notna(val)]
                    required_cols = ['item', 'category', 'units', 'cost', 'manager_approve', 'comments']
                    found_headers = [col for col in required_cols if col in row_lower]
                    
                    if found_headers:
                        print(f"    ✅ POTENTIAL HEADER ROW - Found: {found_headers}")
                        
                        # Show the full row to see all columns
                        print(f"    📝 Full row: {[str(val) for val in row if pd.notna(val)]}")
                        
                        # Now read from this row as header
                        try:
                            header_df = pd.read_excel(file_path, sheet_name=sheet_name, header=idx)
                            print(f"    📊 Using row {idx} as header:")
                            print(f"    📝 Columns: {list(header_df.columns)}")
                            
                            # Show first few data rows
                            print(f"    📋 First 3 data rows:")
                            for i, data_row in header_df.head(3).iterrows():
                                print(f"      {list(data_row)[:6]}...")  # First 6 columns
                                
                        except Exception as e:
                            print(f"    ⚠️  Error reading with header {idx}: {e}")
            
            print(f"\n📊 Sheet {sheet_name} summary:")
            print(f"   - Total rows examined: {len(df)}")
            print(f"   - Total columns: {df.shape[1]}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    catalog_path = r"C:\Users\koren.vaknin\Desktop\filles\develop\Panel\catalog.xlsx"
    analyze_catalog_detailed(catalog_path) 