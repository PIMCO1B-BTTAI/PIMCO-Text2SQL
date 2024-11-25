# deletes all tsv files in PIMCO-TEXT2SQL/data/
# this should be run in PIMCO-Text2SQL folder
import os
os.chdir("data")
directory = os.getcwd()
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    if filename.endswith(".tsv") and os.path.isfile(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")