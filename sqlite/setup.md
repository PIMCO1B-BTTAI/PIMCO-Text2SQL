# SQLite Setup

### Installation:
Below are instructions for installing SQLite on your local machine.

1. Navigate to the official SQLite download page (https://www.sqlite.org/download.html) and download the precompiled binaries for your operating system. Unzip the file.
2. (Optional) Move the sqlite3 binary to the /usr/local/bin/ directory for more convenient access.
`sudo mv /path/to/sqlite3/directory /usr/local/bin/`
3. Verify that the installation was successful.
`sqlite3 --version`

### Usage in VSCode:
Below are instructions for using SQLite within VSCode.

1. Run import_files.py:
`python import_files.py`
2. Open an SQLite shell to interact with the database. In your terminal:
`sqlite3 nport.db`
3. Test a query: `SELECT * FROM table_name LIMIT 10;`
4. Enter `.exit` to exit the SQLite shell.

Note: This will generate a large .db file that cannot be pushed to Github.

