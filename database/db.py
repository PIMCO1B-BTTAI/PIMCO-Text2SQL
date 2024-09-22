from pathlib import Path
from pprint import pprint
import sqlite3
import os
import csv

# Creates directory for writing files to Drive
btt_pimco_sql_directory = Path("~/Google Drive/Shared drives/PIMCO 1B/Database/").expanduser()
btt_pimco_sql_directory.mkdir(parents=True, exist_ok=True)

# Folders containing raw NPORT data
folders = [
    Path("~/Google Drive/Shared drives/PIMCO 1B/Raw Data/2024q2_nport/").expanduser(),
    Path("~/Google Drive/Shared drives/PIMCO 1B/Raw Data/2024q1_nport/").expanduser(),
    Path("~/Google Drive/Shared drives/PIMCO 1B/Raw Data/2023q4_nport/").expanduser(),
    Path("~/Google Drive/Shared drives/PIMCO 1B/Raw Data/2023q3_nport/").expanduser(),
    Path("~/Google Drive/Shared drives/PIMCO 1B/Raw Data/2023q2_nport/").expanduser(),
    Path("~/Google Drive/Shared drives/PIMCO 1B/Raw Data/2023q1_nport/").expanduser()
]

# Connect to SQLite database
conn = sqlite3.connect(btt_pimco_sql_directory / 'nport_2023_24.sqlite')
cursor = conn.cursor()

# Creates db file for NPORT datasets (first 10000 lines of data)
for folder in folders:
    if folder.exists() and folder.is_dir():
        folder_name = folder.name

        for filename in os.listdir(folder):
            if filename.endswith('.tsv'):
                orig_table_name = os.path.splitext(filename)[0]
                table_name = f"_{folder_name}_{orig_table_name}"

                file_path = folder / filename

                # Read the TSV file and determine table schema
                with open(file_path, 'r') as file:
                    reader = csv.reader(file, delimiter='\t')
                    column_names = next(reader)

                    # Create table with columns based on column names
                    create_table = f"CREATE TABLE IF NOT EXISTS {table_name} ("
                    create_table += ', '.join([f"{name} TEXT" for name in column_names])
                    create_table += ");"

                    cursor.execute(create_table)

                    # Import data into the table
                    insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({', '.join(['?']*len(column_names))})"

                    line_count = 0

                    for row in reader:
                        if line_count < 10000:
                            cursor.execute(insert_query, row)
                            line_count += 1
                        else:
                            break 

                print(f"Imported {filename} into table {table_name}")

conn.commit()

cursor.execute("SELECT * FROM _2023q1_nport_EXPLANATORY_NOTE")
nport_from_db = cursor.fetchall()

for data in nport_from_db:
    print(data)


