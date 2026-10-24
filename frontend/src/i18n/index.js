export const LANGUAGES = [
	{ code: "ar", name: "العربية", dir: "rtl" },
	{ code: "en", name: "English", dir: "ltr" },
	{ code: "ur", name: "اردو", dir: "rtl" },
	{ code: "hi", name: "हिन्दी", dir: "ltr" },
	{ code: "bn", name: "বাংলা", dir: "ltr" },
]

export function languageOf(code) {
	return LANGUAGES.find((language) => language.code === code) || LANGUAGES[1]
}

export function __(text, args) {
	const boot = (window.frappe && window.frappe.boot) || {}
	let out = (boot.__messages && boot.__messages[text]) || text
	;(args || []).forEach((value, index) => {
		out = out.split("{" + index + "}").join(value)
	})
	return out
}

export function componentLabel(component) {
	return {
		Oil: __("Oil"),
		"Oil Filter": __("Oil Filter"),
		"Front Tires": __("Front Tires"),
		"Rear Tires": __("Rear Tires"),
		Battery: __("Battery"),
	}[component]
}

export const FINDING_REASONS = ["Leak", "Worn", "Noise", "Loose", "Low Level", "Damaged", "Needs Replacement"]

export function reasonLabel(reason) {
	return {
		Leak: __("Leak"),
		Worn: __("Worn"),
		Noise: __("Noise"),
		Loose: __("Loose"),
		"Low Level": __("Low Level"),
		Damaged: __("Damaged"),
		"Needs Replacement": __("Needs Replacement"),
		"Not Done": __("Not Done"),
	}[reason]
}

export function statusLabel(status) {
	return {
		"Due Alert": __("Due Alert"),
		"Driver Arrived": __("Driver Arrived"),
		"Full Inspection": __("Full Inspection"),
		Approved: __("Approved"),
		Service: __("Service"),
		"Final Check": __("Final Check"),
		Completed: __("Completed"),
	}[status]
}

export function isolate(value) {
	return "⁦" + String(value).split("-").join("‑") + "⁩"
}

export function formatKm(value) {
	return Number(value || 0).toLocaleString("en-US") + " " + __("km")
}
