#!/usr/bin/env python3
"""
Batch processor: Scan multiple folders and save results to JSON.
"""

from zai_reader import DocumentReader
from pathlib import Path
import json
from datetime import datetime

def process_multiple_folders(folder_list):
    """Process multiple folders and compile report."""
    reader = DocumentReader(max_file_size_mb=100)

    report = {
        'timestamp': datetime.now().isoformat(),
        'folders': {},
        'summary': {
            'total_folders': len(folder_list),
            'total_documents': 0,
            'total_words': 0,
            'failed_folders': []
        }
    }

    for folder_path in folder_list:
        try:
            print(f"Processing: {folder_path}")
            documents = reader.scan_folder(folder_path)

            folder_stats = {
                'document_count': len(documents),
                'total_words': sum(d['words'] for d in documents),
                'documents': [
                    {
                        'name': d['filename'],
                        'words': d['words'],
                        'size_kb': d['file_size_bytes'] / 1024
                    }
                    for d in documents
                ]
            }

            report['folders'][str(folder_path)] = folder_stats
            report['summary']['total_documents'] += len(documents)
            report['summary']['total_words'] += sum(d['words'] for d in documents)

        except Exception as e:
            report['summary']['failed_folders'].append({
                'path': str(folder_path),
                'error': str(e)
            })

    return report

if __name__ == "__main__":
    folders = ['/data', './documents', '/home/user/files']
    result = process_multiple_folders(folders)

    with open('scan_report.json', 'w') as f:
        json.dump(result, f, indent=2)

    print("\nReport saved to: scan_report.json")
    print(json.dumps(result['summary'], indent=2))
