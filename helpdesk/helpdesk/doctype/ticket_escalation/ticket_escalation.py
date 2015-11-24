# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class TicketEscalation(Document):
	def validate(self):
		self.validate_is_default()
		self.validate_escalation_records()

	def validate_is_default(self):
		if not frappe.db.get_values("Ticket Escalation", "*", "name"):
			if not self.is_default:
				frappe.throw("Their Should be atlease one default Ticket Escalation record")
		else:
			dt = frappe.db.get_value("Ticket Escalation", {"is_default":1}, "name")
			if self.is_default:
				frappe.db.set_value("Ticket Escalation", dt, "is_default", 0)

	def validate_escalation_records(self):
		if not self.escalation_hierarchy:
			frappe.throw("Escalation Hierarchy records are missing")
			