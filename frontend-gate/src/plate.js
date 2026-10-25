import { currentLanguage } from "./i18n.js"

export const PLATE_LETTERS = [
	["A", "ا"], ["B", "ب"], ["J", "ح"], ["D", "د"], ["R", "ر"], ["S", "س"],
	["X", "ص"], ["T", "ط"], ["E", "ع"], ["G", "ق"], ["K", "ك"], ["L", "ل"],
	["Z", "م"], ["N", "ن"], ["H", "ه"], ["U", "و"], ["V", "ى"],
]
const ARABIC = Object.fromEntries(PLATE_LETTERS)
const LATIN = Object.fromEntries(PLATE_LETTERS.map(([latin, arabic]) => [arabic, latin]).concat([["أ", "A"], ["إ", "A"], ["آ", "A"], ["ي", "V"]]))
const INDIC = "٠١٢٣٤٥٦٧٨٩"

export function arabicPlate() {
	return currentLanguage() === "ar"
}

export function plateDigit(digit) {
	return arabicPlate() ? INDIC[Number(digit)] : digit
}

export function plateLetter(letter) {
	return arabicPlate() ? ARABIC[letter] || letter : letter
}

function latinChar(char) {
	const indic = INDIC.indexOf(char)
	return indic !== -1 ? String(indic) : LATIN[char] || char
}

export function parsePlate(plate) {
	const raw = Array.from(String(plate || "").toUpperCase()).map(latinChar).join("")
	return {
		digits: (raw.match(/[0-9]/g) || []).map(plateDigit).join(""),
		letters: (raw.match(/[A-Z]/g) || []).map(plateLetter).join(" "),
	}
}
