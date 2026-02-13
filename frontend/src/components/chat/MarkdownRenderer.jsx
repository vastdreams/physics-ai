/**
 * PATH: frontend/src/components/chat/MarkdownRenderer.jsx
 * PURPOSE: Unified markdown renderer with LaTeX math support via KaTeX
 * 
 * FEATURES:
 * - Markdown parsing with react-markdown
 * - LaTeX math rendering with KaTeX (inline $ and display $$)
 * - GitHub Flavored Markdown (tables, strikethrough, task lists)
 * - Custom code block rendering with syntax highlighting
 * - Auto-detection of LaTeX delimiters (converts various formats)
 * - Copy-to-clipboard with proper formatting
 * - Responsive typography
 */

import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import remarkGfm from 'remark-gfm';
import { useState, useMemo } from 'react';
import { Copy, Check, Play, ExternalLink } from 'lucide-react';
import { clsx } from 'clsx';
import 'katex/dist/katex.min.css';

/**
 * Known LaTeX math commands that indicate math mode.
 * Used by bare-LaTeX detection to avoid wrapping non-math backslash uses.
 */
const MATH_COMMANDS = new Set([
  // Greek letters
  'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'varepsilon', 'zeta', 'eta',
  'theta', 'vartheta', 'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'pi',
  'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi',
  'varphi', 'chi', 'psi', 'omega',
  'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon',
  'Phi', 'Psi', 'Omega',
  // Fractions, roots, accents
  'frac', 'dfrac', 'tfrac', 'sqrt', 'vec', 'hat', 'bar', 'dot', 'ddot',
  'tilde', 'widetilde', 'widehat', 'overline', 'underline',
  // Big operators
  'sum', 'prod', 'int', 'iint', 'iiint', 'oint', 'bigcup', 'bigcap',
  // Calculus / analysis
  'partial', 'nabla', 'infty', 'lim', 'limsup', 'liminf',
  // Binary operators
  'cdot', 'times', 'pm', 'mp', 'div', 'cap', 'cup', 'wedge', 'vee',
  'oplus', 'otimes', 'circ', 'bullet',
  // Relations
  'leq', 'geq', 'neq', 'approx', 'equiv', 'sim', 'simeq', 'cong',
  'propto', 'll', 'gg', 'prec', 'succ',
  // Set / logic
  'in', 'notin', 'subset', 'supset', 'subseteq', 'supseteq',
  'forall', 'exists', 'nexists', 'emptyset',
  // Misc symbols
  'hbar', 'ell', 'Re', 'Im', 'dagger', 'ddagger', 'star',
  // Delimiters
  'left', 'right', 'langle', 'rangle', 'lceil', 'rceil', 'lfloor', 'rfloor',
  // Formatting
  'mathrm', 'mathbf', 'mathit', 'mathcal', 'mathbb', 'mathfrak',
  'boldsymbol', 'operatorname', 'text',
  // Spacing
  'quad', 'qquad',
  // Arrows
  'to', 'rightarrow', 'leftarrow', 'Rightarrow', 'Leftarrow', 'mapsto',
  'leftrightarrow', 'Leftrightarrow',
  // Functions
  'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'arcsin', 'arccos', 'arctan',
  'sinh', 'cosh', 'tanh', 'exp', 'ln', 'log', 'det', 'max', 'min',
  'sup', 'inf', 'arg', 'deg',
  // Combinatorics / layout
  'binom', 'choose', 'overset', 'underset', 'overbrace', 'underbrace',
  'stackrel',
]);

/**
 * Check if a LaTeX command name is a known math command.
 */
function isMathCommand(cmd) {
  return MATH_COMMANDS.has(cmd);
}

/**
 * Skip a balanced brace group starting at position `pos` (which should be '{').
 * Returns the index just after the closing '}'.
 */
function skipBraceGroup(text, pos) {
  if (pos >= text.length || text[pos] !== '{') return pos;
  let depth = 1;
  let i = pos + 1;
  while (i < text.length && depth > 0) {
    if (text[i] === '{') depth++;
    else if (text[i] === '}') depth--;
    i++;
  }
  return i;
}

/**
 * Preprocess content to normalize LaTeX delimiters for remark-math / rehype-katex.
 *
 * Handles three cases LLMs produce:
 * 1. \( ... \)  →  $ ... $       (standard LaTeX inline delimiters)
 * 2. \[ ... \]  →  $$ ... $$     (standard LaTeX display delimiters)
 * 3. Bare LaTeX in running text  →  wrapped in $ ... $
 *    e.g. "so m \gamma^3 \vec{a} \cdot \vec{v} = m c^2 \frac{d\gamma}{dt}"
 */
function preprocessLatex(content) {
  if (!content || typeof content !== 'string') return content;

  let processed = content;

  // --- Step 1: Convert \( ... \) to $ ... $ ---
  // Non-greedy [\s\S]*? handles multiline and nested parens safely.
  processed = processed.replace(
    /\\\(([\s\S]*?)\\\)/g,
    (_, inner) => `$${inner}$`
  );

  // --- Step 2: Convert \[ ... \] to $$ ... $$ ---
  // Newlines around $$ ensure remark-math parses as display math.
  processed = processed.replace(
    /\\\[([\s\S]*?)\\\]/g,
    (_, inner) => `\n$$\n${inner.trim()}\n$$\n`
  );

  // --- Step 3: Wrap bare LaTeX math expressions ---
  processed = wrapBareLatex(processed);

  return processed;
}

/**
 * Split content into math-delimited and text segments.
 * Only process text segments for bare LaTeX wrapping.
 */
function wrapBareLatex(content) {
  // Parse into segments: 'math' (inside $/$$ delimiters) and 'text' (outside)
  const segments = [];
  let pos = 0;
  const len = content.length;

  while (pos < len) {
    // Check for $$ (display math)
    if (content[pos] === '$' && pos + 1 < len && content[pos + 1] === '$') {
      const closeIdx = content.indexOf('$$', pos + 2);
      if (closeIdx !== -1) {
        segments.push({ type: 'math', value: content.slice(pos, closeIdx + 2) });
        pos = closeIdx + 2;
        continue;
      }
    }

    // Check for $ (inline math) — but not $$
    if (content[pos] === '$' && (pos + 1 >= len || content[pos + 1] !== '$')) {
      let closeIdx = pos + 1;
      while (closeIdx < len) {
        if (content[closeIdx] === '$' && content[closeIdx - 1] !== '\\') break;
        closeIdx++;
      }
      if (closeIdx < len) {
        segments.push({ type: 'math', value: content.slice(pos, closeIdx + 1) });
        pos = closeIdx + 1;
        continue;
      }
    }

    // Regular text character
    const lastSeg = segments[segments.length - 1];
    if (lastSeg && lastSeg.type === 'text') {
      lastSeg.value += content[pos];
    } else {
      segments.push({ type: 'text', value: content[pos] });
    }
    pos++;
  }

  return segments
    .map((seg) => (seg.type === 'math' ? seg.value : wrapBareLatexInText(seg.value)))
    .join('');
}

/**
 * Detect bare LaTeX math expressions in plain text and wrap them in $ ... $.
 *
 * Strategy:
 *  1. Find all positions of \knowncommand in the text.
 *  2. Group nearby commands into contiguous math expressions.
 *  3. Expand each expression to include brace arguments and surrounding math context.
 *  4. Wrap each expression in $ ... $.
 */
function wrapBareLatexInText(text) {
  // --- 1. Find all known LaTeX command positions ---
  const cmdRegex = /\\([a-zA-Z]{2,})/g;
  const cmdPositions = [];
  let m;
  while ((m = cmdRegex.exec(text)) !== null) {
    if (isMathCommand(m[1])) {
      // Expand past any brace arguments right after the command
      let end = cmdRegex.lastIndex;
      while (end < text.length && text[end] === '{') {
        end = skipBraceGroup(text, end);
      }
      cmdPositions.push({ start: m.index, end });
    }
  }

  if (cmdPositions.length === 0) return text;

  // --- 2. Group nearby commands into expressions ---
  const isMathChar = (ch) => /[a-zA-Z0-9 \t=+\-*/^_{}(),.<>|]/.test(ch);

  const expressions = [];
  let current = { start: cmdPositions[0].start, end: cmdPositions[0].end };

  for (let i = 1; i < cmdPositions.length; i++) {
    const gap = text.slice(current.end, cmdPositions[i].start);
    // Merge if the gap is short, contains only math-like chars, and no paragraph breaks
    if (gap.length < 80 && !gap.includes('\n\n') && [...gap].every((ch) => isMathChar(ch) || ch === '\\')) {
      current.end = cmdPositions[i].end;
    } else {
      expressions.push({ ...current });
      current = { start: cmdPositions[i].start, end: cmdPositions[i].end };
    }
  }
  expressions.push({ ...current });

  // --- 3. Expand each expression ---
  for (const expr of expressions) {
    // Expand forward: include trailing math content and any further brace groups / commands
    let end = expr.end;
    while (end < text.length) {
      const ch = text[end];
      if (ch === '{') {
        end = skipBraceGroup(text, end);
      } else if (ch === '\\' && end + 1 < text.length && /[a-zA-Z]/.test(text[end + 1])) {
        // Another \command — include it and its brace args
        end++;
        while (end < text.length && /[a-zA-Z]/.test(text[end])) end++;
        while (end < text.length && text[end] === '{') {
          end = skipBraceGroup(text, end);
        }
      } else if (/[a-zA-Z0-9 \t=+\-*/^_(),.<>]/.test(ch) && ch !== '\n') {
        // Check for sentence boundary: punctuation followed by space
        if (/[.!?;]/.test(ch) && end + 1 < text.length && /[\s\n]/.test(text[end + 1])) {
          break;
        }
        end++;
      } else {
        break;
      }
    }
    // Trim trailing whitespace and sentence-ending punctuation from math expression
    while (end > expr.end && /[\s.!?;,]/.test(text[end - 1])) end--;
    expr.end = end;

    // Expand backward: include leading variable names (single letters, short tokens)
    let start = expr.start;
    // Skip whitespace
    while (start > 0 && text[start - 1] === ' ') start--;
    // Include a leading math token (variable name, number, etc.)
    while (start > 0 && /[a-zA-Z0-9_^=+\-*/]/.test(text[start - 1])) {
      start--;
      // Stop at sentence boundaries
      if (start > 0 && /[.!?;:]/.test(text[start]) && /\s/.test(text[start - 1] || '')) {
        start++;
        break;
      }
    }
    // If we captured a long word (> 3 chars with no math operators), it's probably
    // a regular English word, not a math variable — don't include it
    const leadCapture = text.slice(start, expr.start).trim();
    if (leadCapture.length > 3 && /^[a-zA-Z]+$/.test(leadCapture)) {
      start = expr.start;
    }
    expr.start = start;
  }

  // --- 4. Build result, wrapping expressions in $ ... $ ---
  // Process from end to start so indices stay valid
  let result = text;
  for (let i = expressions.length - 1; i >= 0; i--) {
    const { start, end } = expressions[i];
    const mathContent = result.slice(start, end).trim();
    if (mathContent) {
      const before = result.slice(0, start);
      const after = result.slice(end);
      // Add space padding so remark-math reliably detects delimiters
      const needSpaceBefore = before.length > 0 && !/\s$/.test(before);
      const needSpaceAfter = after.length > 0 && !/^\s/.test(after);
      result =
        before +
        (needSpaceBefore ? ' ' : '') +
        `$${mathContent}$` +
        (needSpaceAfter ? ' ' : '') +
        after;
    }
  }

  return result;
}

// Custom code block component with copy and execute buttons
function CodeBlock({ node, inline, className, children, ...props }) {
  const [copied, setCopied] = useState(false);
  const match = /language-(\w+)/.exec(className || '');
  const language = match ? match[1] : 'text';
  const code = String(children).replace(/\n$/, '');

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Inline code
  if (inline) {
    return (
      <code 
        className="px-1.5 py-0.5 bg-slate-100 text-pink-600 rounded text-sm font-mono"
        {...props}
      >
        {children}
      </code>
    );
  }

  // Block code
  return (
    <div className="relative group my-4 rounded-xl overflow-hidden border border-slate-200 shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-slate-50 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
            {language}
          </span>
        </div>
        <div className="flex items-center gap-1">
          <button
            onClick={handleCopy}
            className="p-1.5 hover:bg-slate-200 rounded transition-colors"
            title="Copy code"
          >
            {copied ? (
              <Check size={14} className="text-green-500" />
            ) : (
              <Copy size={14} className="text-slate-400" />
            )}
          </button>
        </div>
      </div>
      
      {/* Code content */}
      <pre className="p-4 bg-slate-900 overflow-x-auto">
        <code className={`text-sm font-mono text-slate-100 ${className || ''}`} {...props}>
          {children}
        </code>
      </pre>
    </div>
  );
}

// Custom link component
function CustomLink({ href, children, ...props }) {
  const isExternal = href?.startsWith('http');
  
  return (
    <a
      href={href}
      target={isExternal ? '_blank' : undefined}
      rel={isExternal ? 'noopener noreferrer' : undefined}
      className="text-orange-600 hover:text-orange-700 underline underline-offset-2 inline-flex items-center gap-1"
      {...props}
    >
      {children}
      {isExternal && <ExternalLink size={12} />}
    </a>
  );
}

// Custom heading components with anchors
function Heading({ level, children, ...props }) {
  const Tag = `h${level}`;
  const sizes = {
    1: 'text-3xl font-bold mt-8 mb-4',
    2: 'text-2xl font-bold mt-6 mb-3',
    3: 'text-xl font-semibold mt-5 mb-2',
    4: 'text-lg font-semibold mt-4 mb-2',
    5: 'text-base font-semibold mt-3 mb-1',
    6: 'text-sm font-semibold mt-2 mb-1',
  };

  return (
    <Tag className={clsx(sizes[level], 'text-slate-900')} {...props}>
      {children}
    </Tag>
  );
}

// Custom table components
function Table({ children }) {
  return (
    <div className="my-4 overflow-x-auto rounded-lg border border-slate-200">
      <table className="min-w-full divide-y divide-slate-200">
        {children}
      </table>
    </div>
  );
}

function TableHead({ children }) {
  return <thead className="bg-slate-50">{children}</thead>;
}

function TableRow({ children, isHeader }) {
  return (
    <tr className={clsx(!isHeader && 'hover:bg-slate-50 transition-colors')}>
      {children}
    </tr>
  );
}

function TableCell({ children, isHeader }) {
  const Component = isHeader ? 'th' : 'td';
  return (
    <Component
      className={clsx(
        'px-4 py-3 text-sm',
        isHeader 
          ? 'font-semibold text-slate-700 text-left' 
          : 'text-slate-600 border-t border-slate-200'
      )}
    >
      {children}
    </Component>
  );
}

// Custom blockquote
function Blockquote({ children }) {
  return (
    <blockquote className="my-4 pl-4 border-l-4 border-orange-400 bg-orange-50 py-3 pr-4 rounded-r-lg text-slate-700 italic">
      {children}
    </blockquote>
  );
}

// Custom list components
function UnorderedList({ children }) {
  return (
    <ul className="my-3 ml-6 space-y-1 list-disc marker:text-slate-400">
      {children}
    </ul>
  );
}

function OrderedList({ children }) {
  return (
    <ol className="my-3 ml-6 space-y-1 list-decimal marker:text-slate-500 marker:font-semibold">
      {children}
    </ol>
  );
}

function ListItem({ children }) {
  return <li className="text-slate-700 leading-relaxed">{children}</li>;
}

// Horizontal rule
function HorizontalRule() {
  return <hr className="my-8 border-t-2 border-slate-200" />;
}

// Paragraph
function Paragraph({ children }) {
  return <p className="my-3 text-slate-700 leading-relaxed">{children}</p>;
}

// Strong/Bold
function Strong({ children }) {
  return <strong className="font-semibold text-slate-900">{children}</strong>;
}

// Emphasis/Italic
function Emphasis({ children }) {
  return <em className="italic text-slate-700">{children}</em>;
}

// Main MarkdownRenderer component
export default function MarkdownRenderer({ content, className, copyable = true }) {
  const [copied, setCopied] = useState(false);
  
  // Preprocess LaTeX delimiters for proper rendering
  const processedContent = useMemo(() => {
    return preprocessLatex(content);
  }, [content]);
  
  if (!content) return null;
  
  const handleCopyAll = () => {
    // Copy the raw content (not processed) for better usability
    navigator.clipboard.writeText(content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={clsx('markdown-content relative group', className)}>
      {/* Copy all button - appears on hover */}
      {copyable && (
        <button
          onClick={handleCopyAll}
          className="absolute top-0 right-0 opacity-0 group-hover:opacity-100 p-2 bg-white/90 hover:bg-slate-100 rounded-lg shadow-sm border border-slate-200 transition-all z-10"
          title="Copy all content"
        >
          {copied ? (
            <Check size={14} className="text-green-500" />
          ) : (
            <Copy size={14} className="text-slate-500" />
          )}
        </button>
      )}
      
      <ReactMarkdown
        remarkPlugins={[remarkMath, remarkGfm]}
        rehypePlugins={[rehypeKatex]}
        components={{
          code: CodeBlock,
          a: CustomLink,
          h1: (props) => <Heading level={1} {...props} />,
          h2: (props) => <Heading level={2} {...props} />,
          h3: (props) => <Heading level={3} {...props} />,
          h4: (props) => <Heading level={4} {...props} />,
          h5: (props) => <Heading level={5} {...props} />,
          h6: (props) => <Heading level={6} {...props} />,
          table: Table,
          thead: TableHead,
          tr: TableRow,
          th: (props) => <TableCell isHeader {...props} />,
          td: TableCell,
          blockquote: Blockquote,
          ul: UnorderedList,
          ol: OrderedList,
          li: ListItem,
          hr: HorizontalRule,
          p: Paragraph,
          strong: Strong,
          em: Emphasis,
        }}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
}

// Export the preprocessing function for use in other components
export { preprocessLatex };
