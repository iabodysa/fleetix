import { api } from "../api.js"
import { LANGUAGES, languageOf } from "../i18n/index.js"

const DEVICE_KEY = "fleetix.maintenance.language"
const boot = (window.frappe && window.frappe.boot) || {}

function readDevice() {
	try {
		return localStorage.getItem(DEVICE_KEY)
	} catch (e) {
		return null
	}
}

function writeDevice(code) {
	try {
		localStorage.setItem(DEVICE_KEY, code)
	} catch (e) {
		return
	}
}

function reloadIn(code) {
	const url = new URL(window.location.href)
	url.searchParams.set("_lang", code)
	window.location.replace(url.toString())
}

export function useLanguage() {
	const current = languageOf(boot.lang)

	function applyDocument() {
		document.documentElement.lang = current.code
		document.documentElement.dir = current.dir
	}

	function chosen() {
		return readDevice()
	}

	async function choose(code) {
		writeDevice(code)
		document.cookie = "preferred_language=" + code + "; path=/; max-age=31536000; samesite=lax"
		if (boot.user && boot.user !== "Guest") await api.setLanguage(code).catch(() => null)
		reloadIn(code)
	}

	function followDevice() {
		const device = readDevice()
		if (!device || device === current.code || new URL(window.location.href).searchParams.has("_lang")) return false
		choose(device)
		return true
	}

	return { languages: LANGUAGES, current, applyDocument, chosen, choose, followDevice }
}
