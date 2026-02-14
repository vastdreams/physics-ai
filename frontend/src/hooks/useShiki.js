/**
 * PATH: frontend/src/hooks/useShiki.js
 * PURPOSE: React hook for Shiki syntax highlighter
 * 
 * FEATURES:
 * - Async loading of Shiki highlighter
 * - Caching for performance
 * - Light/dark theme support
 * - Multiple language support
 */

import { useState, useEffect, useCallback, useRef } from 'react';

import { createHighlighter } from 'shiki';

// Singleton highlighter instance
let highlighterPromise = null;
let cachedHighlighter = null;

// Languages to preload
const PRELOADED_LANGUAGES = [
  'python',
  'javascript',
  'typescript',
  'json',
  'bash',
  'shell',
  'latex',
  'markdown',
  'html',
  'css',
  'sql',
  'yaml',
  'rust',
  'go',
  'cpp',
  'c',
  'java'
];

// Themes
const THEMES = {
  light: 'github-light',
  dark: 'github-dark'
};

/**
 * Initialize and get Shiki highlighter (singleton)
 */
async function getShikiHighlighter() {
  if (cachedHighlighter) {
    return cachedHighlighter;
  }

  if (!highlighterPromise) {
    highlighterPromise = createHighlighter({
      themes: [THEMES.light, THEMES.dark],
      langs: PRELOADED_LANGUAGES,
    });
  }

  cachedHighlighter = await highlighterPromise;
  return cachedHighlighter;
}

/**
 * React hook for using Shiki highlighter
 * 
 * @returns {Object} - { highlight, isReady, error }
 */
export function useShiki() {
  const [isReady, setIsReady] = useState(!!cachedHighlighter);
  const [error, setError] = useState(null);
  const highlighterRef = useRef(cachedHighlighter);

  useEffect(() => {
    if (cachedHighlighter) {
      highlighterRef.current = cachedHighlighter;
      setIsReady(true);
      return;
    }

    let mounted = true;

    getShikiHighlighter()
      .then((highlighter) => {
        if (mounted) {
          highlighterRef.current = highlighter;
          setIsReady(true);
        }
      })
      .catch((err) => {
        if (mounted) {
          console.error('Failed to load Shiki:', err);
          setError(err);
        }
      });

    return () => {
      mounted = false;
    };
  }, []);

  /**
   * Highlight code with Shiki
   * 
   * @param {string} code - Code to highlight
   * @param {string} language - Language identifier
   * @param {string} theme - 'light' or 'dark'
   * @returns {string} - HTML string with highlighted code
   */
  const highlight = useCallback((code, language = 'text', theme = 'dark') => {
    if (!highlighterRef.current) {
      // Return escaped HTML if highlighter not ready
      return escapeHtml(code);
    }

    try {
      // Normalize language name
      const lang = normalizeLanguage(language);
      const themeName = THEMES[theme] || THEMES.dark;

      const html = highlighterRef.current.codeToHtml(code, {
        lang,
        theme: themeName,
      });

      return html;
    } catch (err) {
      console.warn(`Shiki highlight error for language "${language}":`, err);
      return escapeHtml(code);
    }
  }, []);

  /**
   * Get tokens for more granular control
   */
  const getTokens = useCallback((code, language = 'text') => {
    if (!highlighterRef.current) {
      return null;
    }

    try {
      const lang = normalizeLanguage(language);
      return highlighterRef.current.codeToTokens(code, { lang });
    } catch (err) {
      console.warn(`Shiki tokenize error:`, err);
      return null;
    }
  }, []);

  return {
    highlight,
    getTokens,
    isReady,
    error,
    supportedLanguages: PRELOADED_LANGUAGES,
  };
}

/**
 * Normalize language name to Shiki-supported format
 */
function normalizeLanguage(lang) {
  const normalized = lang?.toLowerCase() || 'text';
  
  const aliases = {
    'py': 'python',
    'js': 'javascript',
    'ts': 'typescript',
    'sh': 'bash',
    'zsh': 'bash',
    'yml': 'yaml',
    'tex': 'latex',
    'md': 'markdown',
    'plaintext': 'text',
    'plain': 'text',
    'txt': 'text',
    'c++': 'cpp',
    'objective-c': 'objc',
    'sympy': 'python',
  };

  return aliases[normalized] || normalized;
}

/**
 * Escape HTML for fallback rendering
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return `<pre><code>${div.innerHTML}</code></pre>`;
}

export default useShiki;
