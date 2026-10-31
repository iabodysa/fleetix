# Copyright (c) 2026, Ittihad and contributors
# For license information, please see license.txt

import frappe
from frappe.permissions import add_permission, update_permission_property

PS = "Project Supervisor"
RM = "Rental Manager"
MS = "Movement Supervisor"
MTS = "Maintenance Supervisor"
AC = "Accountant"
DR = "Driver"

READ = ("read",)
EDIT = ("read", "write")
MANAGE = ("read", "write", "create")
SUBMIT = (*MANAGE, "submit", "cancel")

CORE_PERMISSIONS = {
	"Company": {PS: READ, RM: READ, MS: READ, MTS: READ, AC: READ},
	"Customer": {PS: READ, RM: READ, MS: READ, MTS: READ, AC: READ},
	"Project": {RM: MANAGE, PS: READ, MS: READ, MTS: READ, AC: READ},
	"Vehicle": {RM: (*MANAGE, "print"), MS: (*EDIT, "print"), PS: READ, MTS: READ, AC: READ, DR: READ},
	"Driver": {RM: MANAGE, PS: MANAGE, MS: READ, MTS: READ, AC: READ},
	"Item": {AC: MANAGE, MS: READ, RM: READ},
	"Item Group": {AC: READ, MS: READ},
	"Warehouse": {AC: MANAGE, MS: READ},
	"Stock Entry": {AC: SUBMIT, MS: MANAGE, RM: SUBMIT},
	"Stock Ledger Entry": {AC: READ, RM: READ},
}


def grant_core_permissions():
	for doctype, grants in CORE_PERMISSIONS.items():
		for role, ptypes in grants.items():
			if frappe.db.exists(
				"Custom DocPerm", {"parent": doctype, "role": role, "permlevel": 0, "if_owner": 0}
			):
				continue
			add_permission(doctype, role, 0)
			for ptype in ptypes[1:]:
				update_permission_property(doctype, role, 0, ptype, 1)


def revoke_core_permissions():
	roles = {role for grants in CORE_PERMISSIONS.values() for role in grants}
	frappe.db.delete(
		"Custom DocPerm", {"parent": ("in", list(CORE_PERMISSIONS)), "role": ("in", list(roles))}
	)
	frappe.clear_cache()
