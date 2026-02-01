/**
 * PATH: frontend/src/components/panels/RightDrawer.jsx
 * PURPOSE: Right side drawer for AI chat (Cursor-style)
 * 
 * FEATURES:
 * - Compact chat interface
 * - Quick actions
 * - Context-aware suggestions
 * - Resizable width
 */

import { useState, useRef, useEffect } from 'react';
import {
  Send,
  Sparkles,
  User,
  X,
  Minimize2,
  Maximize2,
  Copy,
  Check,
  Loader2,
  MessageSquare,
  Atom,
  Calculator,
  Code,
  History,
  Trash2
} from 'lucide-react';
import { clsx } from 'clsx';

const quickActions = [
  { icon: Atom, label: 'Simulate', action: 'run simulation' },
  { icon: Calculator, label: 'Solve', action: 'solve equation' },
  { icon: Code, label: 'Explain', action: 'explain this' },
];

function MiniMessage({ message }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className={clsx(
      'group py-3 px-3',
      isUser ? 'bg-transparent' : 'bg-light-50'
    )}>
      <div className="flex gap-2">
        <div className={clsx(
          'w-6 h-6 rounded flex items-center justify-center flex-shrink-0',
          isUser
            ? 'bg-gradient-to-br from-accent-purple to-accent-pink'
            : 'bg-gradient-to-br from-accent-primary to-accent-blue'
        )}>
          {isUser ? <User size={12} className="text-white" /> : <Sparkles size={12} className="text-white" />}
        </div>
        <div className="flex-1 min-w-0">
          <div className="text-xs font-medium text-light-600 mb-0.5">
            {isUser ? 'You' : 'Physics AI'}
          </div>
          {message.isLoading ? (
            <div className="flex items-center gap-1.5 text-light-500 text-sm">
              <Loader2 size={12} className="animate-spin" />
              <span>Thinking...</span>
            </div>
          ) : (
            <div className="text-sm text-light-700 whitespace-pre-wrap break-words">
              {message.content}
            </div>
          )}
        </div>
        {!isUser && !message.isLoading && (
          <button
            onClick={handleCopy}
            className="opacity-0 group-hover:opacity-100 p-1 hover:bg-light-200 rounded transition-all"
          >
            {copied ? <Check size={12} className="text-green-500" /> : <Copy size={12} className="text-light-400" />}
          </button>
        )}
      </div>
    </div>
  );
}

export default function RightDrawer({ onClose, onMaximize, isMaximized }) {
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

    setMessages(prev => [...prev, { role: 'assistant', isLoading: true }]);

    try {
      const response = await fetch('http://localhost:5002/api/v1/substrate/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input.trim() }),
      });

      if (!response.ok) throw new Error('API error');

      const data = await response.json();
      
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: data.response || data.message || "I've processed your request.",
        }
      ]);
    } catch (error) {
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: "I'm having trouble connecting. Make sure the API is running on port 5002.",
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

  const handleQuickAction = (action) => {
    setInput(action);
    inputRef.current?.focus();
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="h-full flex flex-col bg-white border-l border-light-200">
      {/* Header */}
      <div className="flex items-center justify-between px-3 py-2 border-b border-light-200 bg-light-50">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 rounded bg-gradient-to-br from-accent-primary to-accent-blue flex items-center justify-center">
            <MessageSquare size={12} className="text-white" />
          </div>
          <span className="font-medium text-sm text-light-800">AI Assistant</span>
        </div>
        <div className="flex items-center gap-1">
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="p-1.5 hover:bg-light-200 rounded transition-colors"
              title="Clear chat"
            >
              <Trash2 size={14} className="text-light-500" />
            </button>
          )}
          <button
            onClick={onMaximize}
            className="p-1.5 hover:bg-light-200 rounded transition-colors"
            title={isMaximized ? 'Minimize' : 'Maximize'}
          >
            {isMaximized ? <Minimize2 size={14} className="text-light-500" /> : <Maximize2 size={14} className="text-light-500" />}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-light-200 rounded transition-colors"
            title="Close"
          >
            <X size={14} className="text-light-500" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="p-4 text-center">
            <div className="w-10 h-10 mx-auto rounded-xl bg-gradient-to-br from-accent-primary to-accent-blue flex items-center justify-center mb-3">
              <Sparkles size={20} className="text-white" />
            </div>
            <h3 className="text-sm font-medium text-light-800 mb-1">Physics AI</h3>
            <p className="text-xs text-light-500 mb-4">
              Ask questions, run simulations, or solve equations
            </p>
            
            {/* Quick Actions */}
            <div className="flex flex-wrap gap-2 justify-center">
              {quickActions.map((action, i) => (
                <button
                  key={i}
                  onClick={() => handleQuickAction(action.action)}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 bg-light-100 hover:bg-light-200 border border-light-300 rounded-lg text-xs text-light-600 transition-colors"
                >
                  <action.icon size={12} />
                  {action.label}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, i) => (
              <MiniMessage key={i} message={message} />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="p-2 border-t border-light-200 bg-light-50">
        <div className="relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything..."
            rows={1}
            className="w-full px-3 py-2 pr-10 bg-white border border-light-300 rounded-lg text-sm text-light-900 placeholder-light-400 resize-none focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary/20"
            style={{ minHeight: '36px', maxHeight: '120px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={clsx(
              'absolute right-1.5 top-1/2 -translate-y-1/2 p-1.5 rounded transition-all',
              input.trim() && !isLoading
                ? 'bg-accent-primary text-white hover:bg-accent-primary/90'
                : 'bg-light-200 text-light-400 cursor-not-allowed'
            )}
          >
            {isLoading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
          </button>
        </div>
      </div>
    </div>
  );
}
