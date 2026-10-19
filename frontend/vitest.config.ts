import { fileURLToPath } from "node:url";

import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  test: {
    // These tests cover plain logic (no components), so no browser
    // environment is needed.
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
