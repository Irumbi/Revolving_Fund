import sqlite3
import pandas as pd
import os
import time

# Database path
db_path = r"C:\Users\lenovo\OneDrive\Desktop\basics c_part 1\Basic Python\Revolving_Fund.db"
# Excel file path
agents_data_file = r"C:\Users\lenovo\OneDrive\Desktop\basics c_part 1\Basic Python\Excel Files\Commissions.xlsx"

# Create the table commission in SQLite
def create_commission_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create the commission table, now including Agent_Image
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS commission (
        Agent_Code TEXT,
        Tel_No TEXT,
        KRA_PIN TEXT,
        Email_Address TEXT,
        Agent_Name TEXT,
        Amount REAL,
        Unit TEXT,
        Agency TEXT,
        Region TEXT,
        Month TEXT,
        Year INTEGER,
        Agent_Image BLOB,  -- Added the Agent_Image column to the table
        PRIMARY KEY (Agent_Code, Month, Year)  -- Ensure unique records for each agent per month
    )
    ''')

    conn.commit()
    conn.close()

# Initialize the database and create table
create_commission_table()

def load_excel_to_db():
    # Load the Excel file into a DataFrame
    agents_df = pd.read_excel(agents_data_file)

    # Clean up the column names and make sure data types are consistent
    agents_df.columns = agents_df.columns.str.strip()  # Strip spaces from column names
    agents_df['Agent_Code'] = agents_df['Agent_Code'].astype(str).str.strip()  # Strip spaces from Agent_Code
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Iterate over the rows in the DataFrame and insert/update the records in the commission table
    for _, row in agents_df.iterrows():
        cursor.execute('''
        REPLACE INTO commission (
            Agent_Code, Tel_No, KRA_PIN, Email_Address, Agent_Name, Amount, 
            Unit, Agency, Region, Month, Year, Agent_Image
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            row['Agent_Code'], row['Tel No'], row['KRA PIN'], row['Email Adress'], 
            row['Agent_Name'], row['Amount'], row['Unit'], row['Agency'], 
            row['Region'], row['Month'], row['Year'], row['Agent_Image']  # Ensure Agent_Image is added
        ))

    conn.commit()
    conn.close()

# Load data from Excel into the commission table
load_excel_to_db()

# Function to monitor Excel file for changes and reload data to database
def monitor_excel_for_changes():
    last_modified_time = os.path.getmtime(agents_data_file)

    while True:
        current_modified_time = os.path.getmtime(agents_data_file)

        if current_modified_time != last_modified_time:
            print("Excel file updated. Reloading data to database...")
            load_excel_to_db()  # Load the latest data to the database
            last_modified_time = current_modified_time

        time.sleep(60)  # Check every minute (adjust as needed)

# Start monitoring for changes
monitor_excel_for_changes()
