const LETTERS = { A: "ا", B: "ب", J: "ح", D: "د", R: "ر", S: "س", X: "ص", T: "ط", E: "ع", G: "ق", K: "ك", L: "ل", Z: "م", N: "ن", H: "ه", U: "و", V: "ى" }
const INDIC = "٠١٢٣٤٥٦٧٨٩"
const LATIN = Object.keys(LETTERS).reduce((map, latin) => Object.assign(map, { [LETTERS[latin]]: latin }), { أ: "A", إ: "A", آ: "A", ي: "V", ة: "H" })

export const PLATE_LETTERS = Object.entries(LETTERS)

export function plateKey(plate) {
	const chars = String(plate || "").toUpperCase().replace(/[\sـ-]/g, "").split("")
	const latin = chars.map((c) => (INDIC.indexOf(c) !== -1 ? String(INDIC.indexOf(c)) : LATIN[c] || c))
	return {
		digits: latin.filter((c) => /[0-9]/.test(c)).join(""),
		letters: latin.filter((c) => /[A-Z]/.test(c)).join(""),
	}
}

export function parsePlate(plate) {
	const raw = String(plate || "").toUpperCase()
	const digits = (raw.match(/[0-9]/g) || []).join("")
	const letters = (raw.match(/[A-Z]/g) || []).join("")
	return {
		digits: digits.split("").map((d) => ({ latin: d, arabic: INDIC[Number(d)] })),
		letters: letters.split("").map((l) => ({ latin: l, arabic: LETTERS[l] || l })),
	}
}
