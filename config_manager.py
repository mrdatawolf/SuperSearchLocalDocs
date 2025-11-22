"""
Configuration manager that handles user settings overrides
"""
import json
from pathlib import Path
from config import DATABASE_PATH, SERVER_HOST, SERVER_PORT, DOCUMENT_PATH

# User config file location
USER_CONFIG_FILE = Path(__file__).parent / "user_config.json"

def load_user_config():
    """Load user configuration overrides from JSON file"""
    if USER_CONFIG_FILE.exists():
        try:
            with open(USER_CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user config: {e}")
            return {}
    return {}

def save_user_config(config_data):
    """Save user configuration to JSON file"""
    try:
        with open(USER_CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving user config: {e}")
        return False

def get_config(key, default=None):
    """Get a config value, checking user overrides first"""
    user_config = load_user_config()
    return user_config.get(key, default)

def get_all_config():
    """Get all configuration values with user overrides applied"""
    # Start with defaults from config.py
    config = {
        'database_path': DATABASE_PATH,
        'server_host': SERVER_HOST,
        'server_port': SERVER_PORT,
        'document_path': DOCUMENT_PATH
    }

    # Apply user overrides
    user_config = load_user_config()
    config.update(user_config)

    return config

def reset_to_defaults():
    """Reset to default configuration by removing user overrides"""
    if USER_CONFIG_FILE.exists():
        USER_CONFIG_FILE.unlink()
    return True
