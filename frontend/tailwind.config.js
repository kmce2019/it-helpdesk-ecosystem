/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a56db',
        secondary: '#7e8ba3',
        success: '#05b981',
        danger: '#f02316',
        warning: '#f59e0b',
        info: '#0891b2',
      },
    },
  },
  plugins: [],
}
