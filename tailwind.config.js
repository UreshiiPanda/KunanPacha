/** @type {import('tailwindcss').Config} */

module.exports = {
  content: [
    "./**/templates/*.html",
  ],
  theme: {
    extend: {
      fontFamily: {
        'barlow': ['Barlow Condensed', 'barlow'],
        'baskervville': ['Baskervville SC', 'serif'],
        'playfair': ['Playfair Display', 'serif'],
      },
    },    screens: {
      'sm': '480px',   // Small screens, mobile phones
      'md': '768px',   // Medium screens, tablets
      'lg': '1024px',  // Large screens, laptops/desktops
      'xl': '1280px',  // Extra large screens, larger desktops
      '2xl': '1536px', // Extra large screens, 2x larger desktops
    }
  },
  plugins: [],
}

