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

# def user_query(doctype, txt, searchfield, start, page_len, filters):
# 	from helpdesk.py.todo import get_highest_role, get_role_priority
# 	from frappe.desk.reportview import get_match_cond

# 	highest_role = get_highest_role(frappe.session.user)
# 	query = ""
# 	roles = []
# 	dept = ""
# 	if highest_role == "Administrator":
# 		roles = ["Department Head"]
# 		if isinstance(filters.get("issue"), list):
# 			dept = validate_multiple_issue_name(filters.get("issue"))
# 		else:
# 			dept = frappe.db.get_value("Issue",filters.get("issue"),"department")
# 		dept = "AND usr.department='{dept}'".format(dept=dept)
# 	else:
# 		priority = get_role_priority(highest_role).get("priority")
# 		roles = frappe.db.sql("select role from `tabRole Priority` where priority < %s"%(priority), as_list=True)
# 		roles = [role[0] for role in roles]

# 	txt = "%{}%".format(txt)

# 	query = """	SELECT DISTINCT
# 				    usr.name,
# 				    concat_ws(' ', usr.first_name, usr.middle_name, usr.last_name),
# 				    department
# 				FROM
# 				    `tabUser` AS usr
# 				JOIN
# 				    `tabUserRole` AS r
# 				JOIN
# 				    `tabRole Priority` AS rp
# 				ON
# 				    r.role=rp.role
# 				AND rp.role IN ({roles})
# 				AND usr.name=r.parent
# 				AND ifnull(enabled, 0)=1
# 				AND usr.docstatus < 2
# 				AND usr.name NOT IN ({standard_users})
# 				AND (usr.{key} like %s
# 				AND usr.user_type != 'Website User'
# 				OR concat_ws(' ', first_name, middle_name, last_name) like %s)
# 				{dept} limit %s, %s""".format(
# 					roles=",".join(["'%s'"%(role) for role in roles]),
# 					standard_users=", ".join(["'%s'"%(role) for role in STANDARD_USERS]),
# 					dept=dept,
# 					key=searchfield,
# 				)

# 	return frappe.db.sql(query, tuple([txt, txt, start, page_len]), debug=1)

def user_query(doctype, txt, searchfield, start, page_len, filters):
	from helpdesk.py.todo import get_highest_role, get_role_priority

	highest_role = get_highest_role(frappe.session.user)
	query = ""
	roles_in = []
	roles_not_in = ["Guest"]
	dept = ""
	if highest_role == "Administrator":
		roles_in = ["Department Head"]
		if isinstance(filters.get("issue"), list):
			dept = validate_multiple_issue_name(filters.get("issue"))
		else:
			dept = frappe.db.get_value("Issue",filters.get("issue"),"department")
		dept = "AND usr.department='{dept}'".format(dept=dept) if dept else ""
	else:
		priority = get_role_priority(highest_role).get("priority")
		query = "select role, priority from `tabRole Priority`"
		roles = frappe.db.sql(query, as_dict=True)
		[roles_in.append(result.get("role")) if result.get("priority") < priority else roles_not_in.append(result.get("role")) for result in roles]

	txt = "%{}%".format(txt)
	if not roles_in: roles_in.append("")

	query = """	SELECT DISTINCT
				    usr.name,
				    concat_ws(' ', usr.first_name, usr.middle_name, usr.last_name),
				    usr.department
				FROM
				    `tabUser` AS usr
				JOIN
				    `tabUserRole` AS r
				ON
				    usr.name=r.parent
				JOIN
				    `tabRole Priority` AS rp
				ON
				    r.role=rp.role
				AND rp.role IN ({roles_in})
				AND usr.name NOT IN
				                     (
				                     SELECT DISTINCT
				                         parent
				                     FROM
				                         tabUserRole
				                     WHERE
				                         role IN ({roles_not_in}))
				AND ifnull(enabled, 0)=1
				AND usr.docstatus < 2
				AND (
				        usr.{key} LIKE %s
				    AND usr.user_type != 'Website User'
				    OR  concat_ws(' ', first_name, middle_name, last_name) LIKE %s
				    ) 
				{dept} ORDER BY usr.department ASC limit %s, %s""".format(
					roles_in=",".join(["'%s'"%(role) for role in roles_in]),
					roles_not_in=",".join(["'%s'"%(role) for role in roles_not_in]),
					standard_users=", ".join(["'%s'"%(role) for role in STANDARD_USERS]),
					dept=dept,
					key=searchfield,
				)
	return frappe.db.sql(query, tuple([txt, txt, start, page_len]))


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

@frappe.whitelist(allow_guest=True)
def get_user_details(user):
	fields = ["floor", "extension_number", "wing", "cabin_or_workstation_number", "department"]
	details = frappe.db.get_value("User", user, fields, as_dict=True)
	if details:
		return details
	else:
		return {}