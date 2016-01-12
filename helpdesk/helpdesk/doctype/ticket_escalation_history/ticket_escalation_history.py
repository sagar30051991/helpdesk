# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from helpdesk.utils import send_mail
from frappe.model.document import Document
from frappe.utils import nowtime, get_datetime

class TicketEscalationHistory(Document):
	pass

def issue_on_update(doc, method):
	# check if record is already exists or not
	esc_name = frappe.db.get_value("Ticket Escalation History",{"ticket_id":doc.name},"name")
	create_update_escalation_history(doc, esc_name=esc_name)

def issue_on_trash(doc, method):
	# TODO check
	esc_name = frappe.db.get_value("Ticket Escalation History",{"ticket_id":doc.name},"name")
	frappe.db.set_value("Ticket Escalation History", esc_name, "status", "Deleted")


def create_update_escalation_history(issue_doc=None, issue_name=None, esc_name=None):
	if not issue_doc:
		issue_doc = frappe.get_doc("Issue", issue_name)

	esc = None
	is_new = True
	args = {
		"user": "User",
		"email": issue_doc.raised_by,
		"action": "user_issue_notification",
		"issue": issue_doc
	}

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
		esc.current_owner = "Administrator"
		esc.current_role = "Administrator"
		
		args.update({
			"msg": "A Support Ticket {name} has been created successfully in \
			the HelpDesk System, please check the Support Ticket details".format(name=issue_doc.name)
		})
		send_mail(args, "[HelpDesk][Issue Raised] HelpDesk Notifications")
		print args.get("email")
		
		esc.raised_email_notification = 1
		esc.raised_email_notification_datetime = get_datetime().now()

	# mail notification to email if issue status is closed
	elif issue_doc.status == "Closed" and not esc.status_closed_email_notification:
		args.update({
			"msg": "A Support Ticket {name}'s status has been changed to Closed, \
			please check the Support Ticket details".format(name=issue_doc.name)
		})
		send_mail(args, "[HelpDesk][Ticket Closed] HelpDesk Notifications")
		
		esc.status_closed_email_notification = 1
		esc.status_closed_email_notification_datetime = get_datetime().now()

	esc.save(ignore_permissions=True)

def todo_on_update(doc, method):
	if not doc.reference_type and doc.reference_name:
		return
	elif doc.reference_type == "Issue":
		# condition = not doc.reference_name and not doc.assigned_by and not doc.role
		# if not doc.reference_name:
		# 	frappe.throw("Please select the reference name field first")
		# if not doc.assigned_by:
		# 	frappe.throw("Please select the assigned by field first")
		# if not doc.role:
		# 	frappe.throw("Please select the assigned by field first")
	
		esc_name = frappe.db.get_value("Ticket Escalation History",{"ticket_id":doc.reference_name}, "name")
		create_update_escalation_record(todo=doc, esc_name=esc_name)

def todo_on_trash(doc, method):
	# ToDo
	pass

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

		# Ticket assignment Email Notification to User
		issue = frappe.get_doc("Issue", esc.ticket_id)
		if not esc.assigned_email_notification:
			args = {
				"user": "User",
				"msg": "Your Support Ticket ({name}) has been assigned to our support representative\
				Please check the support ticket details".format(name=issue.name),
				"email": issue.raised_by,
				"action": "user_issue_notification",
				"issue": issue
			}

			send_mail(args, "[HelpDesk][Ticket Assigned] HelpDesk Notifications")
		
			esc.assigned_email_notification = 1
			esc.assigned_email_notification_datetime = get_datetime().now()

	else:
		# update child table record and update moodified date of the Ticket Escalation History
		items = esc.items
		entry = [ch for ch in items if ch.get("name") == rec_id][0]
	
	entry.assigned_by = todo.assigned_by
	entry.assigned_to = todo.owner
	entry.todo_status = todo.status
	entry.due_date = todo.date
	esc.is_assigned = 1
	# esc.assigned_on = get_datetime("{date} {time}".format(date=todo.date, time=todo.due_time))
	esc.assigned_on = get_datetime()
	esc.current_owner = todo.owner
	esc.current_role = todo.assigned_to_role
	esc.save(ignore_permissions=True)