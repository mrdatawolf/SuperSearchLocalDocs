# Quick Start Guide

Get your document search running in 3 simple steps!

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**Optional:** For image text extraction, install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

## Step 2: Index Your Documents

```bash
python indexer.py
```

This will scan `\\192.168.203.207\Shared Folders` and create a searchable database.

**To change the document location**, edit [config.py](../config.py) first.

## Step 3: Start Searching

```bash
python server.py
```

Then open your browser to: **http://127.0.0.1:9000**

## Tips

- **Update the index**: Just run `python indexer.py` again whenever you add new documents
- **Search tips**: Searches file names, folder names, AND document content automatically
  - Example: Search "Acronis" finds files in "Acronis Codes" folder, files named "AcronisAdmin.pdf", and documents mentioning Acronis
- **Open documents**: Click a result to copy its file path, then paste in Windows Explorer

## Troubleshooting

**Can't access network path?**
- Check that `\\192.168.203.207\Shared Folders` is accessible
- Update the path in [config.py](../config.py) if needed

**Database not found?**
- Run `python indexer.py` first

**Want to index local files instead?**
- Edit [config.py](../config.py) and change `DOCUMENT_PATH` to a local folder

---

For full documentation, see [README.md](../README.md)
