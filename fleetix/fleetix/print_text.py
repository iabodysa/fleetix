# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re

MARKUP = re.compile(r"(<[^>]*>|&#?\w+;)")
LTR_RUN = re.compile(r"\(?[0-9A-Za-z](?:[0-9A-Za-z\-_./:,#+() ]*[0-9A-Za-z)])?")


def ltr_runs(value):
	if value is None:
		return ""
	return "".join(
		part if MARKUP.fullmatch(part) else LTR_RUN.sub(r'<span class="tp-lr">\g<0></span>', part)
		for part in MARKUP.split(str(value))
	)
