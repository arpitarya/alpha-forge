import { resolve } from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/**
 * Dual-purpose Vite config:
 *   - `pnpm dev`         → serves /playground/index.html for iterating on the orb
 *   - `pnpm build`       → builds /src/index.ts as a library (esm + cjs)
 *   - `pnpm build:demo`  → bundles the playground as a static site
 *
 * The "lib" mode is the default for `vite build` (no --mode flag); the demo
 * build switches off lib mode and packages the playground for hosting.
 */
export default defineConfig(({ mode }) => {
  const isDemo = mode === "demo";

  return {
    plugins: [react()],
    root: isDemo ? "playground" : ".",
    publicDir: false,
    server: {
      port: 5180,
      open: "/playground/",
      strictPort: false,
    },
    build: isDemo
      ? {
          outDir: "../dist-demo",
          emptyOutDir: true,
        }
      : {
          lib: {
            entry: resolve(__dirname, "src/index.ts"),
            name: "SolarOrbBall",
            fileName: "solar-orb-ball",
            formats: ["es", "cjs"],
          },
          cssCodeSplit: false,
          sourcemap: true,
          rollupOptions: {
            external: ["react", "react-dom", "react/jsx-runtime"],
            output: {
              globals: {
                react: "React",
                "react-dom": "ReactDOM",
              },
              assetFileNames: (assetInfo) => {
                if (assetInfo.name?.endsWith(".css")) return "solar-orb-ball.css";
                return assetInfo.name ?? "asset";
              },
            },
          },
        },
  };
});
