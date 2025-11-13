"""
FastAPI application that uses zai_reader.py for background folder scanning.

This module demonstrates how to integrate the DocumentReader into a FastAPI
application with background tasks, task status tracking, and JSON endpoints.

Endpoints:
    GET /: Health check
    POST /read-folder: Start a background folder scan
    GET /read-folder/{task_id}: Get task status and results
    GET /tasks: List all tasks
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid
import logging
from datetime import datetime
from enum import Enum

# Import the DocumentReader from zai_reader module
from zai_reader import DocumentReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    """Enum for task statuses."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class FolderScanRequest(BaseModel):
    """Request model for folder scanning."""
    folder_path: str = Field(..., description="Path to folder to scan")
    max_file_size_mb: int = Field(
        50,
        description="Maximum file size to process in MB",
        ge=1,
        le=1000
    )


class DocumentData(BaseModel):
    """Model for document data."""
    filename: str
    text: str
    words: int
    file_path: str
    file_size_bytes: int


class TaskResult(BaseModel):
    """Model for task results."""
    task_id: str
    status: TaskStatus
    folder_path: Optional[str] = None
    documents: Optional[List[DocumentData]] = None
    stats: Optional[Dict] = None
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None


# Global task storage (in production, use Redis or a database)
tasks_db: Dict[str, TaskResult] = {}


app = FastAPI(
    title="ZAI Reader API",
    description="Multi-format document reader with background tasks",
    version="1.0.0"
)


def process_folder_task(task_id: str, folder_path: str, max_file_size_mb: int):
    """
    Background task to process folder scanning.

    Args:
        task_id (str): Unique task identifier
        folder_path (str): Path to folder to scan
        max_file_size_mb (int): Maximum file size to process
    """
    try:
        logger.info(f"Task {task_id}: Starting folder scan for {folder_path}")
        tasks_db[task_id].status = TaskStatus.RUNNING

        # Initialize reader and scan
        reader = DocumentReader(max_file_size_mb=max_file_size_mb)
        results = reader.scan_folder(folder_path)

        # Convert results to DocumentData objects
        documents = [
            DocumentData(**{
                'filename': doc['filename'],
                'text': doc['text'],
                'words': doc['words'],
                'file_path': doc['file_path'],
                'file_size_bytes': doc['file_size_bytes']
            })
            for doc in results
        ]

        # Update task with results
        tasks_db[task_id].status = TaskStatus.COMPLETED
        tasks_db[task_id].documents = documents
        tasks_db[task_id].stats = reader.get_stats()
        tasks_db[task_id].completed_at = datetime.now().isoformat()

        logger.info(
            f"Task {task_id}: Completed. "
            f"Processed {len(documents)} documents"
        )

    except Exception as e:
        logger.error(f"Task {task_id}: Error - {str(e)}")
        tasks_db[task_id].status = TaskStatus.FAILED
        tasks_db[task_id].error = str(e)
        tasks_db[task_id].completed_at = datetime.now().isoformat()


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ZAI Reader API",
        "version": "1.0.0"
    }


@app.post("/read-folder", response_model=TaskResult, tags=["Scanning"])
async def read_folder(
    request: FolderScanRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a background task to scan a folder.

    This endpoint accepts a folder path and initiates a background task
    to scan and extract text from supported documents (.txt, .md, .pdf).

    Args:
        request (FolderScanRequest): Request containing folder path and options
        background_tasks (BackgroundTasks): FastAPI background tasks manager

    Returns:
        TaskResult: Initial task status with task ID

    Raises:
        HTTPException: If folder path is invalid

    Example:
        POST /read-folder
        {
            "folder_path": "/data",
            "max_file_size_mb": 50
        }
    """
    task_id = str(uuid.uuid4())

    # Create initial task record
    task_result = TaskResult(
        task_id=task_id,
        status=TaskStatus.PENDING,
        folder_path=request.folder_path,
        created_at=datetime.now().isoformat()
    )

    tasks_db[task_id] = task_result

    # Add background task
    background_tasks.add_task(
        process_folder_task,
        task_id,
        request.folder_path,
        request.max_file_size_mb
    )

    logger.info(f"Task {task_id} created for folder {request.folder_path}")

    return task_result


@app.get("/read-folder/{task_id}", response_model=TaskResult, tags=["Scanning"])
async def get_task_status(task_id: str):
    """
    Get the status and results of a folder scanning task.

    Args:
        task_id (str): Unique task identifier

    Returns:
        TaskResult: Current task status and results (if completed)

    Raises:
        HTTPException: If task not found

    Example:
        GET /read-folder/abc123def456
    """
    if task_id not in tasks_db:
        logger.warning(f"Task not found: {task_id}")
        raise HTTPException(
            status_code=404,
            detail=f"Task {task_id} not found"
        )

    return tasks_db[task_id]


@app.get("/tasks", tags=["Tasks"])
async def list_tasks(status: Optional[TaskStatus] = None):
    """
    List all tasks or filter by status.

    Args:
        status (Optional[TaskStatus]): Filter by task status

    Returns:
        Dict: List of tasks with summaries

    Example:
        GET /tasks
        GET /tasks?status=completed
    """
    if status:
        filtered_tasks = {
            task_id: {
                'task_id': task.task_id,
                'status': task.status,
                'folder_path': task.folder_path,
                'document_count': len(task.documents) if task.documents else 0,
                'created_at': task.created_at
            }
            for task_id, task in tasks_db.items()
            if task.status == status
        }
    else:
        filtered_tasks = {
            task_id: {
                'task_id': task.task_id,
                'status': task.status,
                'folder_path': task.folder_path,
                'document_count': len(task.documents) if task.documents else 0,
                'created_at': task.created_at
            }
            for task_id, task in tasks_db.items()
        }

    return {
        'total_tasks': len(filtered_tasks),
        'tasks': filtered_tasks
    }


@app.get("/stats", tags=["Statistics"])
async def get_stats():
    """
    Get overall statistics about all tasks.

    Returns:
        Dict: Statistics about completed tasks and documents
    """
    completed_tasks = [
        task for task in tasks_db.values()
        if task.status == TaskStatus.COMPLETED
    ]

    total_documents = sum(
        len(task.documents) if task.documents else 0
        for task in completed_tasks
    )

    total_words = sum(
        sum(doc.words for doc in task.documents)
        if task.documents else 0
        for task in completed_tasks
    )

    return {
        'total_tasks': len(tasks_db),
        'completed_tasks': len(completed_tasks),
        'failed_tasks': len([t for t in tasks_db.values() if t.status == TaskStatus.FAILED]),
        'total_documents': total_documents,
        'total_words': total_words
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting ZAI Reader API server...")
    print("Documentation available at: http://localhost:8000/docs")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
