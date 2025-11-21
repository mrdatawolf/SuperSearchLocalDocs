"""Flask web server for document search"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
from pathlib import Path
from config import DATABASE_PATH, SERVER_HOST, SERVER_PORT
from company_abbreviations import get_company_abbreviations

app = Flask(__name__)

# Initialize company abbreviations
company_abbrev = None

@app.before_request
def initialize():
    """Initialize company abbreviations on first request"""
    global company_abbrev
    if company_abbrev is None:
        company_abbrev = get_company_abbreviations()


def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Serve the main search page"""
    return render_template('index.html')


@app.route('/api/search')
def search():
    """Search API endpoint with filtering support"""
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'results': [], 'count': 0, 'query': ''})

    # Get filter parameters
    file_types = request.args.get('fileTypes', '').split(',') if request.args.get('fileTypes') else []
    search_scope = request.args.get('scope', 'all')  # all, filenames, folders, content
    sort_by = request.args.get('sort', 'relevance')  # relevance, date, name, size
    date_from = request.args.get('dateFrom', '')
    date_to = request.args.get('dateTo', '')
    size_min = request.args.get('sizeMin', '')
    size_max = request.args.get('sizeMax', '')

    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))
    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    def escape_fts5_query(text):
        """Escape special characters for FTS5 queries"""
        # Escape double quotes by doubling them
        text = text.replace('"', '""')
        return text

    # Build FTS5 search query based on scope
    # Get alternative queries (with company abbreviation expansion)
    global company_abbrev
    query_alternatives = []

    if company_abbrev:
        query_alternatives = company_abbrev.get_search_alternatives(query)
    else:
        query_alternatives = [query]

    # Build FTS5 queries for each alternative
    fts_queries = []

    for alt_query in query_alternatives:
        # Split query into words for AND logic
        words = alt_query.split()

        if len(words) > 1:
            # Multi-word query: use AND logic to find documents with all words
            # Escape and quote each word to handle special characters
            if search_scope == 'filenames':
                escaped_words = [f'file_name: "{escape_fts5_query(word)}"*' for word in words]
                fts_query = '(' + ' AND '.join(escaped_words) + ')'
            elif search_scope == 'folders':
                escaped_words = [f'folder_path: "{escape_fts5_query(word)}"*' for word in words]
                fts_query = '(' + ' AND '.join(escaped_words) + ')'
            elif search_scope == 'content':
                escaped_words = [f'content: "{escape_fts5_query(word)}"*' for word in words]
                fts_query = '(' + ' AND '.join(escaped_words) + ')'
            else:  # all - search across all fields
                escaped_words = [f'"{escape_fts5_query(word)}"*' for word in words]
                fts_query = '(' + ' AND '.join(escaped_words) + ')'
        else:
            # Single word query: escape and quote to handle special characters
            escaped_query = escape_fts5_query(alt_query)
            if search_scope == 'filenames':
                fts_query = f'file_name: "{escaped_query}"*'
            elif search_scope == 'folders':
                fts_query = f'folder_path: "{escaped_query}"*'
            elif search_scope == 'content':
                fts_query = f'content: "{escaped_query}"*'
            else:  # all
                fts_query = f'"{escaped_query}"*'

        fts_queries.append(fts_query)

    # Combine all alternatives with OR logic
    search_query = ' OR '.join(fts_queries)

    try:
        # Build WHERE clause for filters
        where_clause = 'WHERE documents_fts MATCH ?'
        params = [search_query]

        # Add file type filter
        if file_types and file_types[0]:
            placeholders = ','.join('?' * len(file_types))
            where_clause += f' AND d.file_type IN ({placeholders})'
            params.extend(file_types)

        # Add date range filter
        if date_from:
            where_clause += ' AND d.modified_date >= ?'
            params.append(date_from)
        if date_to:
            where_clause += ' AND d.modified_date <= ?'
            params.append(date_to)

        # Add size filter
        if size_min:
            where_clause += ' AND d.file_size >= ?'
            params.append(int(size_min))
        if size_max:
            where_clause += ' AND d.file_size <= ?'
            params.append(int(size_max))

        # First, get the total count of matching documents
        count_sql = f'''
            SELECT COUNT(*)
            FROM documents_fts
            JOIN documents d ON documents_fts.rowid = d.id
            {where_clause}
        '''
        cursor.execute(count_sql, params)
        total_count = cursor.fetchone()[0]

        # Now get the actual results with limit
        sql = f'''
            SELECT
                d.id,
                d.file_name,
                d.file_path,
                d.folder_path,
                d.file_type,
                d.file_size,
                d.modified_date,
                d.indexed_date,
                snippet(documents_fts, -1, '<mark>', '</mark>', '...', 64) as snippet,
                rank
            FROM documents_fts
            JOIN documents d ON documents_fts.rowid = d.id
            {where_clause}
        '''

        # Add sorting
        if sort_by == 'date':
            sql += ' ORDER BY d.modified_date DESC'
        elif sort_by == 'name':
            sql += ' ORDER BY d.file_name ASC'
        elif sort_by == 'size':
            sql += ' ORDER BY d.file_size DESC'
        else:  # relevance (default)
            sql += ' ORDER BY rank'

        sql += ' LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        cursor.execute(sql, params)

        results = []
        for row in cursor.fetchall():
            # Build a smart snippet that shows where the match occurred
            snippet_text = row['snippet'] if row['snippet'] else ''

            # If snippet is empty or doesn't contain a mark, check if match was in filename or folder
            if not snippet_text or '<mark>' not in snippet_text:
                if query.lower() in row['file_name'].lower():
                    snippet_text = f"Match in filename: {row['file_name']}"
                elif row['folder_path'] and query.lower() in row['folder_path'].lower():
                    snippet_text = f"Match in folder: {row['folder_path']}"
                else:
                    snippet_text = 'No preview available'

            results.append({
                'id': row['id'],
                'file_name': row['file_name'],
                'file_path': row['file_path'],
                'file_type': row['file_type'],
                'file_size': row['file_size'],
                'modified_date': row['modified_date'],
                'indexed_date': row['indexed_date'],
                'snippet': snippet_text
            })

        conn.close()

        # Calculate total pages
        total_pages = (total_count + per_page - 1) // per_page

        return jsonify({
            'results': results,
            'count': total_count,
            'displayed': len(results),
            'query': query,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'filters': {
                'fileTypes': file_types,
                'scope': search_scope,
                'sort': sort_by
            }
        })

    except Exception as e:
        conn.close()
        return jsonify({
            'results': [],
            'count': 0,
            'query': query,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def stats():
    """Get database statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as count FROM documents')
    total = cursor.fetchone()['count']

    cursor.execute('SELECT file_type, COUNT(*) as count FROM documents GROUP BY file_type ORDER BY count DESC')
    by_type = [{'type': row['file_type'], 'count': row['count']} for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'total': total,
        'by_type': by_type
    })


@app.route('/api/open/<int:doc_id>')
def open_document(doc_id):
    """Get document path for opening"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT file_path FROM documents WHERE id = ?', (doc_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({'file_path': row['file_path']})
    else:
        return jsonify({'error': 'Document not found'}), 404


if __name__ == '__main__':
    if not os.path.exists(DATABASE_PATH):
        print(f"ERROR: Database not found at {DATABASE_PATH}")
        print("Please run indexer.py first to create and populate the database")
        exit(1)

    print(f"Starting server at http://{SERVER_HOST}:{SERVER_PORT}")
    print("Press Ctrl+C to stop")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=True)
