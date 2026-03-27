"""
Run this script to export the SQLite database to CSV for Power BI.
Usage: python pipeline/export_to_powerbi.py
Power BI: Connect via "Get Data > Text/CSV" pointing to data/carbon_emissions.csv
"""
import sqlite3
import pandas as pd
import os

DB  = os.path.join(os.path.dirname(__file__), "..", "data", "carbon_data.db")
CSV = os.path.join(os.path.dirname(__file__), "..", "data", "carbon_emissions.csv")

conn = sqlite3.connect(DB)
df   = pd.read_sql_query("SELECT * FROM emissions", conn)
conn.close()

df.to_csv(CSV, index=False)
print(f"Exported {len(df)} rows to {CSV}")
