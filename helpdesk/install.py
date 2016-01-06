from __future__ import unicode_literals
import json
import frappe

hierarchy = {
	1: {
		"time":2,
		"role": "Administrator",
		"is_dept_escalation": 0
	},
	2: {
		"time":2,
		"role": "Department Head",
		"is_dept_escalation": 0
	}
}

roles_priority = ["Administrator","Department Head"]
# subject = []

def after_install():
	check_hod_role()
	create_escalation_settings_doc()
	setup_role_priority_settings()

def check_hod_role():
	if not frappe.db.get_value("Role", "Department Head", "name"):
		doc = frappe.new_doc("Role")
		doc.role_name = "Department Head"
		doc.save(ignore_permissions=True)

def create_escalation_settings_doc():
	if frappe.db.get_value("Ticket Escalation Settings","Default"):
		return

	def append_rows(doc):
		"""Append Escalation Hierarchy"""
		doc.set("escalation_hierarchy",[])
		for idx, ch_rec in hierarchy.iteritems():
			ch = doc.append("escalation_hierarchy", {})
			ch.time = ch_rec.get("time")
			ch.role = ch_rec.get("role")
			ch.is_dept_escalation = ch_rec.get("is_dept_escalation")

	if not frappe.db.get_value("Priority","Default","name"):
		frappe.get_doc({
			"doctype": "Priority",
			"priority": "Default"
		}).insert(ignore_permissions=True)

	esc = frappe.new_doc("Ticket Escalation Settings")
	esc.priority = "Default"
	esc.is_default = 1
	append_rows(esc)
	esc.save(ignore_permissions=True)

def setup_role_priority_settings():
	doc = frappe.get_doc("Role Priority Settings", "Role Priority Settings")
	if not doc.roles_priority:
		for i, role in enumerate(roles_priority):
			rl = doc.append('roles_priority', {})
			rl.role = role
			rl.priority = len(roles_priority) - i
	doc.save(ignore_permissions=True)
