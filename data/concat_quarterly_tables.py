import os
import pandas as pd

# Path to the directory containing quarterly folders
directory_path = os.getcwd()
# Get the list of quarter folders
quarter_folders = [folder for folder in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, folder))]

# Process each table name across quarters and save as .tsv file
for table_name in list(os.listdir(os.path.join(directory_path, quarter_folders[0]))):
    if table_name.endswith(".tsv"):
        if os.path.isfile(table_name):
            print(f"The table '{table_name}' already exists in the current working directory.")
        else:
            if(table_name=="FUND_REPORTED_HOLDING.tsv") or (table_name=="IDENTIFIERS.tsv") or (table_name=="SECURITIES_LENDING.tsv"):
                print("Skipping '{table_name}' because we will run out of RAM due to its size")
                continue
            print("Saving table", table_name,"...")
            table_frames = []  # Temporary storage for chunks of the table across quarters

            # Loop through each quarter folder
            for quarter in quarter_folders:
                table_path = os.path.join(directory_path, quarter, table_name)

                if os.path.isfile(table_path):
                    # Process each table in chunks and append to table_frames
                    chunk_iter = pd.read_csv(table_path, sep='\t', chunksize=10000)

                    for chunk in chunk_iter:
                        table_frames.append(chunk)

            # Concatenate all chunks for this table
            table_df = pd.concat(table_frames, ignore_index=True)

            # Save concatenated data as a .tsv file in the current directory
            table_df.to_csv(table_name, sep='\t', index=False)
            print('Finished creating ',table_name)
            # Clear table_frames and table_df to free up memory
            del table_frames
            del table_df
    else:
        print(f"Skipping non-TSV file: {table_name}")
