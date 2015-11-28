from __future__ import unicode_literals
import json
import frappe
# import frappe.defaults
# from frappe.desk.star import _toggle_star

hierarchy = {
	1: {
		"time":2,
		"role": "Administrator",
		"is_dept_escalation": 0
	}
	# 2: {
	# 	"time":2,
	# 	"role": "Administrator",
	# 	"is_dept_escalation": 0
	# }
	# 3: {
	# 	"time":2,
	# 	"role": "Administrator",
	# 	"is_dept_escalation": 0
	# }
	# 4: {
	# 	"time":2,
	# 	"role": "Administrator",
	# 	"is_dept_escalation": 0
	# }
}

def execute():
	esc_settings = frappe.db.get_value("Ticket Escalation Settings","Default")
	if not esc_settings:
		create_escalation_settings_doc()

def create_escalation_settings_doc():
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
	append_rows(esc)