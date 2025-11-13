# ZAI Reader - Quick Reference

## Installation

```bash
pip install -r requirements.txt
```

## Module: zai_reader.py

### Quick Start

```python
from zai_reader import scan_folder

results = scan_folder('/data')
```

### Return Format

```python
[
  {
    'filename': 'document.pdf',
    'text': 'Full extracted text...',
    'words': 1260,
    'file_path': '/data/document.pdf',
    'file_size_bytes': 524288
  }
]
```

### Common Operations

| Task | Code |
|------|------|
| **Count files** | `len(results)` |
| **Total words** | `sum(d['words'] for d in results)` |
| **Filter PDFs** | `[d for d in results if d['filename'].endswith('.pdf')]` |
| **Get stats** | `reader.get_stats()` |
| **Custom size limit** | `DocumentReader(max_file_size_mb=100)` |

---

## FastAPI: app.py

### Start Server

```bash
python app.py
# Open: http://localhost:8000/docs
```

### API Requests

**Start Scan (POST)**
```bash
curl -X POST http://localhost:8000/read-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/data", "max_file_size_mb": 50}'
```

**Get Status (GET)**
```bash
curl http://localhost:8000/read-folder/{task_id}
```

**List Tasks (GET)**
```bash
curl http://localhost:8000/tasks
curl "http://localhost:8000/tasks?status=completed"
```

**Get Stats (GET)**
```bash
curl http://localhost:8000/stats
```

---

## Status Values

- `pending`: Task queued
- `running`: Currently processing
- `completed`: Successfully finished
- `failed`: Error occurred

---

## Files Included

| File | Purpose |
|------|---------|
| `zai_reader.py` | Core module with DocumentReader class |
| `app.py` | FastAPI application with endpoints |
| `requirements.txt` | Python dependencies |
| `USAGE_GUIDE.md` | Detailed documentation |
| `simple_scan.py` | Basic usage example |
| `batch_processor.py` | Multi-folder processing |
| `api_client.py` | API client example |

---

## Environment Variables

Optional settings (can be hardcoded):
```bash
export FOLDER_PATH="/data"
export MAX_FILE_SIZE_MB=50
export API_HOST="0.0.0.0"
export API_PORT=8000
```

---

## Performance Tips

1. Process large folders in chunks
2. Set appropriate file size limits
3. Use background tasks for real-time responsiveness
4. Monitor logs for errors

---

## Support

- Check logs: stderr shows detailed error messages
- Verify PyMuPDF: `python -c "import fitz; print('OK')"`
- Test module: `python zai_reader.py`
- Check API: http://localhost:8000/docs

---

## Version Info

- **Python**: 3.10+
- **FastAPI**: 0.104.1+
- **PyMuPDF**: 1.23.8+
- **Pydantic**: 2.5.0+

Last Updated: 2024-01-15
