/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        navy: {
          950: '#070a12',
          900: '#0b0f19',
          850: '#0f172a',
          800: '#151e33',
          700: '#1e293b',
          600: '#334155',
        },
        cyan: {
          DEFAULT: '#06b6d4',
          glow: '#22d3ee',
        },
        teal: {
          DEFAULT: '#14b8a6',
          glow: '#2dd4bf',
        },
        violet: {
          DEFAULT: '#8b5cf6',
          glow: '#a855f7',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glow-cyan': '0 0 20px -3px rgba(6, 182, 212, 0.35)',
        'glow-teal': '0 0 20px -3px rgba(20, 184, 166, 0.35)',
        'glow-violet': '0 0 20px -3px rgba(139, 92, 246, 0.35)',
      }
    },
  },
  plugins: [],
}
