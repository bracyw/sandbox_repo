/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./projects/ui/src/**/*.{html,ts}'],
  theme: {
    extend: {
      colors: {
        border: '#e2e8f0',
        input: '#e2e8f0',
        ring: '#0f172a',
        background: '#ffffff',
        foreground: '#0f172a',
        primary: {
          DEFAULT: '#0f172a',
          foreground: '#f8fafc'
        },
        secondary: {
          DEFAULT: '#f1f5f9',
          foreground: '#0f172a'
        },
        muted: {
          DEFAULT: '#f8fafc',
          foreground: '#64748b'
        },
        destructive: {
          DEFAULT: '#dc2626',
          foreground: '#fef2f2'
        }
      },
      borderRadius: {
        lg: '0.75rem',
        md: '0.5rem',
        sm: '0.375rem'
      }
    }
  },
  plugins: []
};
