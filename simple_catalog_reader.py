#!/usr/bin/env python3
"""
Simple Catalog Reader - Quick analysis of catalog structure
"""

import pandas as pd
import os

def analyze_catalog(file_path):
    """Analyze catalog file structure"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📁 Analyzing: {file_path}")
    print(f"📏 Size: {os.path.getsize(file_path):,} bytes")
    
    try:
        # Read Excel file
        excel_file = pd.ExcelFile(file_path)
        print(f"📋 Sheets: {len(excel_file.sheet_names)}")
        
        for sheet_name in excel_file.sheet_names:
            print(f"\n🔍 Sheet: {sheet_name}")
            
            # Read first few rows to understand structure
            df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=10)
            print(f"   📊 Rows (sample): {len(df)}")
            print(f"   📊 Columns: {len(df.columns)}")
            
            # Show column names
            print("   📝 Columns:")
            for i, col in enumerate(df.columns):
                print(f"      {i}: {col}")
            
            # Show first few rows of data
            print("   📋 First 5 rows:")
            for idx, row in df.head(5).iterrows():
                print(f"      Row {idx}: {list(row)[:5]}...")  # First 5 columns only
            
            # Check if this might be the new format
            required_cols = ['item', 'category', 'units', 'cost', 'manager_approve', 'comments']
            found_cols = [col for col in required_cols if col in df.columns]
            
            if found_cols:
                print(f"   ✅ Found required columns: {found_cols}")
            else:
                print("   ⚠️  No required columns found in header row")
                print("   💡 Checking if data starts from different row...")
                
                # Check first 5 rows for potential headers
                for check_row in range(min(5, len(df))):
                    row_values = [str(val).lower().strip() for val in df.iloc[check_row] if pd.notna(val)]
                    matches = [col for col in required_cols if col in row_values]
                    if matches:
                        print(f"      Row {check_row} might be headers: {matches}")
                        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    catalog_path = r"C:\Users\koren.vaknin\Desktop\filles\develop\Panel\catalog.xlsx"
    analyze_catalog(catalog_path) 