
import os
directory = os.getcwd()
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if filename.endswith(".tsv") and os.path.isfile(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")