#!/usr/bin/env python3
"""
FastAPI client: Submit scan request and poll for results.
"""

import requests
import time
import json
import sys
from typing import Optional, Dict

class ZAIReaderClient:
    """Client for ZAI Reader API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def start_scan(self, folder_path: str, max_size_mb: int = 50) -> str:
        """Start a folder scan and return task ID."""
        response = requests.post(
            f"{self.base_url}/read-folder",
            json={
                "folder_path": folder_path,
                "max_file_size_mb": max_size_mb
            }
        )
        response.raise_for_status()
        return response.json()['task_id']

    def get_task_status(self, task_id: str) -> Dict:
        """Get status of a task."""
        response = requests.get(f"{self.base_url}/read-folder/{task_id}")
        response.raise_for_status()
        return response.json()

    def wait_for_completion(self, task_id: str, timeout: int = 600, poll_interval: int = 2):
        """Poll until task completes."""
        start_time = time.time()

        while time.time() - start_time < timeout:
            task = self.get_task_status(task_id)

            if task['status'] in ['completed', 'failed']:
                return task

            print(f"Status: {task['status']}... (elapsed: {int(time.time() - start_time)}s)")
            time.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")

def main():
    if len(sys.argv) < 2:
        print("Usage: python api_client.py /path/to/folder")
        sys.exit(1)

    folder = sys.argv[1]
    client = ZAIReaderClient()

    print(f"Starting scan for: {folder}")
    task_id = client.start_scan(folder)
    print(f"Task ID: {task_id}")

    print("\nWaiting for completion...")
    result = client.wait_for_completion(task_id)

    if result['status'] == 'completed':
        print(f"✓ Scan complete!")
        print(f"  Documents: {len(result['documents'])}")
        print(f"  Total words: {sum(d['words'] for d in result['documents'])}")

        for doc in result['documents'][:5]:
            print(f"  - {doc['filename']}: {doc['words']} words")
    else:
        print(f"✗ Scan failed: {result['error']}")

if __name__ == "__main__":
    main()
