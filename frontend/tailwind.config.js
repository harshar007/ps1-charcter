/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ps1: {
          dark: '#0c0d12',
          card: '#161922',
          border: '#2a2f3f',
          accent: '#00e5ff',
          neon: '#ff0077',
          gray: '#9ba3b4',
          highlight: '#2c3347'
        }
      },
      fontFamily: {
        mono: ['"Courier New"', 'Courier', 'monospace'],
        display: ['system-ui', '-apple-system', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
