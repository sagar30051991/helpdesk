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
		
		roles = ["Administrator", "Department Head"]
		[roles.append(ch.role) for ch in self.roles_priority if ch.role not in roles]

		self.set('roles_priority', [])
		for i, role in enumerate(roles):
			rl = self.append('roles_priority', {})
			rl.role = role
			rl.priority = len(roles) - i