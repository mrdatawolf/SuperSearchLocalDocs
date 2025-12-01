import sqlite3

db_path = r"C:\Users\patrick\DocumentSearch\databases\db_4248340a6fc5.sqlite3"

print("Checking if folder_path or file_name is mixed into content...\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get a few documents with their folder paths and content
cursor.execute("""
    SELECT file_name, folder_path, content
    FROM documents
    WHERE LENGTH(content) > 100
    LIMIT 5
""")

documents = cursor.fetchall()

for i, (file_name, folder_path, content) in enumerate(documents, 1):
    print(f"Document {i}:")
    print(f"  File: {file_name}")
    print(f"  Folder: {folder_path}")
    print(f"  Content preview (first 200 chars):")
    print(f"    {content[:200]}...")

    # Check if folder path words appear in content
    folder_words = set(folder_path.lower().split())
    content_lower = content.lower()

    # Check for exact folder path in content
    if folder_path.lower() in content_lower:
        print("  ⚠️  WARNING: Exact folder path found in content!")

    print()

conn.close()

print("\nConclusion:")
print("If folder paths appear in 'Content preview', then paths are being indexed.")
print("If not, then words like 'biztech' are just common words in your documents.")
