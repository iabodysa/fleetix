const STORE_KEY = "fleetix.store.lang"
const RTL = ["ar", "ur"]

export const LANGUAGES = [
	{ code: "ar", name: "العربية" },
	{ code: "en", name: "English" },
	{ code: "ur", name: "اردو" },
	{ code: "hi", name: "हिन्दी" },
	{ code: "bn", name: "বাংলা" },
]

function boot() {
	return (window.frappe && window.frappe.boot) || {}
}

export function __(text, args) {
	let out = (boot().__messages && boot().__messages[text]) || text
	;(args || []).forEach((value, index) => {
		out = out.split("{" + index + "}").join(value)
	})
	return out
}

export function storedLanguage() {
	try {
		return localStorage.getItem(STORE_KEY)
	} catch (e) {
		return null
	}
}

export function currentLanguage() {
	return boot().lang || "en"
}

export function isRtl(code) {
	return RTL.indexOf(code || currentLanguage()) !== -1
}

export function applyDirection() {
	document.documentElement.lang = currentLanguage()
	document.documentElement.dir = isRtl() ? "rtl" : "ltr"
}

function urlFor(code) {
	const url = new URL(window.location.href)
	url.searchParams.set("_lang", code)
	return url.toString()
}

export function ensureLanguage() {
	const stored = storedLanguage()
	const asked = new URL(window.location.href).searchParams.get("_lang")
	if (stored && stored !== currentLanguage() && asked !== stored) {
		window.location.replace(urlFor(stored))
		return false
	}
	return true
}

export function chooseLanguage(code) {
	try {
		localStorage.setItem(STORE_KEY, code)
	} catch (e) {
		code = code || "en"
	}
	document.cookie = "preferred_language=" + code + "; path=/; max-age=31536000; SameSite=Lax"
	window.location.replace(urlFor(code))
}

export function isolate(value) {
	return "⁦" + String(value) + "⁩"
}
