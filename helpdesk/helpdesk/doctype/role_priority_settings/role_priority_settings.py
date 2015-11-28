# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class RolePrioritySettings(Document):
	def validate(self):
		if not self.roles_priority:
			frappe.throw("Please Set the roles priority first")
		
		ttl_record = len(self.roles_priority) + 1
		p = [n for n in xrange(1, ttl_record)][::-1]

		for ch in self.roles_priority:
			ch.priority = p[ch.idx - 1]