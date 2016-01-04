# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now
from frappe.model.document import Document

class TicketEscalationSettings(Document):
	def validate(self):
		self.validate_escalation_heirarchy_records()
		self.setup_default_profile()

	def on_trash(self):
		if self.name == "Default":
			frappe.throw("Can not delete the Default Escalation Settings")

	def setup_default_profile(self):
		if self.is_default:
			query = """	UPDATE `tabTicket Escalation Settings` SET is_default=0, modified='{now}' WHERE
						name<>'{name}'""".format(now=now(), name=self.name)
			frappe.db.sql(query)
		else:
			docname = frappe.db.get_value("Ticket Escalation Settings", {"is_default":1, "name":["!=", self.name]}, "name")
			if not docname:
				if self.name == "Default":
					self.is_default = 1
				else:
					frappe.db.set_value("Ticket Escalation Settings", "Default", "is_default", 1)
				frappe.msgprint("Setting up the Default Escalation Settings")

	def validate_escalation_heirarchy_records(self):
		# check if escalate hierarchy table have atlease 2 entries
		if not self.escalation_hierarchy or len(self.escalation_hierarchy) < 2:
			frappe.throw("Escalate settings should have at lease two Escalate hierarchy records")
		# check for duplicate entries in escalate hierarchy table
		elif len(set([ch.role for ch in self.escalation_hierarchy])) != len(self.escalation_hierarchy):
			frappe.throw("Escalation hierarchy contains duplicate records")
		else:
			# check if escalation hierarchy record is correct or not
			entries = self.escalation_hierarchy
			self.validate_hierarchy_entries(entries)

	def validate_hierarchy_entries(self, entries):
		"""check order of users roles according the their authority"""
		doc = frappe.get_doc("Role Priority Settings", "Role Priority Settings")
		priority_dict = {ch.role:ch.priority for ch in doc.roles_priority}

		high_role = entries[0].role
		high_priority = priority_dict.get(high_role)
		for ch in entries[1:]:
			if high_priority < priority_dict.get(ch.role):
				frappe.throw("Priority for Role %s is greater than %s"%(ch.role, high_role))
			else:
				high_role, high_priority = ch.role, priority_dict.get(high_role)