import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#faf7f5",
          100: "#f0e9e3",
          200: "#e0d1c5",
          300: "#ccb3a0",
          400: "#b5907a",
          500: "#a57862",
          600: "#986856",
          700: "#7e5548",
          800: "#67463e",
          900: "#553b35",
        },
      },
    },
  },
  plugins: [],
};

export default config;
