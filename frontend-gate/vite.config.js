import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { fileURLToPath } from "url"
import flexGapFallback from "../frontend/compat/postcss-flex-gap.js"
import classicFallback from "../frontend/compat/classic-fallback.js"

const here = (path) => fileURLToPath(new URL(path, import.meta.url))

export default defineConfig({
	plugins: [vue({ template: { transformAssetUrls: { includeAbsolute: false } } }), classicFallback()],
	css: { postcss: { plugins: [flexGapFallback()] } },
	build: {
		target: "chrome55",
		cssTarget: "chrome55",
		modulePreload: false,
		outDir: here("../fleetix/public/gate"),
		emptyOutDir: true,
		rollupOptions: { output: { inlineDynamicImports: true } },
	},
})
