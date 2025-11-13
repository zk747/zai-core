#!/usr/bin/env python3
"""
Simple example: Scan a folder and print results.
Usage: python simple_scan.py /path/to/folder
"""

import sys
from pathlib import Path
from zai_reader import scan_folder
import json

def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_scan.py /path/to/folder")
        sys.exit(1)

    folder = sys.argv[1]
    print(f"Scanning: {folder}")
    print("-" * 50)

    results = scan_folder(folder)

    for doc in results:
        print(f"📄 {doc['filename']}")
        print(f"   Words: {doc['words']}")
        print(f"   Size: {doc['file_size_bytes'] / 1024:.1f} KB")
        print(f"   Preview: {doc['text'][:60]}...")
        print()

    print(f"\nTotal: {len(results)} documents")

if __name__ == "__main__":
    main()
