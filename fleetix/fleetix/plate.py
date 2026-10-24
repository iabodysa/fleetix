# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

from fleetix.fleetix.api.gate import plate_key

ARABIC_LETTERS = str.maketrans(
	"ABJDRSXTEGKLZNHUV",
	"\u0627\u0628\u062d\u062f\u0631\u0633\u0635\u0637\u0639\u0642\u0643\u0644\u0645\u0646\u0647\u0648\u0649",
)
ARABIC_DIGITS = str.maketrans("0123456789", "\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669")


def saudi_plate(plate):
	key = plate_key(plate)
	if not key:
		return None
	digits, letters = key.split("-")
	if not letters or len(digits) > 4 or len(letters) > 3:
		return None
	return {
		"digits": " ".join(digits),
		"letters": " ".join(letters),
		"digits_ar": " ".join(digits.translate(ARABIC_DIGITS)),
		"letters_ar": " ".join(letters.translate(ARABIC_LETTERS)),
	}
