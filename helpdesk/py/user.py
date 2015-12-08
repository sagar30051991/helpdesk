import frappe

def validate_user(doc, method):
	"""
		validate user their should be only one department head
	"""
	query = """ SELECT name FROM `tabUser` WHERE department='%s' AND
				name IN (SELECT parent FROM `tabUserRole` WHERE role='Department Head')"""%(doc.department)
	record = frappe.db.sql(query, as_list=True)

	dept_head = [ch.role for ch in doc.user_roles if ch.role == "Department Head"]
	record = [r[0] for r in record]

	if record and dept_head and doc.name not in record:
		frappe.throw("Their can be only one Department Head for %s"%(doc.department))
	elif not record and not dept_head:
		frappe.msgprint("[Warning] Their is no Department Head for the <b>{0}</b> Department<br>\
			Please set the Department Head for <b>{0}</b>".format(doc.department))