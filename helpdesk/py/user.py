import frappe

def validate_user(doc, method):
	"""
		validate user their should be only one department head
	"""
	query = """ SELECT name FROM `tabUser` WHERE department='%s' AND
				name IN (SELECT parent FROM `tabUserRole` WHERE role='Department Head')"""%(doc.department)
	record = frappe.db.sql(query)

	dept_head = [ch.role for ch in doc.user_roles if ch.role == "Department Head"]

	if record and dept_head:
		frappe.throw("Their can be only one Department Head for %s"%(doc.department))
	elif not record and dept_head:
		frappe.throw("[Warning] Their is no Department Head for the %s Department"%(doc.department))