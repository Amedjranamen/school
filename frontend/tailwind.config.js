/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{js,jsx}',
    './components/**/*.{js,jsx}',
    './app/**/*.{js,jsx}',
    './src/**/*.{js,jsx}',
  ],
  prefix: "",
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        // Palette bibliothèque moderne
        library: {
          'navy': '#1E40AF',      // header, sidebar
          'blue': '#60A5FA',      // boutons et hover
          'gray-light': '#F1F5F9', // fond général
          'gray-dark': '#334155',  // textes secondaires
          'success': '#16A34A',    // succès/validation
          'danger': '#DC2626',     // alertes
        },
        // Shadcn UI colors (conservés pour compatibilité)
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "#1E40AF", // bleu nuit
          foreground: "#ffffff",
        },
        secondary: {
          DEFAULT: "#60A5FA", // bleu clair
          foreground: "#ffffff",
        },
        destructive: {
          DEFAULT: "#DC2626", // rouge alertes
          foreground: "#ffffff",
        },
        muted: {
          DEFAULT: "#F1F5F9", // gris clair
          foreground: "#334155", // gris foncé
        },
        accent: {
          DEFAULT: "#16A34A", // vert succès
          foreground: "#ffffff",
        },
        popover: {
          DEFAULT: "#ffffff",
          foreground: "#334155",
        },
        card: {
          DEFAULT: "#ffffff",
          foreground: "#334155",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}