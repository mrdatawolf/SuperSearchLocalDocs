import sqlite3
import os

# Check word counts in the network share database
db_path = r"C:\Users\patrick\DocumentSearch\databases\db_4248340a6fc5.sqlite3"

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    exit()

print(f"Analyzing word sources in: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if word_counts table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='word_counts'")
has_word_counts = cursor.fetchone() is not None

if not has_word_counts:
    print("word_counts table doesn't exist yet. Need to rebuild word counts.")
    conn.close()
    exit()

# Get some sample high-count words
cursor.execute("""
    SELECT word, count
    FROM word_counts
    ORDER BY count DESC
    LIMIT 30
""")
top_words = cursor.fetchall()

print("Top 30 most common words in word_counts:")
print("=" * 60)
for word, count in top_words:
    print(f"  {word:30s} {count:>8,} occurrences")

print("\n" + "=" * 60)

# Check for folder/path-like words (words commonly in paths)
path_indicators = ['pbidata', 'netdoc', 'biztech', 'tools', 'shared', 'folders',
                   'retired', 'documents', 'desktop', 'users', 'patrick']

print("\nChecking for potential path words:")
print("=" * 60)
found_path_words = []
for indicator in path_indicators:
    cursor.execute("SELECT word, count FROM word_counts WHERE word = ?", (indicator,))
    result = cursor.fetchone()
    if result:
        found_path_words.append(result)
        print(f"  {result[0]:30s} {result[1]:>8,} occurrences")

if not found_path_words:
    print("  No obvious path-related words found!")
else:
    print(f"\nFound {len(found_path_words)} potential path words.")
    print("This might indicate file paths are being indexed.")

# Sample a document to see what's in content
print("\n" + "=" * 60)
print("Sample document content (first 500 chars):")
print("=" * 60)
cursor.execute("SELECT file_name, folder_path, content FROM documents WHERE LENGTH(content) > 100 LIMIT 1")
sample = cursor.fetchone()
if sample:
    print(f"File: {sample[0]}")
    print(f"Folder: {sample[1]}")
    print(f"Content preview: {sample[2][:500]}...")

conn.close()
