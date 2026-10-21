# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import base64
from io import BytesIO

import pyqrcode
from frappe.utils import get_url_to_form


def document_qr(doctype, name):
	buffer = BytesIO()
	pyqrcode.create(get_url_to_form(doctype, name)).svg(buffer, scale=4, quiet_zone=1, omithw=False)
	return "data:image/svg+xml;base64," + base64.b64encode(buffer.getvalue()).decode()
