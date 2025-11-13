# ZAI Reader - Reference Card

## Installation
```bash
pip install -r requirements.txt
```

## Module Usage

### Basic Import
```python
from zai_reader import scan_folder
results = scan_folder('/data')
```

### Advanced Configuration
```python
from zai_reader import DocumentReader
reader = DocumentReader(max_file_size_mb=100)
results = reader.scan_folder('/data')
stats = reader.get_stats()
```

## API Endpoints

### Health Check
```bash
GET /
```

### Start Scan
```bash
POST /read-folder
Content-Type: application/json

{
  "folder_path": "/data",
  "max_file_size_mb": 50
}
```

### Get Task Status
```bash
GET /read-folder/{task_id}
```

### List Tasks
```bash
GET /tasks
GET /tasks?status=completed
```

### Get Statistics
```bash
GET /stats
```

## Starting Services

### Development
```bash
# Module testing
python zai_reader.py

# API server
python app.py
```

### Production
```bash
# With Gunicorn
gunicorn app:app --workers 4

# With Uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

## Common Tasks

### Count Documents in Folder
```python
from zai_reader import scan_folder
results = scan_folder('/data')
print(f"Found {len(results)} documents")
```

### Get Total Words
```python
total_words = sum(doc['words'] for doc in results)
print(f"Total words: {total_words:,}")
```

### Filter by File Type
```python
pdfs = [d for d in results if d['filename'].endswith('.pdf')]
texts = [d for d in results if d['filename'].endswith(('.txt', '.md'))]
```

### Export to JSON
```python
import json
with open('documents.json', 'w') as f:
    json.dump(results, f, indent=2)
```

### Process with Error Handling
```python
from zai_reader import DocumentReader

reader = DocumentReader()
try:
    results = reader.scan_folder('/data')
except ValueError as e:
    print(f"Path error: {e}")
except PermissionError as e:
    print(f"Permission error: {e}")

# Check for errors
if reader.get_stats()['errors_count'] > 0:
    for error in reader.get_stats()['errors']:
        print(f"Error: {error}")
```

## Return Format

Each document is a dictionary:
```python
{
    'filename': 'example.pdf',           # Filename with extension
    'text': 'Full text content...',      # Complete extracted text
    'words': 1260,                       # Number of words
    'file_path': '/data/example.pdf',    # Full file path
    'file_size_bytes': 524288            # File size in bytes
}
```

## Task Status Values
- `pending`: Queued, not yet started
- `running`: Currently being processed
- `completed`: Successfully finished
- `failed`: Error occurred during processing

## Configuration Options

### DocumentReader
- `max_file_size_mb`: Max file size to process (default: 50)
- `encoding`: Text file encoding (default: 'utf-8')

### FastAPI
- `host`: Listen address (default: 0.0.0.0)
- `port`: Port number (default: 8000)
- `workers`: Number of workers (default: 1, recommended: CPU count)

## File Size Guidelines
- Small files: < 1 MB (instant processing)
- Medium files: 1-10 MB (seconds)
- Large files: 10-50 MB (tens of seconds)
- Very large: > 50 MB (consider adjusting limits)

## Supported Formats
- `.txt` - Plain text files
- `.md` - Markdown files
- `.pdf` - PDF documents (requires PyMuPDF)

## Performance Tips
1. Use batch processing for multiple folders
2. Set appropriate file size limits
3. Use background tasks for API
4. Monitor CPU and memory usage
5. Scale horizontally for production

## Troubleshooting

### PyMuPDF Installation Issues
```bash
# Ubuntu/Debian
sudo apt-get install libfitz-dev
pip install --upgrade PyMuPDF

# macOS
brew install mupdf
pip install PyMuPDF

# Windows
pip install PyMuPDF
```

### Port Already in Use
```bash
# Find process on port 8000
lsof -i :8000

# Use different port
uvicorn app:app --port 8001
```

### Encoding Errors
```python
# Try different encoding
reader = DocumentReader(encoding='latin-1')
results = reader.scan_folder('/data')
```

### Permission Denied
```bash
# Check folder permissions
ls -la /data

# Grant read permission
chmod -R 755 /data
```

## API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Example Workflows

### Workflow 1: Quick Local Scan
```python
from zai_reader import scan_folder
results = scan_folder('/home/user/documents')
for doc in results:
    print(f"{doc['filename']}: {doc['words']} words")
```

### Workflow 2: Background API Scan
```bash
# Start scan
TASK_ID=$(curl -X POST http://localhost:8000/read-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/data"}' | jq -r '.task_id')

# Poll for results
curl http://localhost:8000/read-folder/$TASK_ID | jq .
```

### Workflow 3: Batch Multi-Folder Processing
```python
from zai_reader import DocumentReader

folders = ['/data1', '/data2', '/data3']
reader = DocumentReader()

for folder in folders:
    results = reader.scan_folder(folder)
    print(f"{folder}: {len(results)} documents")
```

## Key Files Reference
- **zai_reader.py**: Core module
- **app.py**: FastAPI application
- **README.md**: Full project overview
- **USAGE_GUIDE.md**: Comprehensive guide
- **API_DOCUMENTATION.md**: API details
- **DEPLOYMENT_GUIDE.md**: Production setup

## Useful Commands

```bash
# Test module
python -c "from zai_reader import scan_folder; print(scan_folder('.'))"

# Start API
python app.py

# Health check
curl http://localhost:8000/

# API documentation
curl http://localhost:8000/openapi.json | jq .

# Test with curl
curl -X POST http://localhost:8000/read-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "."}'
```

## Version Information
- **Python**: 3.10+
- **FastAPI**: 0.104.1+
- **PyMuPDF**: 1.23.8+
- **Pydantic**: 2.5.0+

## Support Resources
- Check README.md for overview
- Read USAGE_GUIDE.md for examples
- Review API_DOCUMENTATION.md for endpoints
- Follow DEPLOYMENT_GUIDE.md for production
- View PROJECT_SUMMARY.md for complete details

---

**Last Updated**: 2024-01-15  
**Version**: 1.0.0
