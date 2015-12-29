import frappe
from frappe.utils import getdate

def validate_docshare(doc, method):
	is_todo_exists = is_todo_already_exists(docname=doc.share_name, assigned_by=doc.owner, assigned_to=doc.user)
	if doc.share_doctype == "Issue" and not is_todo_exists:
		todo = frappe.new_doc("ToDo")
		todo.reference_type = doc.share_doctype
		todo.reference_name = doc.share_name
		todo.description = frappe.db.get_value("Issue", doc.share_name, "description")
		todo.owner = doc.user
		todo.assigned_by = doc.owner
		todo.date = getdate()
		todo.save(ignore_permissions=True)

def is_todo_already_exists(docname=None, assigned_by=None, assigned_to=None):
	filters = {
		"owner":assigned_to,
		"assigned_by":assigned_by,
		"reference_type": "Issue",
		"reference_name": docname
	}

	if frappe.db.get_value("ToDo", filters, "name"):
		return True
	else:
		return False