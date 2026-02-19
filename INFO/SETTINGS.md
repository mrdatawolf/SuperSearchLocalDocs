# Settings Configuration

The Document Search application now supports user-configurable settings through a web interface.

## Accessing Settings

Click the **⚙️ Settings** button in the top-right corner of the web interface.

## Available Settings

### Database Path
**Purpose**: Location of the SQLite database file containing indexed documents.

**Use Case**: Multiple users can point to a shared database on a network drive.

**Example**:
- Network path: `\\192.168.0.1\Shared Folders\Databases\documents.sqlite3`
- Local path: `C:\Data\documents.sqlite3`

### Document Path
**Purpose**: Root folder to scan when running the indexer.

**Note**: This setting is used by `indexer.py`, not by the search server.

**Example**:
- Network share: `\\192.168.0.1\Shared Folders`
- Local folder: `C:\Users\Public\Documents`

## How It Works

### Configuration Priority
1. **User Overrides** (stored in `user_config.json`) - Highest priority
2. **Default Values** (from `config.py`) - Fallback

### Storage
User settings are saved to `user_config.json` in the application directory. This file is automatically created when you save settings through the web interface.

**Example `user_config.json`**:
```json
{
    "database_path": "\\\\192.168.0.1\\Databases\\documents.sqlite3",
    "document_path": "\\\\192.168.0.1\\Shared Folders"
}
```

### Applying Changes
After saving settings:
1. The application will use the new settings immediately for future requests
2. Refresh your browser page to ensure all components use the new settings
3. The indexer will automatically use the new document path

## Multi-User Setup

To share a database across multiple computers:

1. **Place database on network share**:
   - Create folder: `\\192.168.0.1\Shared Folders\Databases\`
   - Copy `documents.sqlite3` to this location

2. **Configure each computer**:
   - Open Document Search in browser
   - Click **⚙️ Settings**
   - Set Database Path to: `\\192.168.0.1\Shared Folders\Databases\documents.sqlite3`
   - Click **Save Changes**
   - Refresh the page

3. **Index documents** (on one computer):
   - Set Document Path to your shared folders location
   - Run `python indexer.py`
   - All computers will see the updated index

## Resetting Settings

Click **Reset to Defaults** in the settings dialog to remove all overrides and use the default values from `config.py`.

## Programmatic Access

If you need to access settings from Python code:

```python
from config_manager import get_all_config, get_config

# Get all settings
config = get_all_config()
print(config['database_path'])

# Get a specific setting
db_path = get_config('database_path', 'default_value.sqlite3')
```

## Troubleshooting

### "Database file not found" error
- Ensure the path is correct and the file exists
- For network paths, ensure you have access permissions
- Use UNC paths (\\\\server\\share) not mapped drives (Z:\\)

### Settings don't apply
- Refresh your browser page after saving
- Check that `user_config.json` was created in the application directory
- Verify the JSON syntax in `user_config.json` is valid

### Can't access network database
- Ensure network share is accessible from your computer
- Try opening the path in Windows Explorer first
- Check file permissions on the network share
- Ensure the SQLite file isn't locked by another process

## For Developers

### Adding New Settings

1. **Add default in `config.py`**:
```python
NEW_SETTING = "default_value"
```

2. **Update `config_manager.py`**:
```python
def get_all_config():
    config = {
        'database_path': DATABASE_PATH,
        'server_host': SERVER_HOST,
        'server_port': SERVER_PORT,
        'document_path': DOCUMENT_PATH,
        'new_setting': NEW_SETTING  # Add here
    }
    # ...
```

3. **Add to settings API** in `server.py`:
```python
'defaults': {
    # ... existing defaults ...
    'new_setting': NEW_SETTING
}
```

4. **Add UI field** in `templates/index.html`:
```html
<div class="setting-item">
    <label for="settingNewSetting">New Setting</label>
    <input type="text" id="settingNewSetting">
    <div class="hint">Description of the setting</div>
</div>
```

5. **Handle in JavaScript**:
```javascript
// In loadSettings()
document.getElementById('settingNewSetting').value = currentSettings.new_setting || '';

// In saveSettings()
const newSettings = {
    // ... existing settings ...
    new_setting: document.getElementById('settingNewSetting').value.trim()
};
```
