# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import re

MARKUP = re.compile(r"(<[^>]*>|&#?\w+;)")
LTR_RUN = re.compile(r"\(?[0-9A-Za-z](?:[0-9A-Za-z\-_./:,#+() ]*[0-9A-Za-z)])?")
WORD = re.compile(r"(?P<ltr>{})|[^\s0-9A-Za-z]+".format(LTR_RUN.pattern))


def box(match):
	return '<span class="{}">{}</span>'.format("tp-lr" if match.group("ltr") else "tp-w", match.group(0))


def ltr_runs(value):
	if value is None:
		return ""
	return "".join(
		part if MARKUP.fullmatch(part) else WORD.sub(box, part)
		for part in MARKUP.split(str(value))
	)
