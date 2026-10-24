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
from frappe.utils import get_url
from frappe.www.printview import get_html_and_style
from PIL import Image

DOTS = 576
PAPER_MM = 72
INK_LEVEL = 150
MIN_INK = 0.01
BOTTOM_MARGIN = 24
RENDER_TIMEOUT = 30

PAGE = (
	'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{style}</style>'
	"<style>html,body{{margin:0;padding:0;background:#FFF}}::-webkit-scrollbar{{display:none}}"
	"body .print-format{{width:{mm}mm!important;max-width:none!important;margin:0!important;padding:0!important;min-height:0!important}}</style>"
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
	page = get_html_and_style(doc, name, print_format=print_format, no_letterhead=1)
	if not page.get("html"):
		frappe.throw(_("Print format {0} not found").format(print_format))
	return localize(PAGE.format(style=page.get("style") or "", html=page["html"], mm=PAPER_MM))


def rasterize(html):
	binary = shutil.which("wkhtmltoimage")
	if not binary:
		frappe.throw(_("Printing is not installed on the server"))
	zoom = DOTS / (PAPER_MM / 25.4 * 96)
	command = [
		binary,
		"--quiet",
		"--enable-local-file-access",
		"--disable-smart-width",
		"--encoding",
		"utf-8",
	]
	command += ["--width", str(DOTS), "--zoom", f"{zoom:.4f}", "--format", "png", "-", "-"]
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


def black_and_white(image):
	page = Image.new("L", (DOTS, image.height), 255)
	page.paste(image.convert("L").crop((0, 0, min(DOTS, image.width), image.height)), (0, 0))
	ink = page.point(lambda level: 0 if level < INK_LEVEL else 255)
	box = ink.point(lambda level: 255 - level).getbbox()
	if box:
		ink = ink.crop((0, 0, DOTS, min(ink.height, box[3] + BOTTOM_MARGIN)))
	ratio = ink.histogram()[0] / (ink.width * ink.height)
	if ratio < MIN_INK:
		frappe.throw(_("The print came out empty, nothing was sent to the printer"))
	return ink


def thermal_png(doc, name, print_format):
	buffer = BytesIO()
	black_and_white(rasterize(page_html(doc, name, print_format))).save(buffer, format="PNG")
	return base64.b64encode(buffer.getvalue()).decode()
