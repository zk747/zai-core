
export interface ScannedFile {
  filename: string;
  word_count: number;
  status: 'Scanned' | 'Processing' | 'Complete' | 'Error';
}
