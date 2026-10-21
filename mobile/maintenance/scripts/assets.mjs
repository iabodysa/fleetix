import { mkdirSync, readFileSync, writeFileSync, copyFileSync, existsSync } from "fs"
import { fileURLToPath } from "url"
import sharp from "sharp"

const here = (path) => fileURLToPath(new URL(path, import.meta.url))
const logo = here("../../../fleetix/public/images/fleetix-logo.svg")
const csv = readFileSync(here("../../../fleetix/translations/ar.csv"), "utf8")
const KEYS = ["Fleetix Maintenance", "Server address", "Save"]
const BG = "#ffffff"

function translations() {
	const rows = {}
	csv.split(/\r?\n/).forEach((line) => {
		const match = line.match(/^"?((?:[^"]|"")*?)"?,"?((?:[^"]|"")*?)"?(,.*)?$/)
		if (match && KEYS.indexOf(match[1]) !== -1) rows[match[1]] = match[2]
	})
	return rows
}

async function icon(size, pad, out) {
	const inner = Math.round(size * (1 - pad * 2))
	const art = await sharp(logo, { density: 600 }).resize(inner, inner, { fit: "contain", background: BG }).png().toBuffer()
	await sharp({ create: { width: size, height: size, channels: 4, background: BG } })
		.composite([{ input: art, gravity: "center" }])
		.png()
		.toFile(out)
}

const tr = translations()
writeFileSync(here("../www/translations.js"), "window.TRANSLATIONS = " + JSON.stringify(tr) + "\n")
copyFileSync(logo, here("../www/logo.svg"))

const res = here("../android/app/src/main/res/")
if (existsSync(res)) {
	const densities = { mdpi: 1, hdpi: 1.5, xhdpi: 2, xxhdpi: 3, xxxhdpi: 4 }
	for (const [name, scale] of Object.entries(densities)) {
		const dir = res + "mipmap-" + name + "/"
		mkdirSync(dir, { recursive: true })
		await icon(Math.round(48 * scale), 0.08, dir + "ic_launcher.png")
		await icon(Math.round(48 * scale), 0.08, dir + "ic_launcher_round.png")
		await icon(Math.round(108 * scale), 0.22, dir + "ic_launcher_foreground.png")
	}
	mkdirSync(res + "values-ar", { recursive: true })
	const xml = (name) =>
		'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n    <string name="app_name">' + name + '</string>\n    <string name="title_activity_main">' + name + "</string>\n</resources>\n"
	writeFileSync(res + "values-ar/strings.xml", xml(tr["Fleetix Maintenance"] || "Fleetix Maintenance"))
}

const pwa = here("../../../frontend/public/icons/")
mkdirSync(pwa, { recursive: true })
await icon(192, 0.1, pwa + "icon-192.png")
await icon(512, 0.1, pwa + "icon-512.png")
