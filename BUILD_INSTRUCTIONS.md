# Building Standalone Executables

This guide explains how to create self-contained Windows applications that don't require Python to be installed.

## Overview

SuperSearch Local Docs consists of **two standalone executables**:

1. **DocumentIndexer.exe** - GUI application for setup, configuration, and indexing
2. **DocumentSearch.exe** - Web server for searching documents

Both work together but are deployed as separate applications.

## Quick Start

### Prerequisites (Build Computer Only)

You only need Python on the computer where you're building the executables:

```bash
# Install build tool
pip install pyinstaller

# Install dependencies
pip install -r requirements.txt
```

### Build Both Applications

**Recommended:** Build both executables at once:

```bash
python build_all.py
```

This creates:
- `dist\DocumentIndexer\` - Complete GUI indexer application
- `dist\DocumentSearch\` - Complete search server application

### Build Individually (Optional)

If you need to build just one:

```bash
# Build GUI indexer only
python build_indexer_exe.py

# Build search server only
python build_exe.py
```

## What Gets Created

### DocumentIndexer Application

Located in `dist\DocumentIndexer\`:

```
DocumentIndexer\
├── DocumentIndexer.exe       # Main GUI application
├── _internal\                # Python runtime and dependencies
│   ├── python311.dll
│   ├── [various DLLs]
│   └── [library files]
├── config.py                 # Default configuration
├── config_manager.py         # Configuration management
├── indexer.py               # Indexing engine
└── company_abbreviations.py # Abbreviation system
```

**Purpose:**
- First-time setup and configuration
- Indexing documents
- Re-indexing when documents change
- Viewing database statistics

### DocumentSearch Application

Located in `dist\DocumentSearch\`:

```
DocumentSearch\
├── DocumentSearch.exe        # Main web server
├── _internal\                # Python runtime and dependencies
│   ├── python311.dll
│   ├── flask\
│   ├── [various DLLs]
│   └── [library files]
├── templates\                # Web interface
│   └── index.html
├── config.py                # Default configuration
├── config_manager.py        # Configuration management
└── company_abbreviations.py # Abbreviation system
```

**Purpose:**
- Running the search web server
- Providing the search interface
- Serving search results

## Deployment

### Single-User Deployment

**What to distribute:**
1. Copy both folders to target computer:
   ```
   C:\Program Files\SuperSearchDocs\
   ├── DocumentIndexer\
   └── DocumentSearch\
   ```

**User workflow:**
1. Run `DocumentIndexer.exe` to configure and index documents
2. Run `DocumentSearch.exe` to search documents
3. Re-run `DocumentIndexer.exe` when adding new documents

### Multi-User Deployment

**For the administrator computer:**
- Deploy both `DocumentIndexer` and `DocumentSearch` folders
- Use DocumentIndexer to maintain the shared database

**For end-user computers:**
- Deploy only the `DocumentSearch` folder
- Configure to point to the shared database

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed multi-user setup.**

## Build Configuration

### Directory vs Single-File Build

**Current setting:** `--onedir` (directory build, recommended)

**Advantages:**
- Faster startup time
- Smaller overall size (shared dependencies)
- Easier to update individual components
- Better compatibility

**To change to single-file:**
Edit `build_exe.py` or `build_indexer_exe.py` and change:
```python
'--onedir',  # Change to '--onefile' for single-file build
```

**Note:** Single-file builds are slower to start because they extract to a temporary directory each time.

### Customizing the Build

Edit the build scripts to customize:

**Icon:**
```python
'--icon=path/to/icon.ico',  # Replace NONE with icon path
```

**Hidden imports** (if modules aren't detected):
```python
'--hidden-import=module_name',
```

**Exclude modules** (to reduce size):
```python
'--exclude-module=module_name',
```

**Add data files:**
```python
'--add-data=source;destination',  # Windows
```

### Build Optimization

**For smaller executable size:**

1. **Remove unused dependencies** before building:
   - Review `requirements.txt`
   - Remove packages you don't use
   - Rebuild

2. **Use UPX compression** (if available):
   - Download UPX from https://upx.github.io/
   - Add UPX to your PATH
   - PyInstaller will automatically use it

3. **Exclude specific modules:**
   ```python
   '--exclude-module=tkinter',  # If not needed in search server
   ```

## Post-Build Steps

### Testing the Build

Before distributing:

1. **Test DocumentIndexer.exe:**
   ```
   cd dist\DocumentIndexer
   DocumentIndexer.exe
   ```
   - Configure paths
   - Run a small index
   - Check for errors

2. **Test DocumentSearch.exe:**
   ```
   cd dist\DocumentSearch
   DocumentSearch.exe
   ```
   - Open browser to http://localhost:9000
   - Perform searches
   - Test all features

### Creating Distribution Package

**Option 1: ZIP file**
```bash
# Create ZIP files for distribution
powershell Compress-Archive -Path dist\DocumentIndexer -DestinationPath DocumentIndexer.zip
powershell Compress-Archive -Path dist\DocumentSearch -DestinationPath DocumentSearch.zip
```

**Option 2: Installer (Advanced)**
Use tools like:
- Inno Setup
- NSIS
- WiX Toolset

Create an installer that:
- Copies both applications
- Creates desktop shortcuts
- Adds to Start menu
- Sets up file associations (optional)

### Versioning

Add version information to your build:

1. Create `version.txt`:
   ```
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(1, 0, 0, 0),
       prodvers=(1, 0, 0, 0),
     ),
     ...
   )
   ```

2. Add to build script:
   ```python
   '--version-file=version.txt',
   ```

## Troubleshooting

### Build Issues

**"PyInstaller not installed"**
```bash
pip install pyinstaller
```

**"Module not found" during build**
- Add to `--hidden-import` in build script
- Ensure module is in requirements.txt
- Check import statements in code

**Build succeeds but exe crashes**
- Run exe from command line to see error messages
- Check for missing data files
- Verify all dependencies are bundled

### Runtime Issues

**"Failed to execute script"**
- Usually means a missing dependency
- Run from command prompt to see actual error
- Add missing modules to hidden imports

**"Database not found"**
- Ensure database path is configured correctly
- Use the Settings UI to set correct path
- Check file permissions

**Antivirus blocks or quarantines exe**
- This is common with PyInstaller executables
- Add exception in antivirus software
- Consider code signing certificate for distribution

**Slow startup**
- Normal for first run
- Consider using `--onedir` instead of `--onefile`
- Optimize by removing unused dependencies

### Size Issues

**Executable is too large**
- Remove unused packages from requirements.txt
- Use `--exclude-module` for unneeded modules
- Enable UPX compression
- Consider `--onefile` with compression

## Advanced Configuration

### Environment Variables

Set environment variables in the build:

```python
# Add to build script
'--runtime-tmpdir=/path/to/temp',
```

### Custom Build Location

Change output directory:

```python
# Add to PyInstaller arguments
'--distpath=custom/dist/path',
'--workpath=custom/work/path',
```

### Debug Build

For troubleshooting:

```python
# Add to build script
'--debug=all',  # Verbose debug output
'--console',    # Show console window even for GUI
```

### Multi-Platform Builds

**Note:** PyInstaller creates executables for the platform it runs on:
- Build on Windows → Windows .exe
- Build on Linux → Linux executable
- Build on Mac → Mac app

For cross-platform distribution, build on each target platform.

## Updating Executables

When you update the code:

1. **Pull latest changes** from repository
2. **Update dependencies** if needed:
   ```bash
   pip install -r requirements.txt --upgrade
   ```
3. **Rebuild executables:**
   ```bash
   python build_all.py
   ```
4. **Test thoroughly** before distributing
5. **Version your releases** (e.g., v1.1, v1.2)

## Distribution Checklist

Before distributing to users:

- [ ] Build both executables successfully
- [ ] Test DocumentIndexer.exe thoroughly
- [ ] Test DocumentSearch.exe thoroughly
- [ ] Test on clean Windows system (no Python)
- [ ] Create user documentation
- [ ] Package with README/instructions
- [ ] Create desktop shortcuts (optional)
- [ ] Add license information
- [ ] Version the release
- [ ] Test network/multi-user scenarios
- [ ] Verify antivirus compatibility
- [ ] Create backup/restore instructions

## Best Practices

1. **Version Control**: Tag releases in git before building
2. **Test Environment**: Test on clean Windows VM without Python
3. **Documentation**: Include DEPLOYMENT_GUIDE.md with distribution
4. **Shortcuts**: Provide .bat files or shortcuts for convenience
5. **Updates**: Plan for distributing updates to existing users
6. **Support**: Provide contact info for issues
7. **Backups**: Remind users to backup their databases

## File Size Reference

Approximate sizes (may vary):

- **DocumentIndexer**: ~50-80 MB (depending on dependencies)
- **DocumentSearch**: ~50-80 MB (depending on dependencies)
- **Combined**: ~100-160 MB

With UPX compression, sizes can be reduced by 30-40%.

## Security Considerations

### Code Signing

For professional distribution:

1. Obtain code signing certificate
2. Sign executables after build:
   ```bash
   signtool sign /f certificate.pfx /p password DocumentIndexer.exe
   ```

Benefits:
- Removes "Unknown Publisher" warnings
- Builds user trust
- Prevents tampering

### Antivirus False Positives

PyInstaller executables often trigger false positives:

**Solutions:**
- Submit to antivirus vendors for whitelisting
- Use code signing
- Build with latest PyInstaller version
- Avoid suspicious module names

## Support Resources

- PyInstaller documentation: https://pyinstaller.org/
- Python packaging guide: https://packaging.python.org/
- Windows code signing: https://docs.microsoft.com/windows/security/

## License Compliance

When distributing:

1. Include Python license (included by PyInstaller)
2. Include licenses for all dependencies
3. Add your own license for your code
4. Create LICENSES.txt with all attributions

PyInstaller automatically includes some licenses, but verify all are present.
