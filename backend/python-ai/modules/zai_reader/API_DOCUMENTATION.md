# ZAI Reader API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
No authentication required (add as needed)

---

## Endpoints

### 1. Health Check

```
GET /
```

**Description**: Verify API is running

**Response** (200 OK):
```json
{
  "status": "healthy",
  "service": "ZAI Reader API",
  "version": "1.0.0"
}
```

---

### 2. Start Folder Scan

```
POST /read-folder
```

**Description**: Initiate background folder scan

**Request Body**:
```json
{
  "folder_path": "/data",
  "max_file_size_mb": 50
}
```

**Parameters**:
| Name | Type | Required | Default | Min | Max | Description |
|------|------|----------|---------|-----|-----|-------------|
| `folder_path` | string | Yes | - | - | - | Absolute or relative folder path |
| `max_file_size_mb` | integer | No | 50 | 1 | 1000 | Max file size to process in MB |

**Response** (200 OK):
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

**Example**:
```bash
curl -X POST http://localhost:8000/read-folder \
  -H "Content-Type: application/json" \
  -d '{
    "folder_path": "/data",
    "max_file_size_mb": 50
  }'
```

---

### 3. Get Task Status

```
GET /read-folder/{task_id}
```

**Description**: Retrieve task status and results (if completed)

**Path Parameters**:
| Name | Type | Description |
|------|------|-------------|
| `task_id` | string (UUID) | Unique task identifier from POST response |

**Response** (200 OK - Running):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "folder_path": "/data",
  "documents": null,
  "stats": null,
  "created_at": "2024-01-15T10:30:00.123456",
  "completed_at": null,
  "error": null
}
```

**Response** (200 OK - Completed):
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "folder_path": "/data",
  "documents": [
    {
      "filename": "document.pdf",
      "text": "Full extracted text content...",
      "words": 1260,
      "file_path": "/data/document.pdf",
      "file_size_bytes": 524288
    },
    {
      "filename": "readme.md",
      "text": "Markdown content here...",
      "words": 342,
      "file_path": "/data/readme.md",
      "file_size_bytes": 4096
    }
  ],
  "stats": {
    "files_read": 2,
    "errors_count": 0,
    "errors": []
  },
  "created_at": "2024-01-15T10:30:00.123456",
  "completed_at": "2024-01-15T10:35:00.654321",
  "error": null
}
```

**Response** (404 Not Found):
```json
{
  "detail": "Task 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

**Example**:
```bash
curl http://localhost:8000/read-folder/550e8400-e29b-41d4-a716-446655440000
```

---

### 4. List All Tasks

```
GET /tasks
GET /tasks?status=completed
```

**Description**: Get list of all tasks with optional filtering

**Query Parameters**:
| Name | Type | Required | Values | Description |
|------|------|----------|--------|-------------|
| `status` | string | No | pending, running, completed, failed | Filter by task status |

**Response** (200 OK):
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
    },
    "660e8400-e29b-41d4-a716-446655440001": {
      "task_id": "660e8400-e29b-41d4-a716-446655440001",
      "status": "running",
      "folder_path": "/home/user/documents",
      "document_count": 0,
      "created_at": "2024-01-15T10:45:00.234567"
    }
  }
}
```

**Examples**:
```bash
# Get all tasks
curl http://localhost:8000/tasks

# Get only completed tasks
curl "http://localhost:8000/tasks?status=completed"

# Get only running tasks
curl "http://localhost:8000/tasks?status=running"
```

---

### 5. Get Statistics

```
GET /stats
```

**Description**: Get overall statistics across all completed tasks

**Response** (200 OK):
```json
{
  "total_tasks": 5,
  "completed_tasks": 3,
  "failed_tasks": 0,
  "total_documents": 42,
  "total_words": 156789
}
```

**Example**:
```bash
curl http://localhost:8000/stats
```

---

## Response Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Request processed successfully |
| 404 | Not Found | Task ID doesn't exist |
| 422 | Validation Error | Invalid request parameters |
| 500 | Server Error | Internal processing error |

---

## Data Models

### TaskResult
```python
{
  "task_id": str,           # UUID
  "status": str,            # pending, running, completed, failed
  "folder_path": str,       # Path scanned
  "documents": List[Dict],  # Results (null until completed)
  "stats": Dict,            # Statistics (null until completed)
  "created_at": str,        # ISO timestamp
  "completed_at": str,      # ISO timestamp or null
  "error": str              # Error message or null
}
```

### DocumentData
```python
{
  "filename": str,          # e.g., "document.pdf"
  "text": str,              # Full extracted text
  "words": int,             # Word count
  "file_path": str,         # Full path to file
  "file_size_bytes": int    # File size in bytes
}
```

---

## Common Use Cases

### Use Case 1: Scan and Wait for Results

```python
import requests
import time

# Start scan
response = requests.post('http://localhost:8000/read-folder', 
    json={'folder_path': '/data'})
task_id = response.json()['task_id']

# Poll until complete
while True:
    status_resp = requests.get(f'http://localhost:8000/read-folder/{task_id}')
    task = status_resp.json()

    if task['status'] in ['completed', 'failed']:
        break

    print(f"Status: {task['status']}")
    time.sleep(2)

# Process results
if task['status'] == 'completed':
    for doc in task['documents']:
        print(f"{doc['filename']}: {doc['words']} words")
```

### Use Case 2: Batch Multiple Scans

```bash
# Scan multiple folders concurrently

FOLDERS=("/data" "/home/docs" "/backup/files")

for folder in "${FOLDERS[@]}"; do
  TASK_ID=$(curl -s -X POST http://localhost:8000/read-folder \
    -H "Content-Type: application/json" \
    -d "{"folder_path": "$folder"}" | jq -r '.task_id')
  echo "Started scan for $folder: $TASK_ID"
done

# Later, check all tasks
curl http://localhost:8000/tasks | jq .
```

### Use Case 3: Download All Documents

```python
import requests
import json

# Get task
task_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(f'http://localhost:8000/read-folder/{task_id}')
task = response.json()

# Export to JSON
with open('documents.json', 'w') as f:
    json.dump(task['documents'], f, indent=2)

# Or save individual files
for doc in task['documents']:
    filename = doc['filename'].replace('/', '_')
    with open(f"extracted_{filename}.txt", 'w') as f:
        f.write(doc['text'])
```

---

## Error Handling

### Error Response Example

```json
{
  "detail": "Task 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| Validation error | Invalid folder_path format | Use absolute or relative path |
| Task not found | Invalid task_id | Use correct UUID from response |
| Server error | Processing failure | Check logs, retry with valid path |

---

## Rate Limiting

Currently: No rate limiting (add as needed for production)

---

## Caching

Currently: No caching (same folder can be scanned multiple times)

---

## Versioning

API Version: 1.0.0
Python: 3.10+

---

## Support

For issues:
1. Check API docs: http://localhost:8000/docs
2. Enable debug logging in code
3. Check PyMuPDF installation
4. Verify folder permissions
