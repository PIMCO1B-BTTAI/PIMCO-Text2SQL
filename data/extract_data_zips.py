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
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            # Create a folder name from the zip file (without .zip extension)
            extract_folder = os.path.join(current_directory, os.path.splitext(zip_file)[0])
            # Check if there is existing folder with that name
            if os.path.isdir(extract_folder):
                print(f"The folder '{extract_folder}' already exists in the current working directory.")
            else:
                # Extract all the contents into said folder
                zip_ref.extractall(extract_folder)
                print(f"Extracted {zip_file} to {extract_folder}")

if __name__ == "__main__":
    extract_all_zip_files()