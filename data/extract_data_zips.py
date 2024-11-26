# extract all zip files in directory data/ into subfolders of tsv data

import os
import zipfile

def extract_all_zip_files():
    current_directory = os.getcwd()
    files_in_directory = os.listdir(current_directory)
    zip_files = [file for file in files_in_directory if file.endswith('.zip')]
    if not zip_files:
        print("No .zip files found in the current directory.")
        return
    
    # Extract each .zip file
    for zip_file in zip_files:
        print(f"Processing '{zip_file}'...")
        try:
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                # Create a folder name from the zip file (without .zip extension)
                extract_folder = os.path.join(current_directory, os.path.splitext(zip_file)[0])
                if os.path.exists(extract_folder) and os.path.isdir(extract_folder):
                    continue
                else:
                    # Create directory if it doesn't exist
                    os.makedirs(extract_folder, exist_ok=True)
                    
                    # Extract all the contents into said folder
                    zip_ref.extractall(extract_folder)
                    print(f"Extracted '{zip_file}' to '{extract_folder}'")
        except zipfile.BadZipFile:
            print(f"Error: '{zip_file}' is not a valid zip file.")
        except PermissionError:
            print(f"Error: Permission denied while accessing '{zip_file}'.")

if __name__ == "__main__":
    os.chdir("../data")
    extract_all_zip_files()