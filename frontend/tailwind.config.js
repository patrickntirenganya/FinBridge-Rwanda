// Palette mirrors ui/theme.py: tea = formal finance, sorghum = informal, soil = the gap.
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.ts"],
  theme: {
    extend: {
      colors: {
        ink: "#1C2B24", slate: "#56665E", mist: "#EEF2EC", line: "#C9D3CC",
        tea: { DEFAULT: "#2F6B4F", dark: "#1F4D38", deep: "#173A2B", soft: "#8FB5A0" },
        sorghum: "#C2922A", soil: "#8E3B2E",
      },
      fontFamily: { sans: ["Atkinson Hyperlegible", "Segoe UI", "system-ui", "sans-serif"] },
      keyframes: {
        rise: { from: { opacity: "0", transform: "translateY(18px)" }, to: { opacity: "1", transform: "none" } },
        floaty: { "0%,100%": { transform: "translateY(0)" }, "50%": { transform: "translateY(-8px)" } },
      },
      animation: { rise: "rise .8s ease both", floaty: "floaty 6s ease-in-out infinite" },
    },
  },
};
