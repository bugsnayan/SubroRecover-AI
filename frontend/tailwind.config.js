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
          950: '#070C13',
          900: '#0D1520', // dark base
          800: '#142030',
          700: '#1D2D42',
          600: '#2A3F5B',
        },
        paper: {
          50: '#FAF9F6',
          100: '#F6F4EF', // light base
          200: '#EDE9E0',
          300: '#E2DCD0',
          400: '#D5CDBF',
        },
        brass: {
          400: '#DFC285',
          500: '#CFA968', // primary accent
          600: '#B88F4E',
          700: '#946E33',
        },
        teal: {
          400: '#40A9A3',
          500: '#2F8F89', // recovered / positive
          600: '#24716D',
          700: '#1A5451',
        },
        rust: {
          400: '#E07757',
          500: '#D1603D', // risk / urgent
          600: '#B64A29',
          700: '#8E361B',
        },
        slate: {
          300: '#B5C2D0',
          400: '#8FA0B3', // muted text
          500: '#6C7E92',
          600: '#4F5F71',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'glow-brass': '0 0 16px -2px rgba(207, 169, 104, 0.25)',
        'glow-teal': '0 0 16px -2px rgba(47, 143, 137, 0.25)',
        'glow-rust': '0 0 16px -2px rgba(209, 96, 61, 0.25)',
      },
    },
  },
  plugins: [],
}
