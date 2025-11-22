"""
GUI for Document Indexer - Initial setup and configuration
Allows users to configure paths and run the indexer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import json
import sys
import os
import multiprocessing

# Import indexer components
from indexer import DocumentIndexer
from config_manager import save_user_config, load_user_config


class TextRedirector:
    """Redirect stdout/stderr to a text widget"""
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.config(state=tk.NORMAL)
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)
        self.widget.config(state=tk.DISABLED)
        self.widget.update_idletasks()

    def flush(self):
        pass


class IndexerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Search - Indexer Setup")
        self.root.geometry("900x750")  # Larger window
        self.root.resizable(True, True)

        # Load existing config
        self.config = load_user_config()

        # Create UI
        self.create_widgets()

        # Load saved paths if they exist
        self.load_saved_config()

    def create_widgets(self):
        """Create the GUI layout"""

        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="📁 Document Search Indexer",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Configure paths and index your documents",
            font=('Arial', 10)
        )
        subtitle_label.pack()

        # Configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding="15")
        config_frame.pack(fill=tk.X, padx=10, pady=10)

        # Document Path
        ttk.Label(config_frame, text="Document Folder to Index:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5)
        )

        doc_path_frame = ttk.Frame(config_frame)
        doc_path_frame.grid(row=1, column=0, sticky=tk.EW, pady=(0, 15))
        doc_path_frame.columnconfigure(0, weight=1)

        self.doc_path_var = tk.StringVar()
        self.doc_path_entry = ttk.Entry(doc_path_frame, textvariable=self.doc_path_var, width=50)
        self.doc_path_entry.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))

        ttk.Button(doc_path_frame, text="Browse...", command=self.browse_doc_path).grid(row=0, column=1)

        ttk.Label(config_frame, text="Folder containing documents to scan (e.g., C:\\Documents or \\\\server\\share)",
                 font=('Arial', 9), foreground='gray').grid(row=2, column=0, sticky=tk.W, pady=(0, 10))

        # Database Path
        ttk.Label(config_frame, text="Database File Path:", font=('Arial', 10, 'bold')).grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )

        db_path_frame = ttk.Frame(config_frame)
        db_path_frame.grid(row=4, column=0, sticky=tk.EW, pady=(0, 15))
        db_path_frame.columnconfigure(0, weight=1)

        self.db_path_var = tk.StringVar(value="documents.sqlite3")
        self.db_path_entry = ttk.Entry(db_path_frame, textvariable=self.db_path_var, width=50)
        self.db_path_entry.grid(row=0, column=0, sticky=tk.EW, padx=(0, 5))

        ttk.Button(db_path_frame, text="Browse...", command=self.browse_db_path).grid(row=0, column=1)

        ttk.Label(config_frame, text="SQLite database file (will be created if it doesn't exist)",
                 font=('Arial', 9), foreground='gray').grid(row=5, column=0, sticky=tk.W, pady=(0, 10))

        config_frame.columnconfigure(0, weight=1)

        # Performance options frame
        perf_frame = ttk.LabelFrame(self.root, text="Performance Options", padding="15")
        perf_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # Parallel processing checkbox
        self.parallel_var = tk.BooleanVar(value=True)  # Default to enabled
        self.parallel_check = ttk.Checkbutton(
            perf_frame,
            text="⚡ Enable Fast Mode (parallel processing)",
            variable=self.parallel_var,
            command=self.update_parallel_info
        )
        self.parallel_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # CPU info label
        cpu_count = os.cpu_count() or 1
        workers = max(1, int(cpu_count * 0.75))
        self.cpu_info_var = tk.StringVar(value=f"Using {workers} of {cpu_count} CPU cores for faster indexing")
        self.cpu_info_label = ttk.Label(
            perf_frame,
            textvariable=self.cpu_info_var,
            font=('Arial', 9),
            foreground='#167E27'
        )
        self.cpu_info_label.grid(row=1, column=0, sticky=tk.W)

        # Buttons frame
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        ttk.Button(
            button_frame,
            text="💾 Save Configuration",
            command=self.save_config,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        self.index_button = ttk.Button(
            button_frame,
            text="▶ Start Indexing",
            command=self.start_indexing,
            width=20
        )
        self.index_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="📊 Show Statistics",
            command=self.show_stats,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        # Progress frame
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            variable=self.progress_var
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        # Log output
        self.log_text = scrolledtext.ScrolledText(
            progress_frame,
            height=20,  # Taller log window
            width=100,  # Wider
            font=('Consolas', 9),
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding="5"
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def load_saved_config(self):
        """Load previously saved configuration"""
        if 'document_path' in self.config:
            self.doc_path_var.set(self.config['document_path'])

        if 'database_path' in self.config:
            self.db_path_var.set(self.config['database_path'])

    def browse_doc_path(self):
        """Browse for document folder"""
        path = filedialog.askdirectory(
            title="Select Document Folder to Index",
            initialdir=self.doc_path_var.get() or os.path.expanduser("~")
        )
        if path:
            self.doc_path_var.set(path)

    def browse_db_path(self):
        """Browse for database file"""
        path = filedialog.asksaveasfilename(
            title="Select or Create Database File",
            defaultextension=".sqlite3",
            filetypes=[("SQLite Database", "*.sqlite3"), ("All Files", "*.*")],
            initialdir=os.path.dirname(self.db_path_var.get()) or os.getcwd()
        )
        if path:
            self.db_path_var.set(path)

    def save_config(self):
        """Save configuration to user_config.json"""
        doc_path = self.doc_path_var.get().strip()
        db_path = self.db_path_var.get().strip()

        if not doc_path:
            messagebox.showwarning("Missing Path", "Please specify a document folder path")
            return

        if not db_path:
            messagebox.showwarning("Missing Path", "Please specify a database file path")
            return

        # Validate document path exists
        if not os.path.exists(doc_path):
            result = messagebox.askyesno(
                "Path Not Found",
                f"The document path does not exist:\n{doc_path}\n\nDo you want to save it anyway?"
            )
            if not result:
                return

        # Save to config
        config_data = {
            'document_path': doc_path,
            'database_path': db_path
        }

        if save_user_config(config_data):
            self.config = config_data
            self.log_message("✓ Configuration saved successfully")
            self.status_var.set("Configuration saved")
            messagebox.showinfo("Success", "Configuration has been saved!")
        else:
            messagebox.showerror("Error", "Failed to save configuration")

    def log_message(self, message):
        """Add message to log output"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the log output"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def update_parallel_info(self):
        """Update the CPU info label when parallel checkbox changes"""
        if self.parallel_var.get():
            cpu_count = os.cpu_count() or 1
            workers = max(1, int(cpu_count * 0.75))
            self.cpu_info_var.set(f"Using {workers} of {cpu_count} CPU cores for faster indexing")
        else:
            self.cpu_info_var.set("Sequential mode - using 1 core (slower but lower CPU usage)")

    def start_indexing(self):
        """Start the indexing process in a background thread"""
        doc_path = self.doc_path_var.get().strip()
        db_path = self.db_path_var.get().strip()

        # Validate paths
        if not doc_path:
            messagebox.showwarning("Missing Path", "Please specify a document folder path")
            return

        if not db_path:
            messagebox.showwarning("Missing Path", "Please specify a database file path")
            return

        if not os.path.exists(doc_path):
            messagebox.showerror("Path Not Found", f"Document folder does not exist:\n{doc_path}")
            return

        # Confirm before starting
        result = messagebox.askyesno(
            "Start Indexing",
            f"Index all documents in:\n{doc_path}\n\nThis may take a while. Continue?"
        )

        if not result:
            return

        # Disable button and clear log
        self.index_button.config(state=tk.DISABLED)
        self.clear_log()
        self.progress_bar.start(10)
        self.status_var.set("Indexing...")

        # Get parallel processing setting
        use_parallel = self.parallel_var.get()

        # Run indexing in background thread
        thread = threading.Thread(target=self.run_indexing, args=(doc_path, db_path, use_parallel))
        thread.daemon = True
        thread.start()

    def progress_callback(self, current, total, message):
        """Callback for indexing progress updates"""
        # This is called from the worker thread, so use root.after for thread-safety
        # We don't actually need to update anything here since scan_and_index handles logging
        pass

    def run_indexing(self, doc_path, db_path, use_parallel):
        """Run the indexing process (called in background thread)"""
        # Save original stdout
        original_stdout = sys.stdout

        try:
            self.log_message("=" * 80)
            self.log_message("Document Indexer Starting...")
            self.log_message("=" * 80)
            self.log_message(f"Document path: {doc_path}")
            self.log_message(f"Database path: {db_path}")
            self.log_message(f"Parallel processing: {'Enabled' if use_parallel else 'Disabled'}")
            self.log_message("")

            # Create indexer with custom paths
            indexer = DocumentIndexer()
            indexer.document_path = doc_path
            indexer.db_path = db_path

            # Initialize database
            self.log_message("Initializing database...")
            indexer.init_database()
            self.log_message("")

            # Redirect stdout to the GUI log window
            sys.stdout = TextRedirector(self.log_text, "stdout")

            # Use the built-in scan_and_index which supports parallel processing
            # This method handles all the logging and progress reporting
            indexed_count, error_count = indexer.scan_and_index(
                use_parallel=use_parallel,
                progress_callback=self.progress_callback
            )

            # Restore stdout before showing statistics
            sys.stdout = original_stdout

            # Show database statistics (using log_message for GUI display)
            self.log_message("")
            self.log_message("=" * 80)
            self.log_message("Database Statistics:")
            self.log_message("=" * 80)
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM documents')
            total_docs = cursor.fetchone()[0]
            self.log_message(f"Total documents in database: {total_docs}")

            cursor.execute('SELECT file_type, COUNT(*) FROM documents GROUP BY file_type ORDER BY COUNT(*) DESC')
            by_type = cursor.fetchall()
            self.log_message("")
            self.log_message("By file type:")
            for file_type, count in by_type:
                self.log_message(f"  {file_type}: {count}")

            conn.close()
            self.log_message("=" * 80)

            self.root.after(0, self.indexing_complete, indexed_count, error_count)

        except Exception as e:
            # Restore stdout in case of error
            sys.stdout = original_stdout

            self.log_message(f"\n❌ ERROR: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
            self.root.after(0, self.indexing_failed, str(e))

        finally:
            # Ensure stdout is always restored
            sys.stdout = original_stdout

    def indexing_complete(self, indexed_count, error_count):
        """Called when indexing completes successfully"""
        self.progress_bar.stop()
        self.index_button.config(state=tk.NORMAL)
        self.status_var.set(f"Indexing complete! {indexed_count} documents indexed")

        messagebox.showinfo(
            "Indexing Complete",
            f"Successfully indexed {indexed_count} documents\nErrors: {error_count}"
        )

    def indexing_failed(self, error_msg):
        """Called when indexing fails"""
        self.progress_bar.stop()
        self.index_button.config(state=tk.NORMAL)
        self.status_var.set("Indexing failed")

        messagebox.showerror(
            "Indexing Failed",
            f"An error occurred during indexing:\n{error_msg}"
        )

    def show_stats(self):
        """Show database statistics"""
        db_path = self.db_path_var.get().strip()

        if not db_path or not os.path.exists(db_path):
            messagebox.showwarning("Database Not Found", "Database file does not exist")
            return

        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM documents')
            total_docs = cursor.fetchone()[0]

            cursor.execute('SELECT file_type, COUNT(*) FROM documents GROUP BY file_type')
            by_type = cursor.fetchall()

            conn.close()

            # Build stats message
            stats_msg = f"Total documents: {total_docs}\n\nBy file type:\n"
            for file_type, count in by_type:
                stats_msg += f"  {file_type}: {count}\n"

            messagebox.showinfo("Database Statistics", stats_msg)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read database:\n{str(e)}")


def main():
    """Main entry point for the GUI"""
    # Required for multiprocessing on Windows
    multiprocessing.freeze_support()

    root = tk.Tk()
    app = IndexerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
