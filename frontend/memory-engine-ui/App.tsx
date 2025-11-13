
import React from 'react';
import MemoryEngine from './components/MemoryEngine';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center p-4 font-sans">
      <div className="w-full max-w-4xl">
        <MemoryEngine />
      </div>
    </div>
  );
};

export default App;
