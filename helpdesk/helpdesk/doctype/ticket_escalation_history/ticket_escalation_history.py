# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe.utils import nowtime, get_datetime
import frappe

class TicketEscalationHistory(Document):
	pass

def issue_on_update(doc, method):
	# check if record is already exists or not
	esc_name = frappe.db.get_value("Ticket Escalation History",{"ticket_id":doc.name},"name")
	create_update_escalation_history(doc, esc_name=esc_name)

def issue_on_trash(doc, method):
	print "on transh"


def create_update_escalation_history(issue_doc=None, issue_name=None, esc_name=None):
	if not issue_doc:
		issue_doc = frappe.get_doc("Issue", issue_name)

	esc = None
	is_new = True
	if not esc_name:
		# ticket does not exist create new
		esc = frappe.new_doc("Ticket Escalation History")
	else:
		# ticket already exist update escalation history
		esc = frappe.get_doc("Ticket Escalation History", esc_name)
		is_new = False

	esc.ticket_id = issue_doc.name
	esc.status = issue_doc.status
	esc.opening_date = issue_doc.opening_date
	esc.opening_time = issue_doc.opening_time
	if is_new:
		datetime_str = "{date} {time}".format(date=issue_doc.opening_date, time=issue_doc.opening_time)
		esc.assigned_on = get_datetime(datetime_str)

	esc.save(ignore_permissions=True)

def todo_on_update(doc, method):
	if not doc.reference_type and doc.reference_name:
		return
	elif doc.reference_type == "Issue" and not doc.reference_name:
		frappe.throw("Please Select the reference name first")
	elif doc.reference_type == "Issue":
		esc_name = frappe.db.get_value("Ticket Escalation History",{"ticket_id":doc.reference_name}, "name")
		create_update_escalation_record(todo=doc, esc_name=esc_name)

def create_update_escalation_record(todo=None, todo_name=None, esc_name=None):
	if not todo:
		todo = frappe.get_doc("ToDo", todo_name)

	esc = frappe.get_doc("Ticket Escalation History", esc_name)
	rec_id = frappe.db.get_value("Escalation Record",{"parent":esc_name, "todo":todo.name},"name")

	entry = None
	if not rec_id:
		# child entry not found create new entry
		entry = esc.append('items', {})
		entry.todo = todo.name
	else:
		# update child table record and update moodified date of the Ticket Escalation History
		items = esc.items
		entry = [ch for ch in items if ch.get("name") == rec_id][0]
	
	entry.assigned_by = todo.assigned_by
	entry.assigned_to = todo.owner
	entry.todo_status = todo.status
	entry.due_date = todo.date
	esc.is_assigned = 1
	esc.assigned_on = get_datetime()
	esc.save(ignore_permissions=True)