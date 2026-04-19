import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves the site from https://<user>.github.io/ai-tracking/,
// so assets must be prefixed with the repo name.
export default defineConfig({
  base: "/ai-tracking/",
  plugins: [react()],
});
