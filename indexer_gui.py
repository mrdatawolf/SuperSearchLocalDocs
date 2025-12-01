"""
GUI for Document Indexer - Supports multiple folder indexing
Allows users to configure multiple paths and run the indexer
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
import json
import sys
import os
import multiprocessing
import sqlite3
from concurrent.futures import ProcessPoolExecutor, as_completed
import queue

# Import indexer components
from indexer import DocumentIndexer
from database_manager import (
    add_indexed_folder, remove_indexed_folder,
    get_all_indexed_folders, get_database_path
)
from config_manager import load_user_config, save_user_config
from config import SERVER_HOST, SERVER_PORT


def index_folder_worker(folder_path, db_path, use_parallel):
    """
    Worker function that indexes a single folder - runs in separate process
    Returns: (folder_path, indexed_count, error_count, success, error_message)
    """
    try:
        # Create indexer for this folder
        indexer = DocumentIndexer(document_path=folder_path, db_path=db_path)

        # Run indexing (output goes to console, not captured)
        indexed_count, error_count = indexer.scan_and_index(
            use_parallel=use_parallel,
            progress_callback=None
        )

        return (folder_path, indexed_count, error_count, True, None)

    except Exception as e:
        import traceback
        error_msg = f"{str(e)}\n{traceback.format_exc()}"
        return (folder_path, 0, 0, False, error_msg)


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
        self.root.title("Document Search - Multi-Folder Indexer")
        self.root.geometry("1000x800")
        self.root.resizable(True, True)

        # Track indexed folders
        self.indexed_folders = []
        self.load_indexed_folders()

        # Create UI
        self.create_widgets()

    def create_widgets(self):
        """Create the GUI layout"""

        # Title
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)

        title_label = ttk.Label(
            title_frame,
            text="📁 Document Search - Multi-Folder Indexer",
            font=('Arial', 16, 'bold')
        )
        title_label.pack()

        subtitle_label = ttk.Label(
            title_frame,
            text="Index multiple document folders - each gets its own database",
            font=('Arial', 10)
        )
        subtitle_label.pack()

        # Server Configuration Frame
        server_frame = ttk.LabelFrame(self.root, text="Server Configuration", padding="15")
        server_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Load current server host from config
        user_config = load_user_config()
        current_server_host = user_config.get('server_host', SERVER_HOST)

        server_grid = ttk.Frame(server_frame)
        server_grid.pack(fill=tk.X)

        ttk.Label(
            server_grid,
            text="Server IP Address:",
            font=('Arial', 10)
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)

        self.server_host_var = tk.StringVar(value=current_server_host)
        server_host_entry = ttk.Entry(
            server_grid,
            textvariable=self.server_host_var,
            width=25,
            font=('Arial', 10)
        )
        server_host_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

        ttk.Label(
            server_grid,
            text=f"  Port: {SERVER_PORT}",
            font=('Arial', 10),
            foreground='gray'
        ).grid(row=0, column=2, sticky=tk.W, padx=(10, 0), pady=5)

        ttk.Button(
            server_grid,
            text="💾 Save Server Config",
            command=self.save_server_config,
            width=20
        ).grid(row=0, column=3, sticky=tk.W, padx=(20, 0), pady=5)

        ttk.Label(
            server_frame,
            text="This IP will be used for network access. Use 192.168.x.x for your network card IP. Restart apps after changing.",
            font=('Arial', 9),
            foreground='gray'
        ).pack(pady=(5, 0))

        # Indexed Folders Frame
        folders_frame = ttk.LabelFrame(self.root, text="Indexed Folders", padding="15")
        folders_frame.pack(fill=tk.BOTH, expand=False, padx=10, pady=10)

        # Listbox with scrollbar for folders
        list_frame = ttk.Frame(folders_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.folders_listbox = tk.Listbox(
            list_frame,
            height=6,
            font=('Consolas', 9),
            yscrollcommand=scrollbar.set
        )
        self.folders_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.folders_listbox.yview)

        # Buttons for folder management
        folder_buttons_frame = ttk.Frame(folders_frame)
        folder_buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(
            folder_buttons_frame,
            text="➕ Add Folder",
            command=self.add_folder,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            folder_buttons_frame,
            text="🔗 Link Existing DB",
            command=self.link_existing_database,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            folder_buttons_frame,
            text="➖ Remove Selected",
            command=self.remove_folder,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            folder_buttons_frame,
            text="🔄 Refresh List",
            command=self.refresh_folders_list,
            width=15
        ).pack(side=tk.LEFT, padx=5)

        ttk.Label(
            folders_frame,
            text="Each folder gets its own database. Use 'Link Existing DB' to use a pre-indexed database.",
            font=('Arial', 9),
            foreground='gray'
        ).pack(pady=(5, 0))

        # Performance options frame
        perf_frame = ttk.LabelFrame(self.root, text="Performance Options", padding="15")
        perf_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        # File-level parallel processing checkbox
        self.parallel_var = tk.BooleanVar(value=True)
        self.parallel_check = ttk.Checkbutton(
            perf_frame,
            text="⚡ Enable Fast Mode (parallel file processing)",
            variable=self.parallel_var,
            command=self.update_parallel_info
        )
        self.parallel_check.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # Folder-level parallel processing checkbox
        self.parallel_folders_var = tk.BooleanVar(value=True)
        self.parallel_folders_check = ttk.Checkbutton(
            perf_frame,
            text="🚀 Index Multiple Folders Simultaneously (recommended for 8+ cores)",
            variable=self.parallel_folders_var,
            command=self.update_parallel_info
        )
        self.parallel_folders_check.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))

        # CPU info label
        cpu_count = os.cpu_count() or 1
        workers = max(1, int(cpu_count * 0.75))
        self.cpu_info_var = tk.StringVar(value=f"Using {workers} of {cpu_count} CPU cores")
        self.cpu_info_label = ttk.Label(
            perf_frame,
            textvariable=self.cpu_info_var,
            font=('Arial', 9),
            foreground='#167E27'
        )
        self.cpu_info_label.grid(row=2, column=0, sticky=tk.W)

        # Update info on startup
        self.update_parallel_info()

        # Buttons frame
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)

        self.index_button = ttk.Button(
            button_frame,
            text="▶ Index All Folders",
            command=self.start_indexing,
            width=20
        )
        self.index_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="📊 Show All Statistics",
            command=self.show_all_stats,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🔨 Rebuild Word Counts",
            command=self.rebuild_word_counts,
            width=20
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="🗜️ Vacuum Databases",
            command=self.vacuum_databases,
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
            height=20,
            width=110,
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

    def save_server_config(self):
        """Save server host configuration to user config"""
        server_host = self.server_host_var.get().strip()

        if not server_host:
            messagebox.showerror("Invalid Input", "Server IP address cannot be empty")
            return

        # Basic IP validation
        parts = server_host.split('.')
        if len(parts) != 4:
            messagebox.showerror(
                "Invalid IP Address",
                "Please enter a valid IPv4 address (e.g., 192.168.1.100)"
            )
            return

        try:
            for part in parts:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError()
        except ValueError:
            messagebox.showerror(
                "Invalid IP Address",
                "Please enter a valid IPv4 address (e.g., 192.168.1.100)"
            )
            return

        # Load current config
        user_config = load_user_config()

        # Update server_host
        user_config['server_host'] = server_host

        # Save config
        if save_user_config(user_config):
            self.log_message(f"✓ Server configuration saved: {server_host}:{SERVER_PORT}")
            self.log_message("  Restart DocumentSearch.exe or DocumentSearchGUI.exe for changes to take effect\n")
            messagebox.showinfo(
                "Configuration Saved",
                f"Server configuration saved successfully!\n\n"
                f"Server will be accessible at:\n"
                f"  http://{server_host}:{SERVER_PORT}\n\n"
                f"Please restart the search server applications for changes to take effect."
            )
        else:
            messagebox.showerror("Error", "Failed to save server configuration")

    def load_indexed_folders(self):
        """Load indexed folders from database manager"""
        self.indexed_folders = get_all_indexed_folders()

    def refresh_folders_list(self):
        """Refresh the folders listbox"""
        self.load_indexed_folders()
        self.folders_listbox.delete(0, tk.END)

        if not self.indexed_folders:
            self.folders_listbox.insert(tk.END, "  (No folders indexed yet - click 'Add Folder' to start)")
            self.folders_listbox.itemconfig(0, {'fg': 'gray'})
        else:
            for folder_info in self.indexed_folders:
                display_text = f"  {folder_info['folder_path']}"
                if not folder_info['db_exists']:
                    display_text += " [NOT INDEXED YET]"
                self.folders_listbox.insert(tk.END, display_text)

    def add_folder(self):
        """Add a new folder to index"""
        path = filedialog.askdirectory(
            title="Select Folder to Index",
            initialdir=os.path.expanduser("~")
        )

        if not path:
            return

        # Normalize path
        path = str(Path(path).resolve())

        # Check if already added
        for folder_info in self.indexed_folders:
            if folder_info['folder_path'] == path:
                messagebox.showinfo("Already Added", "This folder is already in the index list")
                return

        # Add to database manager
        db_path = add_indexed_folder(path)
        self.log_message(f"✓ Added folder: {path}")
        self.log_message(f"  Database: {Path(db_path).name}\n")

        # Refresh list
        self.refresh_folders_list()

        # Update CPU info to reflect new folder count
        self.update_parallel_info()

    def link_existing_database(self):
        """Link a folder to an existing database file without re-indexing"""
        # Step 1: Select folder
        folder_path = filedialog.askdirectory(
            title="Select Folder (the documents location)",
            initialdir=os.path.expanduser("~")
        )

        if not folder_path:
            return

        # Normalize path
        folder_path = str(Path(folder_path).resolve())

        # Check if folder exists
        if not os.path.exists(folder_path):
            messagebox.showerror("Folder Not Found", f"The selected folder does not exist:\n{folder_path}")
            return

        # Check if already added
        for folder_info in self.indexed_folders:
            if folder_info['folder_path'] == folder_path:
                messagebox.showinfo("Already Added", "This folder is already in the index list")
                return

        # Step 2: Select existing database file
        db_file = filedialog.askopenfilename(
            title="Select Existing Database File",
            initialdir=os.path.expanduser("~"),
            filetypes=[
                ("SQLite Database", "*.sqlite3"),
                ("Database Files", "*.db"),
                ("All Files", "*.*")
            ]
        )

        if not db_file:
            return

        # Normalize path
        db_file = str(Path(db_file).resolve())

        # Validate database file exists
        if not os.path.exists(db_file):
            messagebox.showerror("Database Not Found", f"The selected database file does not exist:\n{db_file}")
            return

        # Confirm the link
        result = messagebox.askyesno(
            "Link Folder to Database",
            f"Link this folder:\n{folder_path}\n\n"
            f"To this database:\n{Path(db_file).name}\n\n"
            f"This will make the database searchable without re-indexing.\n"
            f"Continue?"
        )

        if not result:
            return

        try:
            # Link folder to existing database
            db_path = add_indexed_folder(folder_path, existing_db_path=db_file)

            self.log_message(f"✓ Linked folder to existing database:")
            self.log_message(f"  Folder: {folder_path}")
            self.log_message(f"  Database: {Path(db_path).name}\n")

            # Refresh list
            self.refresh_folders_list()

            # Update CPU info
            self.update_parallel_info()

            messagebox.showinfo(
                "Link Successful",
                f"Folder successfully linked to database!\n\n"
                f"The database is now searchable without re-indexing.\n"
                f"Run DocumentSearch.exe to search this folder."
            )

        except FileNotFoundError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to link folder to database:\n{str(e)}")

    def remove_folder(self):
        """Remove selected folder from index"""
        selection = self.folders_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a folder to remove")
            return

        index = selection[0]
        if not self.indexed_folders or index >= len(self.indexed_folders):
            return

        folder_info = self.indexed_folders[index]
        folder_path = folder_info['folder_path']

        # Confirm removal
        result = messagebox.askyesno(
            "Remove Folder",
            f"Remove this folder from the index?\n\n{folder_path}\n\n"
            f"Note: The database file will remain but won't be used for searches."
        )

        if result:
            remove_indexed_folder(folder_path)
            self.log_message(f"✓ Removed folder: {folder_path}\n")
            self.refresh_folders_list()

            # Update CPU info to reflect new folder count
            self.update_parallel_info()

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
        cpu_count = os.cpu_count() or 1
        file_parallel = self.parallel_var.get()
        folder_parallel = self.parallel_folders_var.get()

        if folder_parallel and file_parallel:
            # Both enabled - dynamic allocation
            num_folders = len(self.indexed_folders) if self.indexed_folders else 1
            folder_workers = min(num_folders, max(2, cpu_count // 4))  # 2-4 folder workers
            cores_per_folder = cpu_count // folder_workers
            self.cpu_info_var.set(
                f"Using all {cpu_count} cores: {folder_workers} folders in parallel, "
                f"~{cores_per_folder} cores per folder"
            )
        elif file_parallel:
            # Only file-level parallel
            workers = max(1, int(cpu_count * 0.75))
            self.cpu_info_var.set(f"Using {workers} of {cpu_count} cores (folders indexed sequentially)")
        else:
            # Sequential mode
            self.cpu_info_var.set("Sequential mode - using 1 core (slowest but lowest CPU usage)")

    def start_indexing(self):
        """Start the indexing process for all folders"""
        if not self.indexed_folders:
            messagebox.showwarning("No Folders", "Please add at least one folder to index")
            return

        # Confirm before starting
        result = messagebox.askyesno(
            "Start Indexing",
            f"Index {len(self.indexed_folders)} folder(s)?\n\nThis may take a while. Continue?"
        )

        if not result:
            return

        # Disable button and clear log
        self.index_button.config(state=tk.DISABLED)
        self.clear_log()
        self.progress_bar.start(10)
        self.status_var.set("Indexing...")

        # Get parallel processing settings
        use_file_parallel = self.parallel_var.get()
        use_folder_parallel = self.parallel_folders_var.get()

        # Run indexing in background thread
        thread = threading.Thread(target=self.run_indexing, args=(use_file_parallel, use_folder_parallel))
        thread.daemon = True
        thread.start()

    def run_indexing(self, use_file_parallel, use_folder_parallel):
        """Run the indexing process for all folders (called in background thread)"""
        try:
            self.log_message("=" * 80)
            self.log_message("MULTI-FOLDER INDEXING STARTING")
            self.log_message("=" * 80)
            self.log_message(f"Folders to index: {len(self.indexed_folders)}")
            self.log_message(f"File-level parallel processing: {'Enabled' if use_file_parallel else 'Disabled'}")
            self.log_message(f"Folder-level parallel processing: {'Enabled' if use_folder_parallel else 'Disabled'}")
            self.log_message("")

            # Filter out folders that don't exist
            valid_folders = []
            for folder_info in self.indexed_folders:
                if os.path.exists(folder_info['folder_path']):
                    valid_folders.append(folder_info)
                else:
                    self.log_message(f"⚠️  WARNING: Folder not found, skipping: {folder_info['folder_path']}")

            if not valid_folders:
                self.log_message("\n❌ ERROR: No valid folders to index!")
                self.root.after(0, self.indexing_failed, "No valid folders found")
                return

            total_indexed = 0
            total_errors = 0

            if use_folder_parallel and len(valid_folders) > 1:
                # PARALLEL FOLDER INDEXING with dynamic reallocation
                cpu_count = os.cpu_count() or 1
                max_workers = min(len(valid_folders), max(2, cpu_count // 4))

                self.log_message(f"🚀 Using {max_workers} worker processes for folder-level parallelism")
                self.log_message(f"   Workers will dynamically pick up folders as they complete")
                self.log_message("")

                # Track progress
                completed = 0
                in_progress = set()

                with ProcessPoolExecutor(max_workers=max_workers) as executor:
                    # Submit all folder tasks
                    future_to_folder = {
                        executor.submit(
                            index_folder_worker,
                            folder_info['folder_path'],
                            folder_info['db_path'],
                            use_file_parallel
                        ): folder_info
                        for folder_info in valid_folders
                    }

                    # Process results as they complete (dynamic reallocation!)
                    for future in as_completed(future_to_folder):
                        folder_info = future_to_folder[future]
                        folder_path = folder_info['folder_path']

                        try:
                            # Get result from worker
                            result_path, indexed_count, error_count, success, error_msg = future.result()

                            completed += 1

                            if success:
                                total_indexed += indexed_count
                                total_errors += error_count
                                self.log_message(
                                    f"✓ [{completed}/{len(valid_folders)}] Completed: {Path(folder_path).name} "
                                    f"({indexed_count} documents, {error_count} errors)"
                                )
                            else:
                                self.log_message(f"❌ [{completed}/{len(valid_folders)}] Failed: {Path(folder_path).name}")
                                self.log_message(f"   Error: {error_msg}")

                        except Exception as e:
                            completed += 1
                            self.log_message(f"❌ [{completed}/{len(valid_folders)}] Exception: {Path(folder_path).name}")
                            self.log_message(f"   Error: {str(e)}")

            else:
                # SEQUENTIAL FOLDER INDEXING (original behavior)
                if not use_folder_parallel and len(valid_folders) > 1:
                    self.log_message("Indexing folders sequentially (folder-level parallelism disabled)")
                self.log_message("")

                for i, folder_info in enumerate(valid_folders, 1):
                    folder_path = folder_info['folder_path']
                    db_path = folder_info['db_path']

                    self.log_message(f"\n{'='*80}")
                    self.log_message(f"INDEXING FOLDER {i}/{len(valid_folders)}")
                    self.log_message(f"{'='*80}")
                    self.log_message(f"Folder: {folder_path}")
                    self.log_message(f"Database: {Path(db_path).name}")
                    self.log_message("")

                    # Call worker function directly (no separate process)
                    result_path, indexed_count, error_count, success, error_msg = index_folder_worker(
                        folder_path, db_path, use_file_parallel
                    )

                    if success:
                        total_indexed += indexed_count
                        total_errors += error_count
                        self.log_message(f"\n✓ Folder complete: {indexed_count} documents indexed, {error_count} errors")
                    else:
                        self.log_message(f"\n❌ Folder failed!")
                        self.log_message(f"Error: {error_msg}")

            # Final summary
            self.log_message("")
            self.log_message("=" * 80)
            self.log_message("ALL FOLDERS COMPLETE")
            self.log_message("=" * 80)
            self.log_message(f"Total documents indexed: {total_indexed}")
            self.log_message(f"Total errors: {total_errors}")
            self.log_message("")

            self.root.after(0, self.indexing_complete, total_indexed, total_errors)

        except Exception as e:
            self.log_message(f"\n❌ ERROR: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
            self.root.after(0, self.indexing_failed, str(e))

    def indexing_complete(self, indexed_count, error_count):
        """Called when indexing completes successfully"""
        self.progress_bar.stop()
        self.index_button.config(state=tk.NORMAL)
        self.status_var.set(f"Complete! {indexed_count} documents indexed")

        messagebox.showinfo(
            "Indexing Complete",
            f"Successfully indexed {indexed_count} documents\n"
            f"Errors: {error_count}\n\n"
            f"You can now use DocumentSearch to search your documents!"
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

    def show_all_stats(self):
        """Show statistics for all databases"""
        if not self.indexed_folders:
            messagebox.showinfo("No Databases", "No folders have been indexed yet")
            return

        try:
            stats_msg = "DATABASE STATISTICS\n" + "=" * 50 + "\n\n"

            total_docs = 0
            for folder_info in self.indexed_folders:
                db_path = folder_info['db_path']
                folder_path = folder_info['folder_path']

                if not os.path.exists(db_path):
                    stats_msg += f"📁 {folder_path}\n"
                    stats_msg += "   (Not indexed yet)\n\n"
                    continue

                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                cursor.execute('SELECT COUNT(*) FROM documents')
                doc_count = cursor.fetchone()[0]
                total_docs += doc_count

                stats_msg += f"📁 {folder_path}\n"
                stats_msg += f"   Documents: {doc_count}\n"

                cursor.execute('SELECT file_type, COUNT(*) FROM documents GROUP BY file_type')
                by_type = cursor.fetchall()
                if by_type:
                    for file_type, count in by_type[:3]:  # Show top 3 types
                        stats_msg += f"     • {file_type}: {count}\n"

                conn.close()
                stats_msg += "\n"

            stats_msg += "=" * 50 + "\n"
            stats_msg += f"TOTAL DOCUMENTS: {total_docs}"

            messagebox.showinfo("Statistics", stats_msg)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read database:\n{str(e)}")

    def rebuild_word_counts(self):
        """Rebuild word counts for all databases"""
        if not self.indexed_folders:
            messagebox.showinfo("No Databases", "No folders have been indexed yet")
            return

        # Confirm action
        result = messagebox.askyesno(
            "Rebuild Word Counts",
            f"This will rebuild word count statistics for all {len(self.indexed_folders)} database(s).\n\n"
            "This is useful after upgrading to improve search performance.\n\n"
            "Continue?"
        )

        if not result:
            return

        # Run in background thread
        def rebuild_all():
            try:
                self.log_message("\n" + "=" * 80)
                self.log_message("REBUILDING WORD COUNTS")
                self.log_message("=" * 80)

                for i, folder_info in enumerate(self.indexed_folders, 1):
                    db_path = folder_info['db_path']
                    folder_path = folder_info['folder_path']

                    if not os.path.exists(db_path):
                        self.log_message(f"\n[{i}/{len(self.indexed_folders)}] Skipping {folder_path} (not indexed yet)")
                        continue

                    self.log_message(f"\n[{i}/{len(self.indexed_folders)}] Processing: {folder_path}")
                    self.log_message(f"Database: {db_path}")

                    # Create indexer and rebuild word counts
                    indexer = DocumentIndexer(document_path=folder_path, db_path=db_path)
                    indexer.rebuild_word_counts()

                self.log_message("\n" + "=" * 80)
                self.log_message("✓ WORD COUNTS REBUILT FOR ALL DATABASES")
                self.log_message("=" * 80 + "\n")

                messagebox.showinfo("Success", "Word counts have been rebuilt for all databases!")

            except Exception as e:
                error_msg = f"Error rebuilding word counts:\n{str(e)}"
                self.log_message(f"\n❌ {error_msg}")
                messagebox.showerror("Error", error_msg)

        thread = threading.Thread(target=rebuild_all)
        thread.daemon = True
        thread.start()

    def vacuum_databases(self):
        """Vacuum all databases to reclaim disk space"""
        if not self.indexed_folders:
            messagebox.showinfo("No Databases", "No folders have been indexed yet")
            return

        # Confirm action
        result = messagebox.askyesno(
            "Vacuum Databases",
            f"This will compact all {len(self.indexed_folders)} database(s) to reclaim disk space.\n\n"
            "Run this AFTER rebuilding word counts to get the most benefit.\n\n"
            "This may take a few minutes depending on database size.\n\n"
            "Continue?"
        )

        if not result:
            return

        # Run in background thread
        def vacuum_all():
            try:
                self.log_message("\n" + "=" * 80)
                self.log_message("DATABASE VACUUM UTILITY")
                self.log_message("=" * 80)
                self.log_message("\nThis will compact all database files to reclaim disk space.")
                self.log_message("Run this AFTER rebuilding word counts to get the most benefit.\n")

                total_space_before = 0
                total_space_after = 0
                successful_vacuums = 0

                for i, folder_info in enumerate(self.indexed_folders, 1):
                    db_path = folder_info['db_path']
                    folder_path = folder_info['folder_path']

                    if not os.path.exists(db_path):
                        self.log_message(f"\n[{i}/{len(self.indexed_folders)}] Skipping {folder_path} (database not found)")
                        continue

                    db_name = os.path.basename(db_path)

                    # Get size before
                    size_before = os.path.getsize(db_path)
                    size_before_mb = size_before / (1024 * 1024)
                    total_space_before += size_before

                    self.log_message(f"\n[{i}/{len(self.indexed_folders)}] Processing: {db_name}")
                    self.log_message(f"  Size before: {size_before_mb:.2f} MB")

                    try:
                        # Connect and vacuum
                        conn = sqlite3.connect(db_path)
                        self.log_message("  Vacuuming... ")

                        # Disable WAL mode if enabled (WAL prevents VACUUM from shrinking the main db file)
                        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                        conn.execute("PRAGMA journal_mode=DELETE")
                        conn.commit()

                        # Execute VACUUM
                        conn.execute("VACUUM")
                        conn.commit()

                        # Switch back to WAL mode for better performance
                        conn.execute("PRAGMA journal_mode=WAL")
                        conn.commit()
                        conn.close()

                        # Force file system to update (Windows caching issue)
                        import time
                        time.sleep(0.2)

                        self.log_message("  Done!")

                        # Get size after
                        size_after = os.path.getsize(db_path)
                        size_after_mb = size_after / (1024 * 1024)
                        total_space_after += size_after

                        saved = size_before - size_after
                        saved_mb = saved / (1024 * 1024)
                        percent_saved = (saved / size_before * 100) if size_before > 0 else 0

                        self.log_message(f"  Size after:  {size_after_mb:.2f} MB")
                        self.log_message(f"  Space saved: {saved_mb:.2f} MB ({percent_saved:.1f}%)")

                        successful_vacuums += 1

                    except Exception as e:
                        self.log_message(f"  ERROR: {e}")

                # Summary
                self.log_message("\n" + "=" * 80)
                self.log_message("SUMMARY")
                self.log_message("=" * 80)

                total_before_mb = total_space_before / (1024 * 1024)
                total_after_mb = total_space_after / (1024 * 1024)
                total_saved_mb = (total_space_before - total_space_after) / (1024 * 1024)
                total_percent = ((total_space_before - total_space_after) / total_space_before * 100) if total_space_before > 0 else 0

                self.log_message(f"Total size before: {total_before_mb:.2f} MB")
                self.log_message(f"Total size after:  {total_after_mb:.2f} MB")
                self.log_message(f"Total space saved: {total_saved_mb:.2f} MB ({total_percent:.1f}%)")
                self.log_message(f"\n✓ Vacuum complete! Successfully compacted {successful_vacuums} of {len(self.indexed_folders)} database(s)\n")

                messagebox.showinfo(
                    "Success",
                    f"Vacuum complete!\n\n"
                    f"Databases compacted: {successful_vacuums}/{len(self.indexed_folders)}\n"
                    f"Space saved: {total_saved_mb:.2f} MB ({total_percent:.1f}%)"
                )

            except Exception as e:
                error_msg = f"Error during vacuum:\n{str(e)}"
                self.log_message(f"\n❌ {error_msg}")
                messagebox.showerror("Error", error_msg)

        thread = threading.Thread(target=vacuum_all)
        thread.daemon = True
        thread.start()


def main():
    """Main entry point for the GUI"""
    # Required for multiprocessing on Windows
    multiprocessing.freeze_support()

    root = tk.Tk()
    app = IndexerGUI(root)
    app.refresh_folders_list()  # Initial load
    root.mainloop()


if __name__ == '__main__':
    main()
