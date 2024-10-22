import sqlite3
import csv
import os

# Ensure the databases folder exists
os.makedirs('databases', exist_ok=True)

# Connect to the SQLite database named social_indicators.db
conn = sqlite3.connect('databases/social_indicators.db')
cursor = conn.cursor()


# Commit changes and close the connection
conn.commit()
conn.close()