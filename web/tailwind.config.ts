import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pink: {
          DEFAULT: "#FF4D8A",
          soft: "#FFE0EC",
          deep: "#C73670",
        },
        ink: {
          DEFAULT: "#2D1B4E",
          soft: "#6B5B8B",
        },
        cream: "#FFFCF7",
      },
      fontFamily: {
        display: ["Fredoka", "system-ui", "sans-serif"],
        sans: ["Quicksand", "system-ui", "sans-serif"],
      },
      keyframes: {
        bobble: {
          "0%, 100%": { transform: "translateY(0) rotate(-3deg)" },
          "50%":      { transform: "translateY(-12px) rotate(3deg)" },
        },
        drift: {
          "0%":   { transform: "translate(0, 0) rotate(0deg)" },
          "25%":  { transform: "translate(30px, -20px) rotate(15deg)" },
          "50%":  { transform: "translate(-20px, 30px) rotate(-10deg)" },
          "75%":  { transform: "translate(20px, 20px) rotate(8deg)" },
          "100%": { transform: "translate(0, 0) rotate(0deg)" },
        },
        dropIn: {
          "0%":   { opacity: "0", transform: "rotate(-15deg) translateY(-100px)" },
          "100%": { opacity: "1", transform: "rotate(-2deg) translateY(0)" },
        },
        wiggle: {
          "0%, 100%": { transform: "rotate(-2deg)" },
          "50%":      { transform: "rotate(2deg)" },
        },
      },
      animation: {
        bobble: "bobble 3s ease-in-out infinite",
        drift: "drift 22s linear infinite",
        dropIn: "dropIn 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
        wiggle: "wiggle 3s ease-in-out infinite",
      },
      boxShadow: {
        soft: "0 8px 24px rgba(45, 27, 78, 0.12)",
        lg2: "0 16px 48px rgba(45, 27, 78, 0.18)",
        pink: "0 12px 32px rgba(255, 77, 138, 0.35)",
      },
    },
  },
  plugins: [],
} satisfies Config;
