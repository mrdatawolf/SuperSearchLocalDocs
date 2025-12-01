"""
Document Search - Desktop GUI Application
Standalone desktop app that wraps the web interface
"""
import sys
import os
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
from pathlib import Path

# Try to import webview for embedded browser (fallback to external browser if not available)
try:
    import webview
    HAS_WEBVIEW = True
except ImportError:
    HAS_WEBVIEW = False


class SearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Document Search")
        self.root.geometry("1200x800")
        self.root.resizable(True, True)

        self.server_process = None

        # Load server configuration from user config
        try:
            from config_manager import load_user_config
            from config import SERVER_HOST, SERVER_PORT
            user_config = load_user_config()
            self.server_host = user_config.get('server_host', SERVER_HOST)
            self.server_port = SERVER_PORT
        except:
            self.server_host = "127.0.0.1"
            self.server_port = 9000

        self.server_url = f"http://{self.server_host}:{self.server_port}"

        # Create UI
        self.create_widgets()

        # Start server
        self.start_server()

        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        """Create the GUI layout"""

        # Status bar at top
        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.pack(fill=tk.X, side=tk.TOP)

        self.status_label = ttk.Label(
            status_frame,
            text="⏳ Starting server...",
            font=('Arial', 10)
        )
        self.status_label.pack(side=tk.LEFT)

        # Buttons
        ttk.Button(
            status_frame,
            text="🔄 Refresh",
            command=self.refresh_browser,
            width=12
        ).pack(side=tk.RIGHT, padx=5)

        ttk.Button(
            status_frame,
            text="🌐 Open in Browser",
            command=self.open_in_external_browser,
            width=15
        ).pack(side=tk.RIGHT, padx=5)

        # Main content area
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        if HAS_WEBVIEW:
            # Use embedded browser
            self.browser_label = ttk.Label(
                content_frame,
                text="Loading web interface...",
                font=('Arial', 12),
                anchor=tk.CENTER
            )
            self.browser_label.pack(fill=tk.BOTH, expand=True)
        else:
            # Show instructions to open in external browser
            info_text = tk.Text(
                content_frame,
                wrap=tk.WORD,
                font=('Arial', 11),
                bg='#f5f5f5',
                padx=20,
                pady=20
            )
            info_text.pack(fill=tk.BOTH, expand=True)

            info_text.insert('1.0', f"""
Document Search - Desktop Application

The search server is starting...

Once started, you can access the search interface at:
{self.server_url}

Click "🌐 Open in Browser" button above to open the interface in your default web browser.

Server Status: Starting...

Note: To use the embedded browser view, install the webview package:
    pip install pywebview
            """)
            info_text.config(state=tk.DISABLED)
            self.info_text = info_text

    def start_server(self):
        """Start the Flask server in a background thread"""
        def run_server():
            try:
                # Get the directory where this script is located
                script_dir = Path(__file__).parent
                server_script = script_dir / "server.py"

                # Start server without auto-opening browser
                self.server_process = subprocess.Popen(
                    [sys.executable, str(server_script), "--no-browser"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )

                # Wait a bit for server to start
                time.sleep(2)

                # Check if server is running
                if self.server_process.poll() is None:
                    self.root.after(0, self.on_server_started)
                else:
                    self.root.after(0, self.on_server_failed)

            except Exception as e:
                self.root.after(0, lambda: self.on_server_error(str(e)))

        thread = threading.Thread(target=run_server, daemon=True)
        thread.start()

    def on_server_started(self):
        """Called when server starts successfully"""
        self.status_label.config(text=f"✅ Server running at {self.server_url}")

        if HAS_WEBVIEW:
            # Launch embedded browser
            self.launch_embedded_browser()
        else:
            # Update info text
            if hasattr(self, 'info_text'):
                self.info_text.config(state=tk.NORMAL)
                self.info_text.delete('1.0', tk.END)
                self.info_text.insert('1.0', f"""
Document Search - Desktop Application

✅ Server is running!

Access the search interface at:
{self.server_url}

Click "🌐 Open in Browser" button above to open the interface in your default web browser.

The search interface will open automatically in your browser shortly...

Note: To use the embedded browser view, install the webview package:
    pip install pywebview
                """)
                self.info_text.config(state=tk.DISABLED)

            # Auto-open in external browser
            time.sleep(0.5)
            self.open_in_external_browser()

    def on_server_failed(self):
        """Called when server fails to start"""
        self.status_label.config(text="❌ Server failed to start")
        messagebox.showerror(
            "Server Error",
            "Failed to start the search server.\n\n"
            "Make sure server.py is in the same directory and no other instance is running."
        )

    def on_server_error(self, error_msg):
        """Called when there's an error starting the server"""
        self.status_label.config(text="❌ Server error")
        messagebox.showerror("Error", f"Error starting server:\n{error_msg}")

    def launch_embedded_browser(self):
        """Launch embedded browser view"""
        def create_window():
            # Create webview window
            webview.create_window(
                'Document Search',
                self.server_url,
                width=1200,
                height=800,
                resizable=True,
                fullscreen=False
            )
            webview.start()

        # Hide the main window and launch webview
        self.root.withdraw()

        # Start webview in a separate thread
        browser_thread = threading.Thread(target=create_window, daemon=True)
        browser_thread.start()

    def refresh_browser(self):
        """Refresh the browser view"""
        if HAS_WEBVIEW:
            # Relaunch embedded browser
            self.launch_embedded_browser()
        else:
            self.open_in_external_browser()

    def open_in_external_browser(self):
        """Open the search interface in default web browser"""
        webbrowser.open(self.server_url)

    def on_closing(self):
        """Handle window close event"""
        # Stop the server
        if self.server_process:
            try:
                self.server_process.terminate()
                self.server_process.wait(timeout=5)
            except:
                self.server_process.kill()

        # Close the window
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = SearchGUI(root)

    # Only run mainloop if not using embedded browser
    if not HAS_WEBVIEW:
        root.mainloop()
    else:
        # Keep the root window alive but hidden
        root.after(100, lambda: None)
        root.mainloop()


if __name__ == '__main__':
    main()
