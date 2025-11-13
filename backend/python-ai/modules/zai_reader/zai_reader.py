"""
zai_reader.py - Multi-format document reader module

This module provides functionality to scan directories for text documents
(.txt, .md, .pdf) and extract their content for further processing.

Classes:
    DocumentReader: Main class for reading and processing documents

Functions:
    scan_folder: Scan a folder for supported document types
    extract_text_from_pdf: Extract text from PDF files
    extract_text_from_plaintext: Extract text from .txt/.md files
"""

from pathlib import Path
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass

try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False
    logging.warning("PyMuPDF (fitz) not installed. PDF reading disabled.")


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentStats:
    """Data class to hold document statistics."""
    filename: str
    text: str
    words: int
    file_path: Path
    file_size_bytes: int
    encoding: Optional[str] = None


class DocumentReader:
    """
    A class to read and process multiple document formats.

    Supported formats: .txt, .md, .pdf

    Attributes:
        supported_formats (tuple): File extensions supported by this reader
        max_file_size_mb (int): Maximum file size to process in MB
    """

    SUPPORTED_FORMATS = ('.txt', '.md', '.pdf')
    MAX_FILE_SIZE_MB = 50

    def __init__(self, max_file_size_mb: int = 50, encoding: str = 'utf-8'):
        """
        Initialize the DocumentReader.

        Args:
            max_file_size_mb (int): Maximum file size to process in MB.
                                   Defaults to 50.
            encoding (str): Default encoding for text files. Defaults to 'utf-8'.
        """
        self.max_file_size_mb = max_file_size_mb
        self.encoding = encoding
        self.files_read = 0
        self.errors = []

    def scan_folder(self, folder_path: str | Path) -> List[Dict]:
        """
        Scan a folder for supported document types and extract their content.

        This method recursively searches for .txt, .md, and .pdf files within
        the specified folder and returns a list of dictionaries containing
        filename, extracted text, and word count.

        Args:
            folder_path (str | Path): Path to the folder to scan.

        Returns:
            List[Dict]: A list of dictionaries with keys:
                - filename: Name of the file
                - text: Extracted text content
                - words: Number of words in the text
                - file_path: Full path to the file
                - file_size_bytes: Size of the file in bytes

        Raises:
            ValueError: If the folder path does not exist.
            PermissionError: If permission is denied to read the folder.

        Examples:
            >>> reader = DocumentReader()
            >>> results = reader.scan_folder('/path/to/documents')
            >>> for doc in results:
            ...     print(f"{doc['filename']}: {doc['words']} words")
        """
        folder_path = Path(folder_path)

        if not folder_path.exists():
            raise ValueError(f"Folder path does not exist: {folder_path}")

        if not folder_path.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        logger.info(f"Starting folder scan: {folder_path}")

        results = []
        self.files_read = 0
        self.errors = []

        try:
            # Recursively find all supported file types
            file_patterns = [f"**/*{ext}" for ext in self.SUPPORTED_FORMATS]
            files_to_process = []

            for pattern in file_patterns:
                files_to_process.extend(folder_path.glob(pattern))

            logger.info(f"Found {len(files_to_process)} supported files")

            for file_path in files_to_process:
                try:
                    doc_data = self._process_file(file_path)
                    if doc_data:
                        results.append(doc_data)
                        self.files_read += 1
                except Exception as e:
                    error_msg = f"Error processing {file_path.name}: {str(e)}"
                    logger.error(error_msg)
                    self.errors.append(error_msg)

            logger.info(
                f"Scan complete: {self.files_read} files processed, "
                f"{len(self.errors)} errors"
            )

        except PermissionError as e:
            logger.error(f"Permission denied accessing folder: {folder_path}")
            raise

        return results

    def _process_file(self, file_path: Path) -> Optional[Dict]:
        """
        Process a single file and extract its content.

        Args:
            file_path (Path): Path to the file to process.

        Returns:
            Optional[Dict]: Dictionary with file data or None if processing fails.
        """
        file_suffix = file_path.suffix.lower()

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size_mb * 1024 * 1024:
            logger.warning(
                f"File {file_path.name} exceeds max size "
                f"({file_size / 1024 / 1024:.2f} MB)"
            )
            return None

        # Route to appropriate handler
        if file_suffix == '.pdf':
            if not HAS_FITZ:
                logger.error(f"PDF processing disabled for {file_path.name}")
                return None
            text = self._extract_pdf(file_path)
        elif file_suffix in ('.txt', '.md'):
            text = self._extract_plaintext(file_path)
        else:
            logger.warning(f"Unsupported file type: {file_suffix}")
            return None

        if text is None:
            return None

        word_count = len(text.split())

        return {
            'filename': file_path.name,
            'text': text,
            'words': word_count,
            'file_path': str(file_path),
            'file_size_bytes': file_size
        }

    def _extract_pdf(self, file_path: Path) -> Optional[str]:
        """
        Extract text from a PDF file using PyMuPDF.

        Args:
            file_path (Path): Path to the PDF file.

        Returns:
            Optional[str]: Extracted text or None if extraction fails.
        """
        if not HAS_FITZ:
            logger.error("PyMuPDF not available for PDF extraction")
            return None

        try:
            doc = fitz.open(file_path)
            text = ""

            for page_num, page in enumerate(doc):
                page_text = page.get_text()
                text += page_text

            doc.close()
            logger.debug(f"Extracted {len(text)} characters from {file_path.name}")
            return text

        except Exception as e:
            logger.error(f"PDF extraction error for {file_path.name}: {e}")
            raise

    def _extract_plaintext(self, file_path: Path) -> Optional[str]:
        """
        Extract text from .txt or .md files.

        This method tries multiple encodings if UTF-8 fails.

        Args:
            file_path (Path): Path to the text file.

        Returns:
            Optional[str]: Extracted text or None if extraction fails.
        """
        encodings = [self.encoding, 'utf-8', 'latin-1', 'cp1252']

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                logger.debug(
                    f"Successfully read {file_path.name} with encoding {encoding}"
                )
                return text
            except (UnicodeDecodeError, LookupError):
                continue

        logger.error(f"Could not decode {file_path.name} with any encoding")
        raise UnicodeDecodeError(
            'unknown', b'', 0, 1,
            f"Unable to decode {file_path.name}"
        )

    def get_stats(self) -> Dict:
        """
        Get statistics about the last scan operation.

        Returns:
            Dict: Dictionary containing scan statistics and errors.
        """
        return {
            'files_read': self.files_read,
            'errors_count': len(self.errors),
            'errors': self.errors
        }


def scan_folder(folder_path: str | Path) -> List[Dict]:
    """
    Convenience function to scan a folder using default settings.

    Args:
        folder_path (str | Path): Path to the folder to scan.

    Returns:
        List[Dict]: List of dictionaries with document data.

    Examples:
        >>> results = scan_folder('/data')
        >>> for doc in results:
        ...     print(f"{doc['filename']}: {doc['words']} words")
    """
    reader = DocumentReader()
    return reader.scan_folder(folder_path)


if __name__ == "__main__":
    # Example usage
    import json

    test_folder = Path("/data")
    if test_folder.exists():
        reader = DocumentReader()
        results = reader.scan_folder(test_folder)
        print(json.dumps(results, indent=2))
        print(f"\nStats: {reader.get_stats()}")
    else:
        print(f"Test folder {test_folder} does not exist")
