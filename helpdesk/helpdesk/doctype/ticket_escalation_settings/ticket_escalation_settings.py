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
			query = """UPDATE `tabTicket Escalation Settings` SET is_default=0, modified='%s'"""%(now())
			frappe.db.sql(query)
		else:
			docname = frappe.db.get_value("Ticket Escalation Settings", {"is_default":1, "name":["!=", self.name]}, "name")
			if not docname:
				frappe.db.set_value("Ticket Escalation Settings", "Default", "is_default", 1)
				# frappe.throw("System should have atleast one default settings profile")
				frappe.msgprint("Setting up the Default Escalation Settings")

	def validate_escalation_heirarchy_records(self):
		# check if escalate hierarchy table have atlease 2 entries
		if not self.escalation_hierarchy or len(self.escalation_hierarchy) < 2:
			frappe.throw("Escalate settings should have at lease two Escalate hierarchy records")
		# check for duplicate entries in escalate hierarchy table
		elif len(set([ch.role for ch in self.escalation_hierarchy])) != len(self.escalation_hierarchy):
			frappe.throw("Escalation hierarchy contains duplicate records")
		else:
			# TODO check if escalation hierarchy record is correct or not
			pass