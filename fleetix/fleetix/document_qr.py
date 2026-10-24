# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import base64
from io import BytesIO

import pyqrcode
from frappe.utils import get_url_to_form
from PIL import Image

QUIET_ZONE = 4


def document_qr(doctype, name, dots=None):
	url = get_url_to_form(doctype, name)
	return qr_png_data_url(url, dots) if dots else qr_data_url(url)


def qr_data_url(text):
	buffer = BytesIO()
	pyqrcode.create(text).svg(buffer, scale=4, quiet_zone=1, omithw=False)
	return "data:image/svg+xml;base64," + base64.b64encode(buffer.getvalue()).decode()


def qr_png_data_url(text, dots):
	code = pyqrcode.create(text, error="M").code
	side = len(code) + 2 * QUIET_ZONE
	modules = Image.new("1", (side, side), 1)
	modules.putdata([0 if cell else 1 for row in pad(code, side) for cell in row])
	module = max(1, dots // side)
	buffer = BytesIO()
	modules.resize((side * module, side * module), Image.NEAREST).save(buffer, format="PNG")
	return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()


def pad(code, side):
	blank = [0] * side
	rows = [blank] * QUIET_ZONE + [[0] * QUIET_ZONE + list(row) + [0] * QUIET_ZONE for row in code]
	return rows + [blank] * QUIET_ZONE
