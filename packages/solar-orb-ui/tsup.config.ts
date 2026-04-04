import { defineConfig } from "tsup";

export default defineConfig([
  {
    entry: ["src/index.ts"],
    format: ["esm", "cjs"],
    dts: true,
    sourcemap: true,
    clean: true,
    external: ["react", "react-dom"],
    treeshake: true,
    splitting: false,
    minify: false,
    async onSuccess() {
      const fs = await import("node:fs/promises");
      for (const file of ["dist/index.js", "dist/index.cjs"]) {
        const content = await fs.readFile(file, "utf-8");
        if (!content.startsWith('"use client"')) {
          await fs.writeFile(file, `"use client";\n${content}`);
        }
      }
    },
  },
  {
    entry: ["src/tokens/index.ts"],
    format: ["esm", "cjs"],
    dts: true,
    sourcemap: true,
    external: ["react", "react-dom"],
    treeshake: true,
    splitting: false,
    minify: false,
  },
]);
