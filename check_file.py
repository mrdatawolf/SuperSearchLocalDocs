import os
import sqlite3

# Check if the file exists
file_path = r"\\192.168.203.207\Shared Folders\Retired\NetDocOld\2020\Network doc\Steve Morris.xlsx"
print(f"Checking file: {file_path}")
print(f"File exists: {os.path.exists(file_path)}")

# Check if Retired folder exists
retired_path = r"\\192.168.203.207\Shared Folders\Retired"
print(f"\nRetired folder exists: {os.path.exists(retired_path)}")

# Check what's actually in the database
db_path = r"C:\Users\patrick\DocumentSearch\databases\db_4248340a6fc5.sqlite3"
print(f"\nQuerying database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get total count
cursor.execute("SELECT COUNT(*) FROM documents")
total = cursor.fetchone()[0]
print(f"Total documents: {total}")

# Search for any .xlsx files with "Morris" in the name
cursor.execute("SELECT file_name, file_path, folder_path FROM documents WHERE file_name LIKE '%Morris%'")
results = cursor.fetchall()
print(f"\nFiles with 'Morris' in name: {len(results)}")
for r in results:
    print(f"  {r[0]}")
    print(f"    Path: {r[1]}")
    print(f"    Folder: {r[2]}")

# Check what the deepest folders are (to see indexing depth)
cursor.execute("""
    SELECT folder_path, COUNT(*) as cnt
    FROM documents
    WHERE folder_path LIKE '%NetDoc%' OR folder_path LIKE '%2020%'
    GROUP BY folder_path
    LIMIT 10
""")
results = cursor.fetchall()
print(f"\nFolders containing 'NetDoc' or '2020': {len(results)}")
for r in results:
    print(f"  {r[0]} ({r[1]} files)")

conn.close()
