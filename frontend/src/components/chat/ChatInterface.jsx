/**
 * PATH: frontend/src/components/chat/ChatInterface.jsx
 * PURPOSE: ChatGPT-style conversational interface for Physics AI
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
  Loader2
} from 'lucide-react';
import { clsx } from 'clsx';

const suggestedPrompts = [
  { icon: Atom, text: "Simulate a simple harmonic oscillator" },
  { icon: Calculator, text: "Solve F = ma for acceleration" },
  { icon: BookOpen, text: "Explain the Schrödinger equation" },
  { icon: Lightbulb, text: "What physics models are available?" },
];

function MessageBubble({ message, isLast }) {
  const [copied, setCopied] = useState(false);
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
      'group flex gap-4 py-6 px-4 animate-fade-in',
      isUser ? 'bg-transparent' : 'bg-light-50'
    )}>
      {/* Avatar */}
      <div className={clsx(
        'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
        isUser 
          ? 'bg-gradient-to-br from-accent-purple to-accent-pink' 
          : 'bg-gradient-to-br from-accent-primary to-accent-blue'
      )}>
        {isUser ? <User size={16} className="text-white" /> : <Sparkles size={16} className="text-white" />}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-medium text-light-800 text-sm">
              {isUser ? 'You' : 'Physics AI'}
            </span>
            {!isUser && message.reasoning && (
              <span className="badge-blue text-[10px]">Reasoning</span>
            )}
          </div>
          
          <div className="text-light-700 prose prose-sm max-w-none">
            {message.isLoading ? (
              <div className="flex items-center gap-2 text-light-500">
                <Loader2 size={16} className="animate-spin" />
                <span>Thinking...</span>
              </div>
            ) : (
              <div className="whitespace-pre-wrap">{displayContent}</div>
            )}
          
          {message.code && (
            <div className="mt-3 relative">
              <pre className="code-block overflow-x-auto">
                <code>{message.code}</code>
              </pre>
              <button 
                onClick={() => navigator.clipboard.writeText(message.code)}
                className="absolute top-2 right-2 p-1.5 bg-light-700 hover:bg-light-600 rounded transition-colors"
              >
                <Copy size={14} className="text-light-300" />
              </button>
            </div>
          )}

          {message.simulation && (
            <div className="mt-3 p-4 bg-light-100 rounded-lg border border-light-300">
              <div className="flex items-center gap-2 mb-2">
                <Atom size={16} className="text-accent-primary" />
                <span className="text-sm font-medium text-light-800">Simulation Result</span>
              </div>
              <pre className="text-xs text-light-600 overflow-x-auto">
                {JSON.stringify(message.simulation, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Agent Metadata */}
        {!isUser && !message.isLoading && (message.model || message.latency) && (
          <div className="flex items-center gap-3 mt-2 text-xs text-light-400">
            {message.model && <span>Model: {message.model}</span>}
            {message.latency && <span>{Math.round(message.latency)}ms</span>}
            {message.tokens && <span>{message.tokens} tokens</span>}
            {message.provider && <span className="px-1.5 py-0.5 bg-light-200 rounded">{message.provider}</span>}
          </div>
        )}

        {/* Actions */}
        {!isUser && !message.isLoading && (
          <div className="flex items-center gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
            <button 
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2 py-1 text-xs text-light-500 hover:text-light-700 hover:bg-light-200 rounded transition-colors"
            >
              {copied ? <Check size={12} /> : <Copy size={12} />}
              {copied ? 'Copied' : 'Copy'}
            </button>
            <button className="flex items-center gap-1.5 px-2 py-1 text-xs text-light-500 hover:text-light-700 hover:bg-light-200 rounded transition-colors">
              <RefreshCw size={12} />
              Regenerate
            </button>
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
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full px-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-accent-primary to-accent-blue flex items-center justify-center mb-6">
              <Sparkles size={32} className="text-white" />
            </div>
            <h2 className="text-2xl font-semibold text-light-900 mb-2">Physics AI Assistant</h2>
            <p className="text-light-500 text-center max-w-md mb-8">
              Ask me about physics simulations, equations, or any scientific questions.
              I can help you run simulations, solve equations, and explore physics concepts.
            </p>

            {/* Suggestions */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-2xl">
              {suggestedPrompts.map((prompt, i) => (
                <button
                  key={i}
                  onClick={() => handleSuggestion(prompt.text)}
                  className="flex items-center gap-3 p-4 bg-light-50 hover:bg-light-100 border border-light-300 hover:border-light-400 rounded-xl text-left transition-all group"
                >
                  <div className="w-10 h-10 rounded-lg bg-light-200 group-hover:bg-accent-primary/10 flex items-center justify-center transition-colors">
                    <prompt.icon size={20} className="text-light-500 group-hover:text-accent-primary transition-colors" />
                  </div>
                  <span className="text-sm text-light-600 group-hover:text-light-800 transition-colors">
                    {prompt.text}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-3xl mx-auto">
            {messages.map((message, i) => (
              <MessageBubble 
                key={i} 
                message={message} 
                isLast={i === messages.length - 1} 
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-light-200 p-4 bg-light-50">
        <div className="max-w-3xl mx-auto">
          <div className="relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about physics, run simulations, or solve equations..."
              rows={1}
              className="w-full px-4 py-3 pr-12 bg-white border border-light-300 rounded-xl text-light-900 placeholder-light-400 resize-none focus:outline-none focus:border-accent-primary focus:ring-2 focus:ring-accent-primary/20 transition-all"
              style={{ minHeight: '52px', maxHeight: '200px' }}
            />
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
              className={clsx(
                'absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all',
                input.trim() && !isLoading
                  ? 'bg-accent-primary text-white hover:bg-accent-primary/90'
                  : 'bg-light-200 text-light-400 cursor-not-allowed'
              )}
            >
              {isLoading ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Send size={18} />
              )}
            </button>
          </div>
          <p className="text-xs text-light-400 text-center mt-2">
            Physics AI can make mistakes. Verify important calculations.
          </p>
        </div>
      </div>
    </div>
  );
}
