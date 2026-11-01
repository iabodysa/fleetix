# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from fleetix.fleetix.api.maintenance import WORKER_ROLES
from fleetix.fleetix.print_samples import print_samples
from fleetix.fleetix.thermal_image import thermal_png

EXIT_PASS = "Thermal Gate Exit Pass"


def thermal_format(doctype, print_format):
	if frappe.db.get_value("Print Format", print_format, "doc_type") != doctype:
		frappe.throw(_("Print format {0} not found").format(print_format))


@frappe.whitelist()
def get_print_image(doctype, name, print_format):
	thermal_format(doctype, print_format)
	doc = frappe.get_doc(doctype, name)
	doc.check_permission("print")
	if print_format == EXIT_PASS and doc.docstatus != 1:
		frappe.throw(_("The exit pass prints after the visit is approved and its parts are issued"))
	return thermal_png(doctype, name, print_format)


@frappe.whitelist()
def get_sample_image(label):
	frappe.only_for(WORKER_ROLES)
	sample = next((row for row in print_samples() if row["label"] == label), None)
	if not sample:
		frappe.throw(_("Print format {0} not found").format(label))
	return thermal_png(frappe.as_json(sample["doc"]), None, sample["format"])
