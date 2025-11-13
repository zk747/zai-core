
import React, { useState, useCallback } from 'react';
import type { ScannedFile } from '../types';
import { SpinnerIcon } from './icons/SpinnerIcon';

const MemoryEngine: React.FC = () => {
  const [folderPath, setFolderPath] = useState<string>('');
  const [files, setFiles] = useState<ScannedFile[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleScan = useCallback(async () => {
    if (!folderPath) {
      setError('Please enter a folder path.');
      return;
    }
    setIsLoading(true);
    setError(null);
    setFiles([]);

    try {
      const response = await fetch('http://localhost:8000/read-folder', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ folder_path: folderPath }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (!data.files || !Array.isArray(data.files)) {
        throw new Error("Invalid response format from server.");
      }

      const scannedFiles: ScannedFile[] = data.files.map((file: any) => ({
        filename: file.filename,
        word_count: file.word_count,
        status: 'Scanned',
      }));

      setFiles(scannedFiles);
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(`Failed to scan folder: ${err.message}`);
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [folderPath]);
  
  const TableRow: React.FC<{ file: ScannedFile }> = ({ file }) => (
    <tr className="border-b border-slate-700 hover:bg-slate-800 transition-colors duration-150">
      <td className="py-3 px-4 text-slate-300 font-mono text-sm">{file.filename}</td>
      <td className="py-3 px-4 text-slate-300 text-center">{file.word_count}</td>
      <td className="py-3 px-4 text-center">
        <span className="bg-green-800/50 text-green-300 text-xs font-medium px-2.5 py-1 rounded-full">
          {file.status}
        </span>
      </td>
    </tr>
  );


  return (
    <div className="bg-slate-800/50 backdrop-blur-sm border border-slate-700 rounded-lg shadow-2xl p-6 md:p-8">
      <h1 className="text-3xl md:text-4xl font-bold text-center mb-6 text-slate-100">
        🧠 ZAI Memory Engine
      </h1>

      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <input
          type="text"
          value={folderPath}
          onChange={(e) => setFolderPath(e.target.value)}
          placeholder="/path/to/your/folder"
          className="flex-grow bg-slate-900 border border-slate-600 rounded-md px-4 py-2 text-slate-300 placeholder-slate-500 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition-all duration-200"
          disabled={isLoading}
        />
        <button
          onClick={handleScan}
          disabled={isLoading || !folderPath}
          className="flex items-center justify-center bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-600 disabled:cursor-not-allowed text-white font-semibold px-6 py-2 rounded-md transition-all duration-200 shadow-md disabled:shadow-none"
        >
          {isLoading ? (
            <>
              <SpinnerIcon className="w-5 h-5 mr-2" />
              Scanning...
            </>
          ) : (
            'Scan'
          )}
        </button>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-3 rounded-md mb-6" role="alert">
          <p>{error}</p>
        </div>
      )}

      <div className="overflow-x-auto bg-slate-900/70 rounded-md border border-slate-700">
        <table className="w-full min-w-max text-left">
          <thead className="bg-slate-700/50">
            <tr>
              <th className="py-3 px-4 font-semibold text-slate-300">Filename</th>
              <th className="py-3 px-4 font-semibold text-slate-300 text-center">Word Count</th>
              <th className="py-3 px-4 font-semibold text-slate-300 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {!isLoading && files.length > 0 && files.map((file) => (
              <TableRow key={file.filename} file={file} />
            ))}
          </tbody>
        </table>
        
        {!isLoading && files.length === 0 && (
            <div className="text-center py-12 text-slate-500">
              <p>Enter a folder path and click "Scan" to see file data.</p>
            </div>
        )}
        {isLoading && (
             <div className="text-center py-12 text-slate-500 flex items-center justify-center">
               <SpinnerIcon className="w-6 h-6 mr-3" />
               <p>Loading file data...</p>
            </div>
        )}
      </div>
    </div>
  );
};

export default MemoryEngine;
