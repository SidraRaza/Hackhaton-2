/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class', // Enable dark mode with class strategy
  theme: {
    extend: {
      colors: {
        // Simplified SaaS-style color palette with neutral background and single primary brand color
        primary: {
          50: '#eff6ff',  // Lightest primary
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6', // Main primary brand color
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a', // Darkest primary
        },
        // Neutral background colors
        background: {
          DEFAULT: '#f8fafc', // Light gray background
          light: '#f1f5f9',   // Lighter background
          dark: '#e2e8f0',    // Darker background
        },
        // Neutral text colors
        text: {
          primary: '#1e293b',  // Dark text
          secondary: '#64748b', // Medium text
          muted: '#94a3b8',    // Light text
        },
        // Simplified border colors
        border: {
          DEFAULT: '#e2e8f0',  // Light border
          light: '#cbd5e1',    // Lighter border
          dark: '#94a3b8',     // Darker border
        }
      },
      boxShadow: {
        // Reduced shadow usage for cleaner look
        'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)', // Very subtle shadow
        'card': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)', // Minimal card shadow
        'none': 'none', // Option for no shadow
      },
      borderRadius: {
        'sm': '0.125rem',
        'DEFAULT': '0.25rem',
        'md': '0.375rem',
        'lg': '0.5rem', // More conservative rounded corners
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'Noto Sans', 'sans-serif'],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  plugins: [],
};