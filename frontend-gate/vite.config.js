import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { fileURLToPath } from "url"

const here = (path) => fileURLToPath(new URL(path, import.meta.url))

export default defineConfig({
	plugins: [vue({ template: { transformAssetUrls: { includeAbsolute: false } } })],
	build: {
		target: "chrome61",
		cssTarget: "chrome61",
		modulePreload: false,
		outDir: here("../fleetix/public/gate"),
		emptyOutDir: true,
	},
})
