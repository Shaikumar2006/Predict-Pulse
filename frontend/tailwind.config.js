/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "#080D14",
        panel: "#0D141D",
        card: "#111A24",
        border: "#22303D",
        primary: "#F1F5F9",
        secondary: "#94A3B8",
        healthy: "#22C55E",
        warning: "#F59E0B",
        critical: "#EF4444",
        info: "#38BDF8",
        ai: "#8B5CF6",
      },
    },
  },
}