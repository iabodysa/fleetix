export const PLATE_LETTERS = [
	["A", "ا"], ["B", "ب"], ["J", "ح"], ["D", "د"], ["R", "ر"], ["S", "س"],
	["X", "ص"], ["T", "ط"], ["E", "ع"], ["G", "ق"], ["K", "ك"], ["L", "ل"],
	["Z", "م"], ["N", "ن"], ["H", "ه"], ["U", "و"], ["V", "ى"],
]
const ARABIC = Object.fromEntries(PLATE_LETTERS)
const INDIC = "٠١٢٣٤٥٦٧٨٩"

export function parsePlate(plate) {
	const raw = String(plate || "").toUpperCase()
	const digits = (raw.match(/[0-9]/g) || []).join("")
	const letters = (raw.match(/[A-Z]/g) || []).join("")
	return {
		digits: digits.split("").map((d) => ({ latin: d, arabic: INDIC[Number(d)] })),
		letters: letters.split("").map((l) => ({ latin: l, arabic: ARABIC[l] || l })),
	}
}
