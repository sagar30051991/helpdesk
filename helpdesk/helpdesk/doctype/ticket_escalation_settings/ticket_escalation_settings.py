# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import now
from frappe.model.document import Document

class TicketEscalationSettings(Document):
	def validate(self):
		if self.is_default:
			query = """UPDATE `tabTicket Escalation Settings` SET is_default=0, modified='%s'"""%(now())
			frappe.db.sql(query)
		else:
			docname = frappe.db.get_value("Ticket Escalation Settings", {"is_default":1, "name":["!=", self.name	]}, "name")
			if not docname:
				frappe.throw("System should have atleast one default settings profile")