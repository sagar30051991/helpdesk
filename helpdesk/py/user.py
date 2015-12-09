import frappe

def validate_user(doc, method):
	"""
		validate user their should be only one department head
	"""
	if doc.name == "Administrator":
		return

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

STANDARD_USERS = ["Guest", "Administrator"]

def user_query(doctype, txt, searchfield, start, page_len, filters):
	from helpdesk.py.todo import get_highest_role, get_role_priority

	highest_role = get_highest_role(frappe.session.user)
	query = ""
	roles = []
	dept = ""
	if highest_role == "Administrator":
		roles = ["Department Head"]
		if isinstance(filters.get("issue"), list):
			dept = validate_multiple_issue_name(filters.get("issue"))
		else:
			dept = frappe.db.get_value("Issue",filters.get("issue"),"department")
		dept = "AND usr.department='{dept}'".format(dept=dept)
	else:
		priority = get_role_priority(highest_role).get("priority")
		roles = frappe.db.sql("select role from `tabRole Priority` where priority < %s"%(priority), as_list=True)
		roles = [role[0] for role in roles]

	query = """	SELECT DISTINCT
				    usr.name,
				    concat_ws(' ', usr.first_name, usr.middle_name, usr.last_name),
				    department
				FROM
				    `tabUser` AS usr
				JOIN
				    `tabUserRole` AS r
				JOIN
				    `tabRole Priority` AS rp
				ON
				    r.role=rp.role
				AND rp.role IN ({roles})
				AND usr.name=r.parent
				AND ifnull(enabled, 0)=1
				AND usr.docstatus < 2
				AND usr.name NOT IN ({standard_users})
				AND usr.user_type != 'Website User' {dept}""".format(
					roles=",".join(["'%s'"%(role) for role in roles]),
					standard_users=", ".join(["'%s'"%(role) for role in STANDARD_USERS]),
					dept=dept)
	return frappe.db.sql(query)

def validate_multiple_issue_name(names):
	query = """SELECT DISTINCT department FROM `tabIssue` WHERE name IN ({names})""".format(
				names=",".join(["'%s'"%(name) for name in names])
			)
	records = frappe.db.sql(query, as_list=True)
	departments = list(set([r[0] for r in records]))
	if not departments:
		frappe.throw("Department field is missing in select Support Ticket")
	elif len(departments) > 1:
		frappe.throw("Can not filter users more than one different departments detected")
	else:
		return departments[0]