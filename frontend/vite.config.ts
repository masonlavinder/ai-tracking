import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// GitHub Pages serves the site from https://<user>.github.io/ai-tracking/,
// so assets must be prefixed with the repo name.
export default defineConfig({
  base: "/ai-tracking/",
  plugins: [react()],
  resolve: {
    alias: {
      "@components": new URL("./src/components", import.meta.url).pathname,
      "@api": new URL("./src/api", import.meta.url).pathname,
      "@types": new URL("./src/types", import.meta.url).pathname,
      "@pages": new URL("./src/pages", import.meta.url).pathname,
    },
  },
});
