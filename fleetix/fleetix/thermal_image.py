# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import base64
import os
import re
import shutil
import subprocess
from io import BytesIO

import frappe
from frappe import _
from frappe.translate import print_language
from frappe.utils import get_url
from frappe.www.printview import get_html_and_style
from PIL import Image

DOTS = 576
PRINT_LANGUAGE = "ar"
SIDE_MARGIN = 8
TOP_MARGIN = 8
BOTTOM_MARGIN = 24
SUPERSAMPLE = 2
INK_LEVEL = 160
MIN_INK = 0.01
RENDER_TIMEOUT = 60

PAGE = (
	'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{style}</style>'
	"<style>html{{zoom:{zoom}}}html,body{{margin:0;padding:0;background:#FFF}}::-webkit-scrollbar{{display:none}}"
	"body .print-format{{width:{dots}px!important;max-width:none!important;margin:0!important;padding:0!important;min-height:0!important}}</style>"
	'</head><body><div class="print-format">{html}</div></body></html>'
)
LOCAL_URL = r"""(?P<q>["'(])(?P<host>{host})?/(?P<root>assets|files|private/files)/(?P<path>[^"')?#]+)"""


def root_dir(root):
	if root == "assets":
		return os.path.abspath(os.path.join(frappe.local.sites_path, "assets"))
	return os.path.abspath(frappe.get_site_path(*root.split("/")))


def local_url(match):
	base = root_dir(match.group("root"))
	path = os.path.abspath(os.path.join(base, match.group("path")))
	if not path.startswith(base + os.sep):
		return match.group(0)
	return match.group("q") + "file://" + path


def localize(html):
	return re.sub(LOCAL_URL.format(host=re.escape(get_url())), local_url, html)


def page_html(doc, name, print_format):
	with print_language(PRINT_LANGUAGE):
		page = get_html_and_style(doc, name, print_format=print_format, no_letterhead=1)
	if not page.get("html"):
		frappe.throw(_("Print format {0} not found").format(print_format))
	return localize(
		PAGE.format(style=page.get("style") or "", html=page["html"], dots=DOTS, zoom=SUPERSAMPLE)
	)


def rasterize(html):
	binary = shutil.which("wkhtmltoimage")
	if not binary:
		frappe.throw(_("Printing is not installed on the server"))
	command = [
		binary,
		"--quiet",
		"--enable-local-file-access",
		"--disable-smart-width",
		"--encoding",
		"utf-8",
	]
	command += ["--width", str(DOTS * SUPERSAMPLE), "--zoom", "1", "--format", "png", "-", "-"]
	result = subprocess.run(
		command,
		input=html.encode(),
		capture_output=True,
		timeout=RENDER_TIMEOUT,
		env=dict(os.environ, QT_QPA_PLATFORM="offscreen"),
	)
	if not result.stdout:
		frappe.log_error("Thermal print render", result.stderr.decode(errors="replace"))
		frappe.throw(_("Printer error"))
	return Image.open(BytesIO(result.stdout))


def ink_box(gray):
	return gray.point(lambda level: 255 if level < INK_LEVEL else 0).getbbox()


def fit_width(gray, box):
	left, top, right, bottom = box
	width = DOTS - 2 * SIDE_MARGIN
	height = round((bottom - top) * width / (right - left))
	content = gray.crop(box).resize((width, height), Image.LANCZOS)
	page = Image.new("L", (DOTS, TOP_MARGIN + height + BOTTOM_MARGIN), 255)
	page.paste(content, (SIDE_MARGIN, TOP_MARGIN))
	return page


def black_and_white(image):
	gray = image.convert("L")
	box = ink_box(gray)
	if not box:
		frappe.throw(_("The print came out empty, nothing was sent to the printer"))
	ink = fit_width(gray, box).point(lambda level: 0 if level < INK_LEVEL else 255)
	ratio = ink.histogram()[0] / (ink.width * ink.height)
	if ratio < MIN_INK:
		frappe.throw(_("The print came out empty, nothing was sent to the printer"))
	return ink


def thermal_png(doc, name, print_format):
	buffer = BytesIO()
	black_and_white(rasterize(page_html(doc, name, print_format))).save(buffer, format="PNG")
	return base64.b64encode(buffer.getvalue()).decode()
