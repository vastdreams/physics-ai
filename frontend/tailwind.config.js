/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          primary: '#6366f1',
          secondary: '#8b5cf6',
          blue: '#3b82f6',
          purple: '#7c3aed',
          pink: '#ec4899',
          cyan: '#06b6d4',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Menlo', 'monospace'],
        math: ['STIX Two Math', 'Cambria Math', 'serif'],
      },
      boxShadow: {
        'glow-sm': '0 2px 10px rgba(99, 102, 241, 0.15)',
        'glow': '0 4px 20px rgba(99, 102, 241, 0.2)',
        'glow-lg': '0 8px 40px rgba(99, 102, 241, 0.3)',
        'glow-purple': '0 4px 20px rgba(139, 92, 246, 0.2)',
        'glow-cyan': '0 4px 20px rgba(6, 182, 212, 0.2)',
        'soft': '0 2px 15px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02)',
        'soft-lg': '0 8px 30px rgba(0, 0, 0, 0.06), 0 2px 8px rgba(0, 0, 0, 0.03)',
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateX(-10px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
    },
  },
  plugins: [],
}
