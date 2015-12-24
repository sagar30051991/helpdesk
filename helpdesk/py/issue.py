import frappe

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return None
	# elif "Department Head" in frappe.get_roles(user):
	# 	return """\
	# 	(tabIssue.owner = '{user}' or tabIssue.raised_by = '{user}') and (tabIssue.department = '{dept}')
	# 	or (tabIssue.name in (select tabToDo.reference_name from tabToDo where
	# 		(tabToDo.owner = '{user}' and tabToDo.status = 'Open') or tabToDo.assigned_by = '{user}'
	# 		and tabToDo.reference_type = 'Issue' and tabToDo.reference_name=tabIssue.name))\
	# 	""".format(
	# 			user=frappe.db.escape(user),
	# 			dept=frappe.db.get_value("User", user, "department")
	# 		)
	else:
		return """\
		(tabIssue.owner = '{user}' or tabIssue.raised_by = '{user}') 
		or (tabIssue.name in (select tabToDo.reference_name from tabToDo where
			(tabToDo.owner = '{user}' and tabToDo.status = 'Open') or tabToDo.assigned_by = '{user}'
			and tabToDo.reference_type = 'Issue' and tabToDo.reference_name=tabIssue.name))\
		""".format(user=frappe.db.escape(user))

@frappe.whitelist(allow_guest=True)
def get_subject_and_department_list():
	# departments = [dept.get("name") for dept in frappe.db.get_all("Department", fields="name")]
	# subjects = [subj.get("name") for subj in frappe.db.get_all("Subject", fields="name")]

	# return {
	# 	"departments": departments,
	# 	"subjects": subjects
	# }
	return {
		"departments": frappe.db.get_all("Department", fields="name as department"),
		"subjects": frappe.db.get_all("Subject", fields="name as subject")
	}

@frappe.whitelist(allow_guest=True)
def raise_issue(raised_by, department, description, subject):
	issue = frappe.new_doc("Issue")
	issue.raised_by = raised_by
	issue.department = department
	issue.description = description
	issue.subject = subject
	issue.save(ignore_permissions=True)
	return issue.name