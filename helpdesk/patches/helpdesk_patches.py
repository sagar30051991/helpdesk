from __future__ import unicode_literals
import json
import frappe

def execute():
	frappe.db.set_default('desktop:home_page', 'dashboard')
	frappe.db.commit()