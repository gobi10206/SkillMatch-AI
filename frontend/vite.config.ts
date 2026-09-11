import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

// Low-bandwidth first: PWA caching is enabled from the start rather
// than bolted on later (see Phase 17 in the roadmap).
export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "SkillMatch AI",
        short_name: "SkillMatch",
        theme_color: "#0f172a",
        display: "standalone",
      },
    }),
  ],
  server: {
    port: 5173,
  },
});
