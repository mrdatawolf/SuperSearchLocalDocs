"""Document indexer - Extracts text from documents and stores in SQLite database"""

import os
import sqlite3
from pathlib import Path
from datetime import datetime
import traceback

# Document parsing libraries
try:
    from docx import Document
except ImportError:
    Document = None

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    from openpyxl import load_workbook
except ImportError:
    load_workbook = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

from config import DOCUMENT_PATH, DATABASE_PATH, SUPPORTED_EXTENSIONS


class DocumentIndexer:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.document_path = DOCUMENT_PATH
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with FTS5 for full-text search"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        cursor = conn.cursor()

        # Create documents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                folder_path TEXT,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                modified_date TEXT,
                indexed_date TEXT NOT NULL,
                content TEXT
            )
        ''')

        # Create FTS5 virtual table for full-text search with multiple searchable columns
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                file_name,
                folder_path,
                content,
                content='documents',
                content_rowid='id'
            )
        ''')

        # Create triggers to keep FTS table in sync
        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, file_name, folder_path, content)
                VALUES (new.id, new.file_name, new.folder_path, new.content);
            END;
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                UPDATE documents_fts
                SET file_name = new.file_name,
                    folder_path = new.folder_path,
                    content = new.content
                WHERE rowid = new.id;
            END;
        ''')

        cursor.execute('''
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                DELETE FROM documents_fts WHERE rowid = old.id;
            END;
        ''')

        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")

    def extract_text_from_docx(self, file_path):
        """Extract text from DOCX files"""
        if Document is None:
            return "[python-docx not installed]"

        try:
            doc = Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return '\n'.join(text)
        except Exception as e:
            return f"[Error reading DOCX: {str(e)}]"

    def extract_text_from_csv(self, file_path):
        """Extract text from CSV files"""
        if pd is None:
            return "[pandas not installed]"

        try:
            df = pd.read_csv(file_path, encoding='utf-8', on_bad_lines='skip')
            return df.to_string()
        except Exception as e:
            try:
                df = pd.read_csv(file_path, encoding='latin-1', on_bad_lines='skip')
                return df.to_string()
            except:
                return f"[Error reading CSV: {str(e)}]"

    def extract_text_from_xlsx(self, file_path):
        """Extract text from XLSX files"""
        if load_workbook is None:
            return "[openpyxl not installed]"

        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)
            text = []
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                text.append(f"Sheet: {sheet_name}")
                for row in sheet.iter_rows(values_only=True):
                    row_text = ' | '.join([str(cell) if cell is not None else '' for cell in row])
                    if row_text.strip():
                        text.append(row_text)
            return '\n'.join(text)
        except Exception as e:
            return f"[Error reading XLSX: {str(e)}]"

    def extract_text_from_pdf(self, file_path):
        """Extract text from PDF files"""
        if PdfReader is None:
            return "[PyPDF2 not installed]"

        try:
            reader = PdfReader(file_path)
            text = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text.append(page_text)
            return '\n'.join(text)
        except Exception as e:
            return f"[Error reading PDF: {str(e)}]"

    def extract_text_from_image(self, file_path):
        """Extract text from images using OCR"""
        if Image is None or pytesseract is None:
            return "[Pillow or pytesseract not installed]"

        try:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text if text.strip() else "[No text found in image]"
        except Exception as e:
            return f"[Error reading image: {str(e)}]"

    def extract_text(self, file_path):
        """Extract text based on file extension"""
        ext = Path(file_path).suffix.lower()

        if ext == '.docx':
            return self.extract_text_from_docx(file_path)
        elif ext == '.csv':
            return self.extract_text_from_csv(file_path)
        elif ext == '.xlsx':
            return self.extract_text_from_xlsx(file_path)
        elif ext == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif']:
            return self.extract_text_from_image(file_path)
        else:
            return "[Unsupported file type]"

    def index_document(self, file_path):
        """Index a single document"""
        try:
            path = Path(file_path)

            # Get file metadata
            file_name = path.name
            file_type = SUPPORTED_EXTENSIONS.get(path.suffix.lower(), 'Unknown')
            file_size = path.stat().st_size
            modified_date = datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            indexed_date = datetime.now().isoformat()

            # Extract folder path (relative to document root, including all subfolders)
            try:
                folder_path = str(path.parent.relative_to(Path(self.document_path)))
                # Replace path separators with spaces for better searchability
                folder_path = folder_path.replace('\\', ' ').replace('/', ' ')
            except ValueError:
                # If path is not relative to document_path, use the full parent path
                folder_path = str(path.parent)

            # Extract text content
            content = self.extract_text(file_path)

            # Store in database with retry logic for locked database
            max_retries = 3
            retry_delay = 1

            for attempt in range(max_retries):
                try:
                    conn = sqlite3.connect(self.db_path, timeout=30.0)
                    cursor = conn.cursor()

                    # Check if document already exists
                    cursor.execute('SELECT id FROM documents WHERE file_path = ?', (str(file_path),))
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing document (trigger will update FTS)
                        doc_id = existing[0]
                        cursor.execute('''
                            UPDATE documents
                            SET file_name=?, folder_path=?, file_type=?, file_size=?, modified_date=?, indexed_date=?, content=?
                            WHERE id=?
                        ''', (file_name, folder_path, file_type, file_size, modified_date, indexed_date, content, doc_id))
                    else:
                        # Insert new document (trigger will insert into FTS)
                        cursor.execute('''
                            INSERT INTO documents (file_path, file_name, folder_path, file_type, file_size, modified_date, indexed_date, content)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (str(file_path), file_name, folder_path, file_type, file_size, modified_date, indexed_date, content))

                    conn.commit()
                    conn.close()

                    return True, f"Indexed: {file_name}"

                except sqlite3.OperationalError as e:
                    if "locked" in str(e).lower() and attempt < max_retries - 1:
                        # Database is locked, retry after delay
                        import time
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise

        except Exception as e:
            return False, f"Error indexing {file_path}: {str(e)}"

    def scan_and_index(self):
        """Scan document folder and index all supported files"""
        print(f"Scanning documents in: {self.document_path}")
        print("-" * 80)

        if not os.path.exists(self.document_path):
            print(f"ERROR: Path does not exist: {self.document_path}")
            return

        indexed_count = 0
        error_count = 0

        # Walk through all directories
        for root, dirs, files in os.walk(self.document_path):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    success, message = self.index_document(file_path)

                    if success:
                        indexed_count += 1
                        print(f"✓ {message}")
                    else:
                        error_count += 1
                        print(f"✗ {message}")

        print("-" * 80)
        print(f"Indexing complete!")
        print(f"Successfully indexed: {indexed_count} documents")
        print(f"Errors: {error_count}")

    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM documents')
        total_docs = cursor.fetchone()[0]

        cursor.execute('SELECT file_type, COUNT(*) FROM documents GROUP BY file_type')
        by_type = cursor.fetchall()

        conn.close()

        print("\nDatabase Statistics:")
        print(f"Total documents: {total_docs}")
        print("\nBy file type:")
        for file_type, count in by_type:
            print(f"  {file_type}: {count}")


if __name__ == '__main__':
    print("=" * 80)
    print("Document Indexer")
    print("=" * 80)

    indexer = DocumentIndexer()
    indexer.scan_and_index()
    indexer.get_stats()
