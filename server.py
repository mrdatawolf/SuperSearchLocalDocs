"""Flask web server for document search"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import webbrowser
import threading
from pathlib import Path
from config import DATABASE_PATH, SERVER_HOST, SERVER_PORT, DOCUMENT_PATH
from config_manager import get_all_config, save_user_config, reset_to_defaults
from company_abbreviations import get_company_abbreviations
from database_manager import get_all_database_paths, get_all_indexed_folders

app = Flask(__name__)

# Initialize company abbreviations
company_abbrev = None

@app.before_request
def initialize():
    """Initialize company abbreviations on first request"""
    global company_abbrev
    if company_abbrev is None:
        company_abbrev = get_company_abbreviations()


def get_all_db_connections():
    """Get connections to all indexed databases"""
    db_paths = get_all_database_paths()
    connections = []

    for db_path in db_paths:
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            connections.append((db_path, conn))

    return connections


def get_db_connection():
    """Get database connection using current config (legacy - for settings UI)"""
    config = get_all_config()
    db_path = config.get('database_path', DATABASE_PATH)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    """Serve the main search page"""
    return render_template('index.html')


@app.route('/api/search')
def search():
    """Search API endpoint with filtering support - queries all databases"""
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

    # Get connections to all databases
    db_connections = get_all_db_connections()

    if not db_connections:
        return jsonify({
            'results': [],
            'count': 0,
            'query': query,
            'error': 'No databases found. Please index some folders first.'
        }), 404

    all_results = []  # Will collect results from all databases

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

        # Query SQL (without LIMIT/OFFSET - we'll do that after merging)
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

        # Query each database and collect results
        for db_path, conn in db_connections:
            try:
                cursor = conn.cursor()
                cursor.execute(sql, params)

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

                    all_results.append({
                        'id': row['id'],
                        'file_name': row['file_name'],
                        'file_path': row['file_path'],
                        'file_type': row['file_type'],
                        'file_size': row['file_size'],
                        'modified_date': row['modified_date'],
                        'indexed_date': row['indexed_date'],
                        'snippet': snippet_text,
                        'rank': row['rank'],
                        'db_source': Path(db_path).name  # Track which database this came from
                    })

                conn.close()
            except Exception as e:
                conn.close()
                print(f"Error querying database {db_path}: {e}")
                continue

        # Sort all results
        if sort_by == 'date':
            all_results.sort(key=lambda x: x.get('modified_date', ''), reverse=True)
        elif sort_by == 'name':
            all_results.sort(key=lambda x: x.get('file_name', '').lower())
        elif sort_by == 'size':
            all_results.sort(key=lambda x: x.get('file_size', 0), reverse=True)
        else:  # relevance (default) - rank is negative, so higher (closer to 0) is better
            all_results.sort(key=lambda x: x.get('rank', -999999), reverse=True)

        # Apply pagination to merged results
        total_count = len(all_results)
        start_idx = offset
        end_idx = offset + per_page
        paginated_results = all_results[start_idx:end_idx]

        # Remove rank and db_source from final results (internal use only)
        for result in paginated_results:
            result.pop('rank', None)
            result.pop('db_source', None)

        # Calculate total pages
        total_pages = (total_count + per_page - 1) // per_page

        return jsonify({
            'results': paginated_results,
            'count': total_count,
            'displayed': len(paginated_results),
            'query': query,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'databases_queried': len(db_connections),
            'filters': {
                'fileTypes': file_types,
                'scope': search_scope,
                'sort': sort_by
            }
        })

    except Exception as e:
        # Close any remaining connections
        for db_path, conn in db_connections:
            try:
                conn.close()
            except:
                pass

        return jsonify({
            'results': [],
            'count': 0,
            'query': query,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def stats():
    """Get database statistics - aggregated across all databases"""
    db_connections = get_all_db_connections()

    if not db_connections:
        return jsonify({
            'total': 0,
            'by_type': [],
            'error': 'No databases found'
        })

    total = 0
    type_counts = {}

    # Aggregate stats from all databases
    for db_path, conn in db_connections:
        try:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) as count FROM documents')
            total += cursor.fetchone()['count']

            cursor.execute('SELECT file_type, COUNT(*) as count FROM documents GROUP BY file_type')
            for row in cursor.fetchall():
                file_type = row['file_type']
                count = row['count']
                type_counts[file_type] = type_counts.get(file_type, 0) + count

            conn.close()
        except Exception as e:
            conn.close()
            print(f"Error getting stats from {db_path}: {e}")
            continue

    # Convert type_counts dict to sorted list
    by_type = [{'type': ftype, 'count': count} for ftype, count in type_counts.items()]
    by_type.sort(key=lambda x: x['count'], reverse=True)

    return jsonify({
        'total': total,
        'by_type': by_type,
        'databases_count': len(db_connections)
    })


@app.route('/api/top-words')
def top_words():
    """Get top 10 most common words from indexed content - across all databases"""
    db_connections = get_all_db_connections()

    if not db_connections:
        return jsonify({'words': [], 'error': 'No databases found'})

    try:
        from collections import Counter
        import re

        word_counts = Counter()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
                     'this', 'that', 'these', 'those', 'it', 'its', 'can', 'will', 'would',
                     'sheet', 'none', 'true', 'false', 'openpyxl', 'not', 'installed',
                     'error', 'reading'}

        # Sample from all databases
        for db_path, conn in db_connections:
            try:
                cursor = conn.cursor()

                # Get random sample of documents
                cursor.execute('''
                    SELECT content FROM documents
                    WHERE content IS NOT NULL AND content != ''
                    AND LENGTH(content) > 20
                    ORDER BY RANDOM()
                    LIMIT 50
                ''')

                rows = cursor.fetchall()

                for row in rows:
                    content = row['content'].lower()
                    # Extract words (alphanumeric, 3+ chars)
                    words = re.findall(r'\b[a-z]{3,}\b', content)
                    for word in words:
                        if word not in stop_words:
                            word_counts[word] += 1

                conn.close()
            except Exception as e:
                conn.close()
                print(f"Error getting words from {db_path}: {e}")
                continue

        # Get top 10
        top_10 = [{'word': word, 'count': count} for word, count in word_counts.most_common(10)]

        return jsonify({'words': top_10})

    except Exception as e:
        return jsonify({'words': [], 'error': str(e)})


@app.route('/api/settings')
def get_settings():
    """Get current settings including defaults and overrides"""
    from config import DATABASE_PATH as DEFAULT_DB, SERVER_HOST as DEFAULT_HOST, SERVER_PORT as DEFAULT_PORT, DOCUMENT_PATH as DEFAULT_DOC

    config = get_all_config()

    # Set default action if not already set
    if 'default_action' not in config:
        config['default_action'] = 'open'

    return jsonify({
        'current': config,
        'defaults': {
            'database_path': DEFAULT_DB,
            'server_host': DEFAULT_HOST,
            'server_port': DEFAULT_PORT,
            'document_path': DEFAULT_DOC,
            'default_action': 'open'
        }
    })


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update user settings"""
    try:
        new_settings = request.json

        # Validate settings
        if 'database_path' in new_settings:
            db_path = Path(new_settings['database_path'])
            if not db_path.exists():
                return jsonify({'error': f'Database file not found: {new_settings["database_path"]}'}), 400

        # Validate default_action if provided
        if 'default_action' in new_settings:
            valid_actions = ['open', 'copy', 'folder']
            if new_settings['default_action'] not in valid_actions:
                return jsonify({'error': f'Invalid default_action. Must be one of: {", ".join(valid_actions)}'}), 400

        # Save settings
        if save_user_config(new_settings):
            return jsonify({'success': True, 'message': 'Settings saved successfully'})
        else:
            return jsonify({'error': 'Failed to save settings'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/reset', methods=['POST'])
def reset_settings():
    """Reset settings to defaults"""
    try:
        reset_to_defaults()
        return jsonify({'success': True, 'message': 'Settings reset to defaults'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/open', methods=['POST'])
def open_file():
    """Open a file in its associated program"""
    try:
        data = request.json
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found', 'path': file_path}), 404

        # Open file in default program (platform-specific)
        import subprocess
        import platform

        system = platform.system()
        if system == 'Windows':
            os.startfile(file_path)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', file_path])

        return jsonify({'success': True, 'message': f'Opened file: {Path(file_path).name}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/file/open-folder', methods=['POST'])
def open_folder():
    """Open File Explorer to the folder containing the file"""
    try:
        data = request.json
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({'error': 'No file path provided'}), 400

        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found', 'path': file_path}), 404

        # Get folder path
        folder_path = str(Path(file_path).parent)

        # Open folder in File Explorer (platform-specific)
        import subprocess
        import platform

        system = platform.system()
        if system == 'Windows':
            # Use explorer with /select to highlight the file
            subprocess.run(['explorer', '/select,', file_path])
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', '-R', file_path])
        else:  # Linux
            subprocess.run(['xdg-open', folder_path])

        return jsonify({'success': True, 'message': f'Opened folder: {folder_path}'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def open_browser():
    """Open the default web browser to the application URL"""
    webbrowser.open(f'http://127.0.0.1:{SERVER_PORT}')


if __name__ == '__main__':
    # Check if any databases exist
    indexed_folders = get_all_indexed_folders()
    db_paths = get_all_database_paths()

    if not indexed_folders:
        print("=" * 80)
        print("WARNING: No indexed folders found!")
        print("=" * 80)
        print("Please run DocumentIndexer.exe first to:")
        print("  1. Add folders to index")
        print("  2. Index your documents")
        print()
        print("The search server will start, but no documents will be available")
        print("until you index some folders.")
        print("=" * 80)
        print()
    else:
        print("=" * 80)
        print("DOCUMENT SEARCH SERVER")
        print("=" * 80)
        print(f"Indexed folders: {len(indexed_folders)}")
        for folder_info in indexed_folders:
            db_exists = "✓" if folder_info['db_exists'] else "✗"
            print(f"  {db_exists} {folder_info['folder_path']}")
        print()
        total_dbs = len([p for p in db_paths if os.path.exists(p)])
        print(f"Active databases: {total_dbs}")
        print("=" * 80)
        print()

    print(f"Starting server on all network interfaces at port {SERVER_PORT}")
    print(f"Access locally at: http://127.0.0.1:{SERVER_PORT}")
    print(f"Access from network at: http://{SERVER_HOST}:{SERVER_PORT}")
    print("Press Ctrl+C to stop")
    print()
    print("Opening web browser...")

    # Open browser after a short delay to ensure server is ready
    threading.Timer(1.5, open_browser).start()

    app.run(host='0.0.0.0', port=SERVER_PORT, debug=True)
