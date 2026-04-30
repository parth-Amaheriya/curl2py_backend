import * as React from 'react';
import { useState, useEffect } from 'react';
import { 
  Play, 
  History, 
  Settings, 
  HelpCircle, 
  Copy, 
  CheckCircle2, 
  Terminal, 
  ChevronRight,
  Loader2,
  Trash2,
  Plus
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { transpileCurlToPython } from './services/geminiService';
import { RequestItem } from './types';

const INITIAL_REQUESTS: RequestItem[] = [
  {
    id: '1',
    name: 'req_1.py',
    curl: 'curl -X POST https://api.example.com/v1/auth \\\n  -H "Content-Type: application/json" \\\n  -d \'{"username": "admin", "password": "password123"}\'',
    python: '',
    status: 'idle',
    method: 'POST',
    endpoint: 'api.example.com',
    format: 'JSON'
  },
  {
    id: '2',
    name: 'req_2.py',
    curl: 'curl -H "Authorization: Bearer token_abc123" \\\n  https://api.example.com/v1/users?status=active',
    python: '',
    status: 'idle',
    method: 'GET',
    endpoint: 'api.example.com',
    format: 'URL'
  }
];

export default function App() {
  const [requests, setRequests] = useState<RequestItem[]>(INITIAL_REQUESTS);
  const [activeIndex, setActiveIndex] = useState(0);
  const [isConverting, setIsConverting] = useState(false);
  const [copyFeedback, setCopyFeedback] = useState(false);

  const activeRequest = requests[activeIndex];

  const handleConvert = async () => {
    if (!activeRequest || isConverting) return;

    setIsConverting(true);
    setRequests(prev => prev.map((r, i) => i === activeIndex ? { ...r, status: 'converting' } : r));

    try {
      const result = await transpileCurlToPython(activeRequest.curl);
      setRequests(prev => prev.map((r, i) => i === activeIndex ? { 
        ...r, 
        python: result.python, 
        status: 'completed',
        method: result.method || r.method,
        endpoint: result.endpoint || r.endpoint,
        format: result.format || r.format
      } : r));
    } catch (error) {
      setRequests(prev => prev.map((r, i) => i === activeIndex ? { ...r, status: 'error' } : r));
    } finally {
      setIsConverting(false);
    }
  };

  const handleCopy = () => {
    if (!activeRequest.python) return;
    navigator.clipboard.writeText(activeRequest.python);
    setCopyFeedback(true);
    setTimeout(() => setCopyFeedback(false), 2000);
  };

  const updateCurl = (val: string) => {
    setRequests(prev => prev.map((r, i) => i === activeIndex ? { ...r, curl: val } : r));
  };

  const addNewRequest = () => {
    const newId = (requests.length + 1).toString();
    const newReq: RequestItem = {
      id: newId,
      name: `req_${newId}.py`,
      curl: 'curl https://api.example.com',
      python: '',
      status: 'idle',
      method: 'GET'
    };
    setRequests(prev => [...prev, newReq]);
    setActiveIndex(requests.length);
  };

  return (
    <div className="h-screen flex flex-col bg-brand-bg select-none overflow-hidden font-mono text-sm">
      {/* Top Bar */}
      <header className="h-12 border-b border-brand-border flex items-center justify-between px-4 bg-stone-950 shrink-0 z-20">
        <div className="flex items-center gap-4">
          <span className="font-bold text-brand-primary tracking-widest text-lg">CURL_TRANSPILLER</span>
        </div>

        <div className="flex items-center gap-3">
          <button 
            onClick={handleConvert}
            disabled={isConverting}
            className="flex items-center gap-2 bg-brand-primary-container text-brand-primary-on-container px-4 py-1.5 rounded-brand hover:brightness-110 active:scale-95 transition-all text-xs font-bold uppercase disabled:opacity-50"
          >
            {isConverting ? <Loader2 size={14} className="animate-spin" /> : <Play size={14} fill="currentColor" />}
            {isConverting ? 'Converting...' : 'Convert'}
          </button>

          <div className="h-6 w-[1px] bg-brand-border mx-1" />

          <div className="flex items-center gap-1">
            <ToolButton icon={<History size={18} />} />
            <ToolButton icon={<Settings size={18} />} />
            <ToolButton icon={<HelpCircle size={18} />} />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Panel: Input */}
        <section className="w-1/2 flex flex-col border-r border-brand-border bg-stone-950/50">
          <div className="h-8 border-b border-brand-border bg-brand-surface-low flex items-center px-4 justify-between shrink-0">
            <span className="text-[10px] font-bold text-brand-text/60 uppercase tracking-widest">INPUT</span>
            <span className="text-[10px] text-brand-text/40">{requests.length} requests detected</span>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-8">
            {requests.map((req, idx) => (
              <div 
                key={req.id} 
                className={`group relative flex flex-col gap-3 transition-opacity ${activeIndex === idx ? 'opacity-100' : 'opacity-40 hover:opacity-100 cursor-pointer'}`}
                onClick={() => setActiveIndex(idx)}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold text-brand-text/40 uppercase tracking-widest">Request {idx + 1}</span>
                  {idx === activeIndex && (
                    <motion.div layoutId="active-indicator" className="w-1.5 h-1.5 bg-brand-primary rounded-full shadow-[0_0_8px_rgba(172,208,172,0.8)]" />
                  )}
                </div>
                
                <textarea
                  value={req.curl}
                  onChange={(e) => updateCurl(e.target.value)}
                  readOnly={activeIndex !== idx}
                  className="w-full bg-brand-surface p-4 rounded-brand border border-brand-border font-mono text-[13px] leading-relaxed text-brand-text focus:outline-none focus:border-brand-primary/50 resize-none min-h-[100px]"
                  placeholder="Paste cURL command here..."
                  spellCheck={false}
                />

                {idx < requests.length - 1 && (
                  <div className="absolute -bottom-4 left-0 w-full h-[1px] bg-brand-border/30" />
                )}
              </div>
            ))}
            
            <button 
              onClick={addNewRequest}
              className="w-full h-24 border border-dashed border-brand-border rounded-brand flex flex-col items-center justify-center gap-2 text-brand-text/30 hover:text-brand-primary hover:border-brand-primary/50 transition-colors group"
            >
              <Plus size={24} className="group-hover:scale-110 transition-transform" />
              <span className="text-[10px] uppercase font-bold tracking-widest">Add New Request</span>
            </button>
          </div>
        </section>

        {/* Right Panel: Output */}
        <section className="w-1/2 flex flex-col bg-brand-bg">
          {/* Tabs */}
          <div className="h-8 border-b border-brand-border bg-brand-surface flex shrink-0">
            {requests.map((req, idx) => (
              <button
                key={req.id}
                onClick={() => setActiveIndex(idx)}
                className={`h-full px-4 flex items-center border-r border-brand-border font-bold text-[10px] transition-all tracking-wide ${
                  activeIndex === idx 
                    ? 'bg-brand-bg text-brand-primary border-t-2 border-t-brand-primary' 
                    : 'text-brand-text/40 hover:bg-brand-surface-low hover:text-brand-text'
                }`}
              >
                [{req.name}]
              </button>
            ))}
          </div>

          {/* Editor Body */}
          <div className="flex-1 overflow-hidden flex flex-col p-6">
            {/* Metadata Bar */}
            <div className="flex justify-between items-center mb-4 bg-brand-surface-low border border-brand-border rounded-brand px-3 py-2 shrink-0">
              <div className="flex items-center gap-3 text-[10px] font-bold tracking-widest">
                <span className="bg-brand-surface-high text-brand-text px-2 py-0.5 rounded-sm">{activeRequest.method || 'GET'}</span>
                <span className="text-brand-border text-xs">|</span>
                <span className="text-brand-text/60">{activeRequest.endpoint || '...'}</span>
                <span className="text-brand-border text-xs">|</span>
                <span className="bg-brand-surface-high text-brand-text px-2 py-0.5 rounded-sm">{activeRequest.format || '...'}</span>
              </div>
              
              <button 
                onClick={handleCopy}
                disabled={!activeRequest.python}
                className="flex items-center gap-2 border border-brand-border rounded-brand px-3 py-1 text-[10px] font-bold text-brand-text/60 hover:text-brand-primary hover:border-brand-primary active:scale-95 transition-all disabled:opacity-30 disabled:pointer-events-none"
              >
                {copyFeedback ? <CheckCircle2 size={12} className="text-brand-primary" /> : <Copy size={12} />}
                {copyFeedback ? 'COPIED' : 'COPY'}
              </button>
            </div>

            {/* Code Block */}
            <div className="flex-1 bg-brand-surface rounded-brand border border-brand-border p-6 overflow-auto relative group">
              <AnimatePresence mode="wait">
                {activeRequest.status === 'idle' && !activeRequest.python && (
                  <motion.div 
                    key="idle"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 flex flex-col items-center justify-center text-brand-text/20 pointer-events-none"
                  >
                    <Terminal size={48} strokeWidth={1} className="mb-4 opacity-5" />
                    <p className="text-[10px] font-bold tracking-[0.3em] uppercase">Awaiting Conversion</p>
                  </motion.div>
                )}

                {activeRequest.status === 'converting' && (
                  <motion.div 
                    key="working"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="absolute inset-0 flex items-center justify-center bg-brand-bg/50 backdrop-blur-[1px] z-10"
                  >
                    <div className="flex flex-col items-center gap-4">
                      <div className="relative">
                        <div className="absolute inset-0 bg-brand-primary/20 blur-xl rounded-full animate-pulse" />
                        <Loader2 size={32} className="text-brand-primary animate-spin relative" />
                      </div>
                      <p className="text-[10px] font-bold tracking-[0.5em] text-brand-primary animate-pulse uppercase">Transpiling...</p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              <pre className="font-mono text-[13px] leading-relaxed whitespace-pre-wrap break-all overflow-x-hidden">
                <code className="text-brand-text">
                  {formatPythonCode(activeRequest.python)}
                </code>
              </pre>
            </div>
          </div>
        </section>
      </main>

      {/* Footer / Status Bar */}
      <footer className="h-8 bg-stone-900 border-t border-brand-border flex items-center px-4 shrink-0 font-bold text-[10px] text-brand-text/40 tracking-[0.2em]">
        <div className="flex items-center gap-6 h-full">
          <div className="flex items-center gap-2 text-brand-primary h-full border-r border-brand-border pr-6">
            <div className="w-2 h-2 bg-brand-primary rounded-full animate-pulse" />
            READY
          </div>
          <div className="flex items-center gap-2 h-full border-r border-brand-border pr-6 opacity-60 hover:opacity-100 transition-opacity cursor-default">
            V1.0.4
          </div>
          <div className="flex items-center gap-2 h-full opacity-60 hover:opacity-100 transition-opacity cursor-default">
            UTF-8
          </div>
        </div>
        
        <div className="flex-1" />
        
        <div className="flex items-center gap-4 text-[9px] opacity-40">
          <span>{activeRequest.python.length} Chars</span>
          <span>Ln 1, Col 1</span>
        </div>
      </footer>
    </div>
  );
}

function ToolButton({ icon }: { icon: React.ReactNode }) {
  return (
    <button className="p-1.5 text-brand-text/40 hover:text-brand-primary hover:bg-brand-surface rounded-brand transition-all active:scale-90">
      {icon}
    </button>
  );
}

function formatPythonCode(code: string) {
  if (!code) return '';
  
  // Basic syntax coloring logic
  return code.split(/(\n|\s+)/).map((segment, i) => {
    if (['import', 'from', 'with', 'as', 'def', 'return', 'if', 'else', 'elif', 'for', 'while', 'print', 'try', 'except', 'finally', 'with', 'class', 'self', 'None', 'True', 'False', 'in', 'is', 'not', 'and', 'or'].includes(segment.trim())) {
      return <span key={i} className="code-syntax-keyword">{segment}</span>;
    }
    if (segment.startsWith('"') || segment.startsWith("'")) {
      return <span key={i} className="code-syntax-string">{segment}</span>;
    }
    if (segment.trim().startsWith('#')) {
      return <span key={i} className="code-syntax-comment">{segment}</span>;
    }
    return segment;
  });
}
