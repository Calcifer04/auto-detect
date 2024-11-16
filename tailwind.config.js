/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",  // This tells Tailwind where to look for class names
    "./public/index.html",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

