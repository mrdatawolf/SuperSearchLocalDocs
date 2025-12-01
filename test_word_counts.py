"""
Test script to verify word_counts rebuild functionality
Creates a test database with known content and verifies word counts are accurate
"""
import sqlite3
import os
import sys
from pathlib import Path

# Add current directory to path to import indexer
sys.path.insert(0, str(Path(__file__).parent))

from indexer import DocumentIndexer

# Test database path
TEST_DB = "test_word_counts.db"
TEST_FOLDER = "test_documents"

def cleanup():
    """Remove test files if they exist"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    if os.path.exists(f"{TEST_DB}-wal"):
        os.remove(f"{TEST_DB}-wal")
    if os.path.exists(f"{TEST_DB}-shm"):
        os.remove(f"{TEST_DB}-shm")

def create_test_database():
    """Create a test database with known content"""
    print("Creating test database with known content...")

    cleanup()

    # Create database
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            file_path TEXT PRIMARY KEY,
            file_name TEXT,
            file_type TEXT,
            file_size INTEGER,
            modified_date TEXT,
            content TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_counts (
            word TEXT PRIMARY KEY,
            count INTEGER NOT NULL DEFAULT 0
        )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word_count ON word_counts(count DESC)')

    # Insert test documents with KNOWN content
    test_docs = [
        {
            'file_path': 'C:\\test\\doc1.txt',
            'file_name': 'doc1.txt',
            'file_type': 'Text File',
            'file_size': 100,
            'modified_date': '2024-01-01',
            'content': 'axisnvr appears here once. This is document one with some test content.'
        },
        {
            'file_path': 'C:\\test\\doc2.txt',
            'file_name': 'doc2.txt',
            'file_type': 'Text File',
            'file_size': 120,
            'modified_date': '2024-01-02',
            'content': 'axisnvr appears here once again. This is document two with different content.'
        },
        {
            'file_path': 'C:\\test\\doc3.txt',
            'file_name': 'doc3.txt',
            'file_type': 'Text File',
            'file_size': 110,
            'modified_date': '2024-01-03',
            'content': 'axisnvr axisnvr axisnvr appears three times here. Document three has unique text.'
        },
        {
            'file_path': 'C:\\test\\doc4.txt',
            'file_name': 'doc4.txt',
            'file_type': 'Text File',
            'file_size': 90,
            'modified_date': '2024-01-04',
            'content': 'This document has the word testing testing testing multiple times for verification.'
        },
        {
            'file_path': 'C:\\test\\doc5.txt',
            'file_name': 'doc5.txt',
            'file_type': 'Text File',
            'file_size': 80,
            'modified_date': '2024-01-05',
            'content': 'Final document with unique uniqueword that appears only once in the entire database.'
        }
    ]

    for doc in test_docs:
        cursor.execute('''
            INSERT INTO documents (file_path, file_name, file_type, file_size, modified_date, content)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (doc['file_path'], doc['file_name'], doc['file_type'],
              doc['file_size'], doc['modified_date'], doc['content']))

    conn.commit()
    conn.close()

    print(f"[OK] Created test database with {len(test_docs)} documents")
    return test_docs

def verify_word_counts(test_docs):
    """Verify word counts are accurate"""
    print("\nVerifying word counts...")

    # Expected word counts (manually calculated)
    expected_counts = {
        'axisnvr': 5,        # 1 + 1 + 3 = 5 total occurrences
        'testing': 3,        # 3 occurrences in doc4
        'uniqueword': 1,     # 1 occurrence in doc5
        'document': 5,       # appears in all 5 docs (once each)
        'appears': 4,        # docs 1, 2, 3, 5
        'content': 2,        # docs 1, 2
    }

    # Connect and check
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()

    # Get actual counts
    cursor.execute("SELECT COUNT(*) FROM word_counts")
    total_words = cursor.fetchone()[0]
    print(f"  Total unique words in table: {total_words}")

    all_passed = True

    for word, expected_count in expected_counts.items():
        cursor.execute("SELECT count FROM word_counts WHERE word = ?", (word,))
        result = cursor.fetchone()

        if result:
            actual_count = result[0]
            status = "[PASS]" if actual_count == expected_count else "[FAIL]"

            if actual_count != expected_count:
                all_passed = False
                print(f"  {status} '{word}': expected {expected_count}, got {actual_count}")
            else:
                print(f"  {status} '{word}': {actual_count} (correct)")
        else:
            all_passed = False
            print(f"  [FAIL] '{word}': NOT FOUND in word_counts table")

    # Check for impossible counts (more occurrences than total documents)
    cursor.execute("""
        SELECT word, count FROM word_counts
        WHERE count > (SELECT COUNT(*) FROM documents)
        LIMIT 10
    """)

    impossible = cursor.fetchall()
    if impossible:
        all_passed = False
        print("\n  [ERROR] FOUND IMPOSSIBLE WORD COUNTS (count > total documents):")
        for word, count in impossible:
            print(f"     '{word}': {count} (only {len(test_docs)} documents exist!)")

    # Check for duplicate entries (shouldn't happen with PRIMARY KEY, but verify)
    cursor.execute("""
        SELECT word, COUNT(*) as cnt
        FROM word_counts
        GROUP BY word
        HAVING cnt > 1
    """)

    duplicates = cursor.fetchall()
    if duplicates:
        all_passed = False
        print("\n  [ERROR] FOUND DUPLICATE WORD ENTRIES:")
        for word, count in duplicates:
            print(f"     '{word}' appears {count} times in word_counts table")

    # Show top 10 words for manual verification
    print("\n  Top 10 words by count:")
    cursor.execute("SELECT word, count FROM word_counts ORDER BY count DESC LIMIT 10")
    for word, count in cursor.fetchall():
        print(f"     {word}: {count}")

    conn.close()

    return all_passed

def run_test():
    """Run the complete test"""
    print("=" * 80)
    print("WORD COUNTS REBUILD TEST")
    print("=" * 80)
    print()

    try:
        # Step 1: Create test database
        test_docs = create_test_database()

        # Step 2: Run rebuild_word_counts
        print("\nRunning rebuild_word_counts()...")
        indexer = DocumentIndexer(document_path=TEST_FOLDER, db_path=TEST_DB)
        indexer.rebuild_word_counts()

        # Step 3: Verify counts
        all_passed = verify_word_counts(test_docs)

        # Results
        print()
        print("=" * 80)
        if all_passed:
            print("[PASS] TEST PASSED - All word counts are accurate!")
            print("=" * 80)
            print()
            print("The rebuild_word_counts() function is working correctly.")
            print("It is safe to use on your production database.")
        else:
            print("[FAIL] TEST FAILED - Word counts are incorrect!")
            print("=" * 80)
            print()
            print("There is still a bug in the rebuild_word_counts() function.")
            print("DO NOT use it on your production database yet.")
        print()

        # Cleanup
        print("Cleaning up test files...")
        cleanup()
        print("[OK] Test files removed")

        return all_passed

    except Exception as e:
        print(f"\n[ERROR] TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        cleanup()
        return False

if __name__ == '__main__':
    success = run_test()
    sys.exit(0 if success else 1)
