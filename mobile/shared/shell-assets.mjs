import { mkdirSync, readFileSync, readdirSync, writeFileSync, copyFileSync, existsSync } from "fs"
import { fileURLToPath } from "url"

const here = (path) => fileURLToPath(new URL(path, import.meta.url))
const LOGO = here("../../fleetix/public/images/fleetix-logo.svg")
const TRANSLATIONS = here("../../fleetix/translations/")
const LANGUAGES = ["ar", "ur", "hi", "bn"]
const BG = "#ffffff"

function csvRows(text) {
	const rows = []
	let row = []
	let cell = ""
	let quoted = false
	for (let index = 0; index < text.length; index++) {
		const char = text[index]
		if (quoted) {
			if (char === '"' && text[index + 1] === '"') {
				cell += '"'
				index++
			} else if (char === '"') quoted = false
			else cell += char
		} else if (char === '"') quoted = true
		else if (char === ",") {
			row.push(cell)
			cell = ""
		} else if (char === "\n" || char === "\r") {
			if (char === "\r" && text[index + 1] === "\n") index++
			row.push(cell)
			rows.push(row)
			row = []
			cell = ""
		} else cell += char
	}
	if (cell || row.length) rows.push(row.concat(cell))
	return rows
}

function translations(lang, keys) {
	const found = {}
	const path = TRANSLATIONS + lang + ".csv"
	if (!existsSync(path)) return found
	csvRows(readFileSync(path, "utf8")).forEach(([source, translation]) => {
		if (keys.indexOf(source) !== -1 && translation && !(source in found)) found[source] = translation
	})
	return found
}

const escape = (text) => text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/'/g, "\\'").replace(/"/g, '\\"')

function resources(strings, pick) {
	return (
		'<?xml version="1.0" encoding="utf-8"?>\n<resources>\n' +
		Object.entries(strings)
			.map(([name, text]) => '    <string name="' + name + '">' + escape(pick(text)) + "</string>\n")
			.join("") +
		'    <string name="title_activity_main">' + escape(pick(strings.app_name)) + "</string>\n</resources>\n"
	)
}

export async function buildShell({ sharp, strings, res, pwa, lockup }) {
	async function splash(out) {
		const { width, height } = await sharp(out).metadata()
		const side = Math.round(Math.min(width, height) * 0.36)
		const art = await sharp(LOGO, { density: 600 }).resize(side, side, { fit: "contain", background: BG }).png().toBuffer()
		const canvas = await sharp({ create: { width, height, channels: 3, background: BG } })
			.composite([{ input: art, gravity: "center" }])
			.png()
			.toBuffer()
		writeFileSync(out, canvas)
	}

	async function icon(size, pad, out) {
		const inner = Math.round(size * (1 - pad * 2))
		const art = await sharp(LOGO, { density: 600 }).resize(inner, inner, { fit: "contain", background: BG }).png().toBuffer()
		await sharp({ create: { width: size, height: size, channels: 4, background: BG } })
			.composite([{ input: art, gravity: "center" }])
			.png()
			.toFile(out)
	}

	if (existsSync(res)) {
		const densities = { mdpi: 1, hdpi: 1.5, xhdpi: 2, xxhdpi: 3, xxxhdpi: 4 }
		for (const [name, scale] of Object.entries(densities)) {
			const dir = res + "mipmap-" + name + "/"
			mkdirSync(dir, { recursive: true })
			await icon(Math.round(48 * scale), 0.08, dir + "ic_launcher.png")
			await icon(Math.round(48 * scale), 0.08, dir + "ic_launcher_round.png")
			await icon(Math.round(108 * scale), 0.22, dir + "ic_launcher_foreground.png")
		}
		for (const dir of readdirSync(res)) {
			if (dir.startsWith("drawable") && existsSync(res + dir + "/splash.png")) await splash(res + dir + "/splash.png")
		}
		writeFileSync(res + "values/shell.xml", resources(strings, (text) => text))
		const keys = Object.values(strings)
		for (const lang of LANGUAGES) {
			const tr = translations(lang, keys)
			mkdirSync(res + "values-" + lang, { recursive: true })
			writeFileSync(res + "values-" + lang + "/strings.xml", resources(strings, (text) => tr[text] || text))
		}
		if (lockup) {
			mkdirSync(res + "drawable-nodpi", { recursive: true })
			copyFileSync(here("../../fleetix/public/images/etihad-lockup.png"), res + "drawable-nodpi/etihad_lockup.png")
		}
	}

	if (pwa) {
		mkdirSync(pwa, { recursive: true })
		await icon(192, 0.1, pwa + "icon-192.png")
		await icon(512, 0.1, pwa + "icon-512.png")
	}
}
