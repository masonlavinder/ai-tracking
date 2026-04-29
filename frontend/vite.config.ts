import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Served from the custom domain watchthediff.knurled.studio at the root,
// so no path prefix is needed.
export default defineConfig({
  base: "/",
  plugins: [react()],
  resolve: {
    alias: {
      "@components": new URL("./src/components", import.meta.url).pathname,
      "@api": new URL("./src/api", import.meta.url).pathname,
      "@types": new URL("./src/types", import.meta.url).pathname,
      "@pages": new URL("./src/pages", import.meta.url).pathname,
      "@data": new URL("./src/data", import.meta.url).pathname,
    },
  },
});
