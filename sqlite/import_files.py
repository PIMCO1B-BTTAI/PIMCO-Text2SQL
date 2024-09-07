import os
import sqlite3
import csv

# Path to directory containing TSV files
tsv_directory = '/users/hannahzhang/Downloads/2024q2_nport'
# Path to SQLite database
db_path = 'nport.db'

def tsv_import(tsv_directory, db_path):
    connect = sqlite3.connect(db_path)
    cursor = connect.cursor()

    # Iterate over files in directory
    for filename in os.listdir(tsv_directory):
        if filename.endswith('.tsv'):
            table_name = os.path.splitext(filename)[0]
            file_path = os.path.join(tsv_directory, filename)

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
                
                for row in reader:
                    cursor.execute(insert_query, row)
            
            print(f"Imported {filename} into table {table_name}")

    connect.commit()
    connect.close()

tsv_import(tsv_directory, db_path)

