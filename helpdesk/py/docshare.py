import frappe
from frappe.utils import getdate

def validate_docshare(doc, method):
	if doc.share_doctype == "Issue":
		todo = frappe.new_doc("ToDo")
		todo.reference_type = doc.share_doctype
		todo.reference_name = doc.share_name
		todo.description = frappe.db.get_value("Issue", doc.share_name, "description")
		todo.owner = doc.user
		todo.assigned_by = doc.owner
		todo.date = getdate()
		todo.save(ignore_permissions=True)