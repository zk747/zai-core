# ZAI Reader - Multi-Format Document Scanner

A Python module and FastAPI service for scanning directories and extracting text from .txt, .md, and .pdf files with comprehensive error handling and background task support.

## Features

✅ **Multi-Format Support**: Reads .txt, .md, and .pdf files  
✅ **Text Extraction**: Uses PyMuPDF for PDF processing  
✅ **Path Management**: Leverages pathlib for cross-platform compatibility  
✅ **FastAPI Integration**: Background tasks with status tracking  
✅ **Error Handling**: Comprehensive error handling with logging  
✅ **Word Counting**: Automatic word count for each document  
✅ **Encoding Detection**: Multiple encoding fallbacks for text files  
✅ **File Size Limits**: Configurable maximum file size restrictions  
✅ **Detailed Metadata**: Returns filename, path, size, and word count  

---

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Key Dependencies:
- **fastapi**: Web framework for building APIs
- **uvicorn**: ASGI server for running FastAPI
- **PyMuPDF (fitz)**: PDF text extraction
- **pydantic**: Data validation and serialization

### 2. Verify Installation

```bash
python -c "import fitz; print('PyMuPDF ready')"
python -c "import fastapi; print('FastAPI ready')"
```

---

## Module Usage: zai_reader.py

### Basic Usage

#### Method 1: Using the Convenience Function

```python
from zai_reader import scan_folder

# Simple folder scan
results = scan_folder('/data')

for doc in results:
    print(f"{doc['filename']}: {doc['words']} words")
```

#### Method 2: Using the DocumentReader Class

```python
from zai_reader import DocumentReader
from pathlib import Path

# Create reader instance with custom settings
reader = DocumentReader(max_file_size_mb=100, encoding='utf-8')

# Scan the folder
results = reader.scan_folder('/data')

# Get statistics
stats = reader.get_stats()
print(f"Files read: {stats['files_read']}")
print(f"Errors: {stats['errors_count']}")

# Access document data
for doc in results:
    print(f"File: {doc['filename']}")
    print(f"Words: {doc['words']}")
    print(f"Size: {doc['file_size_bytes']} bytes")
    print(f"Path: {doc['file_path']}")
    print(f"Preview: {doc['text'][:100]}...")
```

### Advanced Usage

#### Custom Error Handling

```python
from zai_reader import DocumentReader
from pathlib import Path

reader = DocumentReader(max_file_size_mb=50)

try:
    results = reader.scan_folder('/data')
except ValueError as e:
    print(f"Invalid path: {e}")
except PermissionError as e:
    print(f"Permission denied: {e}")

# Check for errors during processing
stats = reader.get_stats()
if stats['errors_count'] > 0:
    print("Errors encountered:")
    for error in stats['errors']:
        print(f"  - {error}")
```

#### Processing Specific File Types

```python
from zai_reader import DocumentReader
from pathlib import Path

reader = DocumentReader()
all_files = reader.scan_folder('/data')

# Filter by extension
pdf_files = [doc for doc in all_files if doc['filename'].endswith('.pdf')]
text_files = [doc for doc in all_files if doc['filename'].endswith(('.txt', '.md'))]

print(f"PDFs: {len(pdf_files)}, Text: {len(text_files)}")
```

#### Batch Processing with Statistics

```python
from zai_reader import DocumentReader
import json

reader = DocumentReader(max_file_size_mb=100)
results = reader.scan_folder('/data')

# Generate report
report = {
    'total_files': len(results),
    'total_words': sum(doc['words'] for doc in results),
    'total_bytes': sum(doc['file_size_bytes'] for doc in results),
    'documents': [
        {
            'name': doc['filename'],
            'words': doc['words'],
            'size_mb': doc['file_size_bytes'] / 1024 / 1024
        }
        for doc in results
    ]
}

print(json.dumps(report, indent=2))
```

---

## FastAPI Server: app.py

### Starting the Server

```bash
# Run with default settings
python app.py

# Or use uvicorn directly
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# For production
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

Access the interactive API documentation at: **http://localhost:8000/docs**

### API Endpoints

#### 1. Health Check
```
GET /
```

**Response:**
```json
{
  "status": "healthy",
  "service": "ZAI Reader API",
  "version": "1.0.0"
}
```

#### 2. Start Folder Scan (Background Task)
```
POST /read-folder
Content-Type: application/json

{
  "folder_path": "/data",
  "max_file_size_mb": 50
}
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "folder_path": "/data",
  "documents": null,
  "stats": null,
  "created_at": "2024-01-15T10:30:00.123456",
  "completed_at": null,
  "error": null
}
```

#### 3. Get Task Status
```
GET /read-folder/{task_id}
```

**Example:**
```bash
curl http://localhost:8000/read-folder/550e8400-e29b-41d4-a716-446655440000
```

**Response (Running):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "folder_path": "/data",
  "created_at": "2024-01-15T10:30:00.123456"
}
```

**Response (Completed):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "folder_path": "/data",
  "documents": [
    {
      "filename": "document.pdf",
      "text": "Full extracted text...",
      "words": 1260,
      "file_path": "/data/document.pdf",
      "file_size_bytes": 524288
    }
  ],
  "stats": {
    "files_read": 5,
    "errors_count": 0,
    "errors": []
  },
  "created_at": "2024-01-15T10:30:00.123456",
  "completed_at": "2024-01-15T10:35:00.654321",
  "error": null
}
```

#### 4. List All Tasks
```
GET /tasks
GET /tasks?status=completed
```

**Response:**
```json
{
  "total_tasks": 3,
  "tasks": {
    "550e8400-e29b-41d4-a716-446655440000": {
      "task_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "completed",
      "folder_path": "/data",
      "document_count": 5,
      "created_at": "2024-01-15T10:30:00.123456"
    }
  }
}
```

#### 5. Get Statistics
```
GET /stats
```

**Response:**
```json
{
  "total_tasks": 3,
  "completed_tasks": 2,
  "failed_tasks": 0,
  "total_documents": 12,
  "total_words": 45230
}
```

---

## Practical Examples

### Example 1: Python Script with Module

```python
from zai_reader import DocumentReader
import json
from pathlib import Path

def analyze_documents(folder_path):
    """Analyze documents in a folder and generate report."""
    reader = DocumentReader(max_file_size_mb=100)

    try:
        documents = reader.scan_folder(folder_path)

        # Generate statistics
        stats = {
            'total_files': len(documents),
            'total_words': sum(d['words'] for d in documents),
            'avg_words': sum(d['words'] for d in documents) / len(documents) if documents else 0,
            'largest_file': max(documents, key=lambda x: x['file_size_bytes']) if documents else None,
            'file_breakdown': {
                'pdfs': len([d for d in documents if d['filename'].endswith('.pdf')]),
                'text_files': len([d for d in documents if d['filename'].endswith('.txt')]),
                'markdown_files': len([d for d in documents if d['filename'].endswith('.md')])
            }
        }

        return stats, documents

    except Exception as e:
        print(f"Error: {e}")
        return None, []

# Usage
stats, docs = analyze_documents('/data')
if stats:
    print(json.dumps(stats, indent=2))
```

### Example 2: Using FastAPI with curl

```bash
# 1. Start a scan
RESPONSE=$(curl -X POST http://localhost:8000/read-folder \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/data", "max_file_size_mb": 50}')

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "Task ID: $TASK_ID"

# 2. Poll for status (repeat until completed)
curl http://localhost:8000/read-folder/$TASK_ID | jq .

# 3. Get statistics
curl http://localhost:8000/stats | jq .
```

### Example 3: Python Async with FastAPI Client

```python
import asyncio
import httpx
import time

async def scan_with_polling(folder_path: str):
    """Scan folder and poll for results."""
    async with httpx.AsyncClient() as client:
        # Start task
        response = await client.post(
            "http://localhost:8000/read-folder",
            json={"folder_path": folder_path, "max_file_size_mb": 50}
        )
        task_id = response.json()['task_id']
        print(f"Started task: {task_id}")

        # Poll until complete
        while True:
            status_response = await client.get(
                f"http://localhost:8000/read-folder/{task_id}"
            )
            task = status_response.json()

            if task['status'] in ['completed', 'failed']:
                return task

            print(f"Status: {task['status']}...")
            await asyncio.sleep(2)

# Usage
result = asyncio.run(scan_with_polling('/data'))
print(f"Completed: {len(result['documents'])} documents")
```

---

## Configuration

### DocumentReader Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_file_size_mb` | int | 50 | Maximum file size to process |
| `encoding` | str | 'utf-8' | Default encoding for text files |

### FastAPI Request Parameters

| Parameter | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `folder_path` | str | Yes | - | Absolute or relative path to folder |
| `max_file_size_mb` | int | No | 50 | Limit file processing size (1-1000 MB) |

---

## Error Handling

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: Folder path does not exist` | Invalid folder path | Verify path exists and is accessible |
| `PermissionError` | Insufficient permissions | Check folder read permissions |
| `UnicodeDecodeError` | Text file encoding issue | Module tries multiple encodings automatically |
| PDF extraction error | Corrupted PDF or no PyMuPDF | Install PyMuPDF: `pip install PyMuPDF` |
| Task not found (404) | Invalid task ID | Use correct task ID from initial response |

### Logging

All events are logged to console with levels:
- **DEBUG**: File read operations
- **INFO**: Task creation, folder scans, completion
- **WARNING**: Large files, unsupported formats
- **ERROR**: Processing failures, permission issues

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Performance Considerations

### Optimization Tips

1. **Batch Processing**: Process large folders in chunks
2. **File Size Limits**: Set appropriate `max_file_size_mb` to skip large files
3. **Encoding**: Specify correct encoding if known
4. **Timeout**: For very large folders, increase API request timeout
5. **Async Processing**: Use background tasks for non-blocking operations

### Benchmarks (Approximate)

- Small PDF (< 1 MB): ~50-100ms
- Large PDF (10 MB): ~500-1000ms
- Text file (any size): ~10-50ms
- Scanning 100 mixed files: ~5-10 seconds

---

## Troubleshooting

### PyMuPDF Installation Issues

```bash
# On Ubuntu/Debian
sudo apt-get install libfitz-dev
pip install PyMuPDF

# On macOS
brew install mupdf
pip install PyMuPDF

# On Windows
pip install PyMuPDF
```

### FastAPI Connection Refused

```bash
# Check if port 8000 is in use
lsof -i :8000

# Use different port
uvicorn app:app --port 8001
```

### Large File Processing Hangs

Reduce `max_file_size_mb` or increase system memory/timeout.

---

## Summary

The **ZAI Reader** module provides a robust, production-ready solution for scanning and extracting text from multiple document formats. The FastAPI integration enables scalable, background processing with comprehensive error handling and task tracking.
