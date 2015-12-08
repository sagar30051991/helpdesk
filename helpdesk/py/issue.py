import frappe

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return None
	elif "Department Head" in frappe.get_roles(user):
		return """\
		(tabIssue.owner = '{user}' or tabIssue.raised_by = '{user}') and (tabIssue.department = '{dept}')
		or (tabIssue.name in (select tabToDo.reference_name from tabToDo where
			(tabToDo.owner = '{user}' and tabToDo.status = 'Open') or tabToDo.assigned_by = '{user}'
			and tabToDo.reference_type = 'Issue' and tabToDo.reference_name=tabIssue.name))\
		""".format(
				user=frappe.db.escape(user),
				dept=frappe.db.get_value("User", user, "department")
			)
	else:
		return """\
		(tabIssue.owner = '{user}' or tabIssue.raised_by = '{user}') 
		or (tabIssue.name in (select tabToDo.reference_name from tabToDo where
			(tabToDo.owner = '{user}' and tabToDo.status = 'Open') or tabToDo.assigned_by = '{user}'
			and tabToDo.reference_type = 'Issue' and tabToDo.reference_name=tabIssue.name))\
		""".format(user=frappe.db.escape(user))
