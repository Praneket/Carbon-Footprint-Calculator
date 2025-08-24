import sqlite3
import pandas as pd

# Fetch data from DB
conn = sqlite3.connect("data/carbon_data.db")
df = pd.read_sql_query("SELECT * FROM emissions", conn)
conn.close()

# Save to CSV (Power BI will auto-refresh from this)
df.to_csv("data/carbon_emissions.csv", index=False)
