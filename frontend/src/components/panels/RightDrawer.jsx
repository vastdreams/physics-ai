/**
 * PATH: frontend/src/components/panels/RightDrawer.jsx
 * PURPOSE: Enhanced right side drawer with CoT visualization and proper formatting
 * 
 * FEATURES:
 * - Proper markdown and LaTeX rendering
 * - Chain of Thought flowchart display
 * - First principles explanations
 * - Copy functionality with formatted output
 * - Agentic flow visualization
 * 
 * FLOW:
 * ┌─────────────┐    ┌──────────────┐    ┌─────────────┐
 * │   User      │───▶│   API Call   │───▶│   Display   │
 * │   Query     │    │   + Parse    │    │   Results   │
 * └─────────────┘    └──────────────┘    └─────────────┘
 *                           │
 *                           ▼
 *                    ┌──────────────┐
 *                    │   Show CoT   │
 *                    │   Flowchart  │
 *                    └──────────────┘
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
  Trash2,
  ChevronDown,
  ChevronRight,
  Brain,
  Zap,
  FileText,
  GitBranch
} from 'lucide-react';
import { clsx } from 'clsx';
import { API_BASE } from '../../config';
import MarkdownRenderer from '../chat/MarkdownRenderer';
import ReasoningFlowChart from '../chat/ReasoningFlowChart';
import QualityBadge from '../chat/QualityBadge';

const quickActions = [
  { icon: Atom, label: 'Simulate', action: 'run simulation for ' },
  { icon: Calculator, label: 'Solve', action: 'solve equation: ' },
  { icon: Code, label: 'Explain', action: 'explain in first principles: ' },
  { icon: Brain, label: 'Derive', action: 'derive step by step: ' },
];

/**
 * Message component with proper formatting and CoT display
 */
function DrawerMessage({ message, showReasoning = true }) {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [showCoT, setShowCoT] = useState(false);

  // Ensure content is always a string
  const getDisplayContent = () => {
    if (typeof message.content === 'string') return message.content;
    if (message.content === null || message.content === undefined) return '';
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
    setTimeout(() => setCopied(false), 1500);
  };

  return (
    <div className={clsx(
      'group py-4 px-4 border-b border-slate-100',
      isUser ? 'bg-white' : 'bg-gradient-to-br from-slate-50 to-white'
    )}>
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className={clsx(
          'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
          isUser
            ? 'bg-gradient-to-br from-indigo-500 to-purple-600'
            : 'bg-gradient-to-br from-orange-500 to-red-500'
        )}>
          {isUser ? (
            <User size={14} className="text-white" />
          ) : (
            <span className="text-white font-bold text-sm">W</span>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-slate-700">
              {isUser ? 'You' : 'Beyond Frontier'}
            </span>
            
            {!isUser && !message.isLoading && (
              <div className="flex items-center gap-1">
                {message.reasoning && showReasoning && (
                  <button
                    onClick={() => setShowCoT(!showCoT)}
                    className={clsx(
                      'text-xs px-2 py-0.5 rounded flex items-center gap-1 transition-colors',
                      showCoT 
                        ? 'bg-purple-100 text-purple-700' 
                        : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                    )}
                  >
                    <Brain size={10} />
                    CoT
                    {showCoT ? <ChevronDown size={10} /> : <ChevronRight size={10} />}
                  </button>
                )}
                {message.quality && (
                  <QualityBadge quality={message.quality} compact={true} />
                )}
                <button
                  onClick={handleCopy}
                  className="p-1 opacity-0 group-hover:opacity-100 hover:bg-slate-100 rounded transition-all"
                  title="Copy"
                >
                  {copied ? (
                    <Check size={12} className="text-green-500" />
                  ) : (
                    <Copy size={12} className="text-slate-400" />
                  )}
                </button>
              </div>
            )}
          </div>
          
          {/* Content */}
          {message.isLoading ? (
            <div className="flex items-center gap-2 text-slate-500 text-sm mt-2">
              <Loader2 size={14} className="animate-spin" />
              <span>Reasoning through first principles...</span>
            </div>
          ) : (
            <div className="mt-2 text-sm">
              <MarkdownRenderer content={displayContent} copyable={false} />
            </div>
          )}
          
          {/* Chain of Thought Flowchart */}
          {!isUser && !message.isLoading && showCoT && message.reasoning && (
            <div className="mt-4 pt-4 border-t border-slate-200">
              <ReasoningFlowChart
                reasoning={message.reasoning}
                title="Reasoning Process"
              />
            </div>
          )}
          
          {/* Metadata */}
          {!isUser && !message.isLoading && message.model && (
            <div className="mt-3 flex items-center gap-3 text-xs text-slate-400">
              {message.model && (
                <span className="flex items-center gap-1">
                  <Zap size={10} />
                  {message.model}
                </span>
              )}
              {message.latency && (
                <span>{Math.round(message.latency)}ms</span>
              )}
              {message.tokens && (
                <span>{message.tokens} tokens</span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Main RightDrawer component
 */
export default function RightDrawer({ onClose, onMaximize, isMaximized }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showAllCoT, setShowAllCoT] = useState(false);
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
    const query = input.trim();
    setInput('');
    setIsLoading(true);

    setMessages(prev => [...prev, { role: 'assistant', isLoading: true }]);

    try {
      const apiBase = API_BASE;
      
      const response = await fetch(`${apiBase}/api/v1/agents/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: query,
          include_reasoning: true,
          first_principles: true
        }),
      });

      if (!response.ok) throw new Error('API error');

      const data = await response.json();
      
      // Extract content robustly
      const extractContent = (obj) => {
        if (typeof obj === 'string') return obj;
        if (!obj || typeof obj !== 'object') return String(obj || '');
        if (typeof obj.content === 'string') return obj.content;
        if (typeof obj.result === 'string') return obj.result;
        if (typeof obj.message === 'string') return obj.message;
        if (obj.content && typeof obj.content === 'object') {
          if (typeof obj.content.content === 'string') return obj.content.content;
        }
        return JSON.stringify(obj, null, 2);
      };

      let content = "I've processed your request.";
      if (typeof data.message === 'string') {
        content = data.message;
      } else if (data.response) {
        content = extractContent(data.response);
      }
      
      // Extract reasoning chain if available
      let reasoning = null;
      if (data.reasoning) {
        reasoning = data.reasoning;
      } else if (data.chain_of_thought) {
        reasoning = data.chain_of_thought;
      } else if (data.response?.reasoning) {
        reasoning = data.response.reasoning;
      } else if (data.derivation_plan) {
        // Convert derivation plan to reasoning steps
        reasoning = data.derivation_plan.map((step, i) => ({
          type: i === 0 ? 'understanding' : i === data.derivation_plan.length - 1 ? 'conclusion' : 'derivation',
          title: step.step || `Step ${i + 1}`,
          content: step.explanation || step.content || step,
          plainLanguage: step.plain_language,
        }));
      }
      
      // Extract quality gate data
      const qualityData = data.quality || data.response?.quality || null;
      
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: content,
          reasoning: reasoning,
          quality: qualityData,
          model: data.model || data.response?.model,
          latency: data.latency_ms || data.response?.latency_ms,
          tokens: data.tokens || data.response?.usage?.total_tokens,
        }
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [
        ...prev.slice(0, -1),
        {
          role: 'assistant',
          content: `**Connection Error**\n\nUnable to reach the Beyond Frontier backend.\n\n**Troubleshooting:**\n1. Ensure the server is running on port 5002\n2. Check network connectivity\n3. Verify API endpoint configuration\n\n*Error: ${error.message}*`,
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
    setInput(prev => action + prev);
    inputRef.current?.focus();
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="h-full flex flex-col bg-white border-l border-slate-200">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 bg-gradient-to-r from-slate-50 to-white">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center shadow-sm">
            <span className="text-white font-bold text-sm">W</span>
          </div>
          <div>
            <span className="font-semibold text-sm text-slate-800">Beyond Frontier</span>
            <p className="text-xs text-slate-500">First Principles Reasoning</p>
          </div>
        </div>
        
        <div className="flex items-center gap-1">
          {messages.some(m => m.reasoning) && (
            <button
              onClick={() => setShowAllCoT(!showAllCoT)}
              className={clsx(
                'px-2 py-1 text-xs rounded flex items-center gap-1 transition-colors',
                showAllCoT 
                  ? 'bg-purple-100 text-purple-700' 
                  : 'text-slate-500 hover:bg-slate-100'
              )}
              title="Toggle all Chain of Thought"
            >
              <GitBranch size={12} />
              CoT
            </button>
          )}
          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="p-1.5 hover:bg-slate-100 rounded transition-colors"
              title="Clear chat"
            >
              <Trash2 size={14} className="text-slate-400" />
            </button>
          )}
          <button
            onClick={onMaximize}
            className="p-1.5 hover:bg-slate-100 rounded transition-colors"
            title={isMaximized ? 'Minimize' : 'Maximize'}
          >
            {isMaximized ? (
              <Minimize2 size={14} className="text-slate-400" />
            ) : (
              <Maximize2 size={14} className="text-slate-400" />
            )}
          </button>
          <button
            onClick={onClose}
            className="p-1.5 hover:bg-slate-100 rounded transition-colors"
            title="Close"
          >
            <X size={14} className="text-slate-400" />
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="p-6 text-center">
            <div className="w-12 h-12 mx-auto rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center mb-4 shadow-lg">
              <Sparkles size={24} className="text-white" />
            </div>
            <h3 className="font-semibold text-slate-800 mb-2">Beyond Frontier Assistant</h3>
            <p className="text-sm text-slate-500 mb-6">
              Ask questions and see the reasoning process with first principles explanations
            </p>
            
            {/* Quick Actions */}
            <div className="space-y-2">
              <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">Quick Actions</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {quickActions.map((action, i) => (
                  <button
                    key={i}
                    onClick={() => handleQuickAction(action.action)}
                    className="flex items-center gap-1.5 px-3 py-2 bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-lg text-xs text-slate-600 transition-colors"
                  >
                    <action.icon size={12} />
                    {action.label}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Features hint */}
            <div className="mt-6 pt-6 border-t border-slate-100">
              <p className="text-xs text-slate-400 mb-3">Features</p>
              <div className="grid grid-cols-2 gap-2 text-xs text-slate-500">
                <div className="flex items-center gap-2">
                  <Brain size={12} className="text-purple-500" />
                  Chain of Thought
                </div>
                <div className="flex items-center gap-2">
                  <FileText size={12} className="text-blue-500" />
                  LaTeX Rendering
                </div>
                <div className="flex items-center gap-2">
                  <GitBranch size={12} className="text-orange-500" />
                  Reasoning Flow
                </div>
                <div className="flex items-center gap-2">
                  <Copy size={12} className="text-green-500" />
                  Copy Support
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            {messages.map((message, i) => (
              <DrawerMessage 
                key={i} 
                message={message} 
                showReasoning={showAllCoT || undefined}
              />
            ))}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <div className="p-3 border-t border-slate-200 bg-gradient-to-t from-slate-50 to-white">
        <div className="relative">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything about physics..."
            rows={1}
            className="w-full px-4 py-3 pr-12 bg-white border border-slate-200 hover:border-slate-300 focus:border-orange-400 rounded-xl text-sm text-slate-800 placeholder-slate-400 resize-none focus:outline-none focus:ring-2 focus:ring-orange-100 transition-all"
            style={{ minHeight: '44px', maxHeight: '120px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className={clsx(
              'absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all',
              input.trim() && !isLoading
                ? 'bg-orange-500 text-white hover:bg-orange-600 shadow-sm'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            )}
          >
            {isLoading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Send size={16} />
            )}
          </button>
        </div>
        <p className="text-xs text-slate-400 mt-2 text-center">
          Press Enter to send • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
