/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './cn/**/*.html',
    './en/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        headline: ['HarmonyOS Sans SC', 'Roboto', 'sans-serif'],
        body: ['HarmonyOS Sans SC', 'Roboto', 'sans-serif'],
        label: ['HarmonyOS Sans SC', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.25rem',
        xl: '0.25rem',
        full: '9999px',
      },
    },
  },
  corePlugins: {
    preflight: false,
  },
};
