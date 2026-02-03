/**
 * PATH: frontend/src/components/chat/ChatInterface.jsx
 * PURPOSE: Wolfram-style conversational interface for Physics AI
 * 
 * FEATURES:
 * - Mathematical proof display with theorems/lemmas
 * - Code artifacts with syntax highlighting
 * - Improved typography and font sizing
 * - Step-by-step derivations
 * 
 * FLOW:
 * ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
 * │   Message   │───▶│   Process    │───▶│   Display   │
 * │    Input    │    │   via API    │    │   Response  │
 * └─────────────┘    └──────────────┘    └─────────────┘
 */

import { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Sparkles, 
  User, 
  Copy, 
  Check, 
  RefreshCw,
  Atom,
  BookOpen,
  Calculator,
  Lightbulb,
  Code,
  Loader2,
  ChevronDown,
  ChevronRight,
  Play,
  Download,
  ExternalLink,
  Zap
} from 'lucide-react';
import { clsx } from 'clsx';
import CodeCell from '../physics/CodeArtifact';
import { TheoremBlock, DerivationChain, MathBlock } from '../physics/ProofDisplay';

const suggestedPrompts = [
  { icon: Atom, text: "Derive the wave equation from first principles", category: "Theory" },
  { icon: Calculator, text: "Prove E = mc² using special relativity", category: "Proof" },
  { icon: BookOpen, text: "Show the Schrödinger equation derivation", category: "Quantum" },
  { icon: Lightbulb, text: "Explain Maxwell's equations with proofs", category: "E&M" },
  { icon: Zap, text: "Calculate escape velocity for Earth", category: "Mechanics" },
  { icon: Code, text: "Simulate a quantum harmonic oscillator", category: "Simulation" },
];

// Parse content for mathematical expressions and code blocks
function parseContent(content) {
  if (!content) return { text: '', math: [], code: [], proofs: [] };
  
  const text = typeof content === 'string' ? content : JSON.stringify(content, null, 2);
  
  // Extract LaTeX expressions (between $...$ or $$...$$)
  const mathRegex = /\$\$(.*?)\$\$|\$(.*?)\$/gs;
  const math = [...text.matchAll(mathRegex)].map(m => ({
    full: m[0],
    expression: m[1] || m[2],
    display: m[0].startsWith('$$')
  }));
  
  // Extract code blocks (```...```)
  const codeRegex = /```(\w+)?\n([\s\S]*?)```/g;
  const code = [...text.matchAll(codeRegex)].map(m => ({
    full: m[0],
    language: m[1] || 'python',
    code: m[2].trim()
  }));
  
  return { text, math, code, proofs: [] };
}

// Render mathematical content with proper formatting
function MathContent({ content }) {
  const parsed = parseContent(content);
  
  // Simple rendering - replace math expressions inline
  let displayText = parsed.text;
  
  // Render code blocks
  const codeBlocks = parsed.code.map((block, i) => (
    <div key={i} className="my-4">
      <CodeCell 
        code={block.code} 
        language={block.language}
        executionCount={i + 1}
      />
    </div>
  ));
  
  // Remove code blocks from text for display
  parsed.code.forEach(block => {
    displayText = displayText.replace(block.full, '');
  });
  
  return (
    <div className="math-content">
      {/* Text content with improved typography */}
      <div className="text-base leading-relaxed text-slate-700 whitespace-pre-wrap font-serif">
        {displayText.trim()}
      </div>
      
      {/* Code artifacts */}
      {codeBlocks.length > 0 && (
        <div className="mt-4 space-y-4">
          {codeBlocks}
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message, isLast }) {
  const [copied, setCopied] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const isUser = message.role === 'user';

  // Ensure content is always a string (safety check for React rendering)
  const getDisplayContent = () => {
    if (typeof message.content === 'string') {
      return message.content;
    }
    if (message.content === null || message.content === undefined) {
      return '';
    }
    // Handle object content - extract nested content or stringify
    if (typeof message.content === 'object') {
      if (message.content.content && typeof message.content.content === 'string') {
        return message.content.content;
      }
      if (message.content.result && typeof message.content.result === 'string') {
        return message.content.result;
      }
      return JSON.stringify(message.content, null, 2);
    }
    return String(message.content);
  };

  const displayContent = getDisplayContent();

  const handleCopy = () => {
    navigator.clipboard.writeText(displayContent);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={clsx(
      'group flex gap-5 py-8 px-6 animate-fade-in border-b border-slate-100',
      isUser ? 'bg-white' : 'bg-gradient-to-br from-slate-50 to-white'
    )}>
      {/* Avatar */}
      <div className={clsx(
        'w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm',
        isUser 
          ? 'bg-gradient-to-br from-indigo-500 to-purple-600' 
          : 'bg-gradient-to-br from-orange-500 to-red-500'
      )}>
        {isUser ? (
          <User size={20} className="text-white" />
        ) : (
          <span className="text-white font-bold text-lg">W</span>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-3 mb-3">
          <span className="font-semibold text-slate-900 text-lg">
            {isUser ? 'Input' : 'Physics AI'}
          </span>
          {!isUser && message.reasoning && (
            <span className="px-2 py-0.5 bg-blue-100 text-blue-700 text-xs font-medium rounded-full">
              Chain of Thought
            </span>
          )}
          {!isUser && !message.isLoading && (
            <button
              onClick={() => setShowDetails(!showDetails)}
              className="ml-auto text-xs text-slate-400 hover:text-slate-600 flex items-center gap-1"
            >
              {showDetails ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
              Details
            </button>
          )}
        </div>
          
        {/* Main Content */}
        <div className="prose prose-slate prose-lg max-w-none">
          {message.isLoading ? (
            <div className="flex items-center gap-3 text-slate-500 py-4">
              <div className="relative">
                <div className="w-8 h-8 border-2 border-orange-200 rounded-full animate-spin border-t-orange-500"></div>
              </div>
              <div>
                <span className="font-medium">Computing...</span>
                <p className="text-sm text-slate-400 mt-1">Analyzing physics principles and deriving solution</p>
              </div>
            </div>
          ) : (
            <MathContent content={displayContent} />
          )}
          
          {/* Code Artifact */}
          {message.code && !message.isLoading && (
            <div className="mt-6">
              <CodeCell 
                code={message.code} 
                language="python"
                executionCount={1}
              />
            </div>
          )}

          {/* Simulation Result */}
          {message.simulation && !message.isLoading && (
            <div className="mt-6">
              <TheoremBlock
                type="corollary"
                title="Simulation Result"
                statement={
                  <pre className="text-sm font-mono bg-slate-900 text-slate-100 p-4 rounded-lg overflow-x-auto">
                    {JSON.stringify(message.simulation, null, 2)}
                  </pre>
                }
              />
            </div>
          )}
        </div>

        {/* Detailed Metadata (collapsible) */}
        {!isUser && !message.isLoading && showDetails && (
          <div className="mt-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
            <h4 className="text-sm font-semibold text-slate-700 mb-3">Computation Details</h4>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              {message.model && (
                <div>
                  <span className="text-slate-400 block">Model</span>
                  <span className="font-mono text-slate-700">{message.model}</span>
                </div>
              )}
              {message.provider && (
                <div>
                  <span className="text-slate-400 block">Provider</span>
                  <span className="font-mono text-slate-700">{message.provider}</span>
                </div>
              )}
              {message.latency && (
                <div>
                  <span className="text-slate-400 block">Latency</span>
                  <span className="font-mono text-slate-700">{Math.round(message.latency)}ms</span>
                </div>
              )}
              {message.tokens && (
                <div>
                  <span className="text-slate-400 block">Tokens</span>
                  <span className="font-mono text-slate-700">{message.tokens}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        {!isUser && !message.isLoading && (
          <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-100">
            <button 
              onClick={handleCopy}
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors"
            >
              {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
              <Download size={14} />
              Export
            </button>
            <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
              <RefreshCw size={14} />
              Regenerate
            </button>
            <a 
              href="#" 
              className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors ml-auto"
            >
              <ExternalLink size={14} />
              Open in Notebook
            </a>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatInterface() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = { role: 'user', content: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Add loading message
    setMessages(prev => [...prev, { role: 'assistant', isLoading: true }]);

    try {
      // Call the DREAM Agents API
      const apiBase = window.location.hostname === 'localhost' 
        ? 'http://localhost:5002' 
        : `http://${window.location.hostname}`;
      
      const response = await fetch(`${apiBase}/api/v1/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: input.trim(),
          context: messages.slice(-4).map(m => `${m.role}: ${m.content}`).join('\n')
        }),
      });

      if (!response.ok) {
        throw new Error('API request failed');
      }

      const data = await response.json();
      
      // Extract response from DREAM agent format - handle various response structures
      const agentResponse = data.response || {};
      
      // Robust content extraction - ensure we always get a string
      const extractContent = (obj) => {
        if (typeof obj === 'string') return obj;
        if (!obj || typeof obj !== 'object') return String(obj || '');
        
        // Try various possible content locations
        if (typeof obj.content === 'string') return obj.content;
        if (typeof obj.result === 'string') return obj.result;
        if (typeof obj.message === 'string') return obj.message;
        if (typeof obj.text === 'string') return obj.text;
        
        // Nested content
        if (obj.content && typeof obj.content === 'object') {
          if (typeof obj.content.content === 'string') return obj.content.content;
          if (typeof obj.content.result === 'string') return obj.content.result;
        }
        
        // Last resort: stringify
        return JSON.stringify(obj, null, 2);
      };
      
      // Try multiple sources for content
      let content = "I've processed your request.";
      if (data.message && typeof data.message === 'string') {
        content = data.message;
      } else if (agentResponse) {
        content = extractContent(agentResponse);
      } else if (data.content) {
        content = extractContent(data);
      }
      
      // Remove loading message and add response
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: content,
          code: data.code,
          simulation: data.simulation,
          reasoning: data.reasoning,
          // Add agent metadata
          model: agentResponse.model || data.model,
          provider: agentResponse.provider || data.provider,
          latency: agentResponse.latency_ms || data.latency_ms,
          tokens: agentResponse.usage?.total_tokens || data.tokens,
        }
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      // Remove loading message and add error
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: `I apologize, but I'm having trouble connecting to the Physics AI backend.\n\nError: ${error.message}\n\nPlease ensure the server is running. The Physics AI system includes:\n\n- **DREAM Agents**: Multi-layer AI (Gatekeeper, Workhorse, Orchestrator)\n- **522 Physics Equations** across 19 domains\n- **Simulations**: Quantum, Classical, Astrophysics\n- **Knowledge Graph**: Relational physics concepts`,
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (text) => {
    setInput(text);
    inputRef.current?.focus();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] bg-white">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full px-6 py-12">
            {/* Logo */}
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center mb-8 shadow-lg">
              <span className="text-white font-bold text-4xl">W</span>
            </div>
            
            {/* Title */}
            <h1 className="text-4xl font-bold text-slate-900 mb-3 tracking-tight">
              Physics AI
            </h1>
            <p className="text-xl text-slate-500 text-center max-w-2xl mb-2 font-light">
              Computational Physics Engine
            </p>
            <p className="text-base text-slate-400 text-center max-w-xl mb-12">
              Ask questions, derive proofs, run simulations, and explore physics through 
              natural language. Powered by 561+ equations across 19 domains.
            </p>

            {/* Suggestions */}
            <div className="w-full max-w-4xl">
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-4 text-center">
                Try asking
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {suggestedPrompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => handleSuggestion(prompt.text)}
                    className="group flex flex-col p-5 bg-gradient-to-br from-slate-50 to-white border border-slate-200 hover:border-orange-300 hover:shadow-md rounded-xl text-left transition-all"
                  >
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-8 h-8 rounded-lg bg-slate-100 group-hover:bg-orange-100 flex items-center justify-center transition-colors">
                        <prompt.icon size={16} className="text-slate-400 group-hover:text-orange-600 transition-colors" />
                      </div>
                      <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                        {prompt.category}
                      </span>
                    </div>
                    <span className="text-base text-slate-700 group-hover:text-slate-900 transition-colors leading-snug">
                      {prompt.text}
                    </span>
                  </button>
                ))}
              </div>
            </div>
            
            {/* Capabilities */}
            <div className="mt-12 flex flex-wrap justify-center gap-6 text-sm text-slate-400">
              <span className="flex items-center gap-2">
                <Atom size={16} className="text-blue-400" />
                Quantum Mechanics
              </span>
              <span className="flex items-center gap-2">
                <Zap size={16} className="text-yellow-500" />
                Electromagnetism
              </span>
              <span className="flex items-center gap-2">
                <Calculator size={16} className="text-green-500" />
                Classical Mechanics
              </span>
              <span className="flex items-center gap-2">
                <BookOpen size={16} className="text-purple-500" />
                Thermodynamics
              </span>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto">
            {messages.map((message, i) => (
              <MessageBubble 
                key={i} 
                message={message} 
                isLast={i === messages.length - 1} 
              />
            ))}
            <div ref={messagesEndRef} className="h-8" />
          </div>
        )}
      </div>

      {/* Input Area - Wolfram Style */}
      <div className="border-t border-slate-200 bg-gradient-to-t from-slate-50 to-white p-6">
        <div className="max-w-4xl mx-auto">
          <div className="relative">
            <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
              <span className="text-orange-500 font-bold text-lg">=</span>
            </div>
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Enter physics query, equation, or natural language question..."
              rows={1}
              className="w-full pl-12 pr-14 py-4 bg-white border-2 border-slate-200 hover:border-slate-300 focus:border-orange-400 rounded-xl text-lg text-slate-800 placeholder-slate-400 resize-none focus:outline-none focus:ring-4 focus:ring-orange-100 transition-all font-light"
              style={{ minHeight: '60px', maxHeight: '200px' }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className={clsx(
                'absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-lg transition-all',
                input.trim() && !isLoading
                  ? 'bg-orange-500 text-white hover:bg-orange-600 shadow-md'
                  : 'bg-slate-100 text-slate-400 cursor-not-allowed'
              )}
            >
              {isLoading ? (
                <Loader2 size={20} className="animate-spin" />
              ) : (
                <Play size={20} className="ml-0.5" />
              )}
            </button>
          </div>
          <div className="flex items-center justify-between mt-3 text-xs text-slate-400">
            <span>
              Press <kbd className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-500 font-mono">Enter</kbd> to compute
            </span>
            <span>
              Powered by Physics AI Knowledge Graph • 561 equations • 19 domains
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
