import frappe

def get_permission_query_conditions(user):
	if not user: user = frappe.session.user

	if "System Manager" in frappe.get_roles(user):
		return None
	else:
		return """\
		 (tabIssue.owner = '{user}' or tabIssue.raised_by = '{user}') 
		 or (tabIssue.name in (select tabToDo.reference_name from tabToDo where
		 	(tabToDo.owner = '{user}' or tabToDo.assigned_by = '{user}') and tabToDo.status = 'Open' 
		 	and tabToDo.reference_type = 'Issue' and tabToDo.reference_name=tabIssue.name))\
		 """.format(user=frappe.db.escape(user))

@frappe.whitelist(allow_guest=True)
def get_subject_and_department_list():
	return {
		"departments": frappe.db.get_all("Department", fields="name as department"),
		"subjects": frappe.db.get_all("Subject", fields="name as subject"),
		"categories": frappe.db.get_all("Category", fields="name as category")
	}

@frappe.whitelist(allow_guest=True)
# def raise_issue(raised_by, department, description, subject):
def raise_issue(**args):
	import json
	import HTMLParser

	args = frappe._dict(args)
	
	issue = frappe.new_doc("Issue")
	issue.raised_by = args.raised_by
	issue.department = HTMLParser.HTMLParser().unescape(args.department)
	issue.description = HTMLParser.HTMLParser().unescape(args.description)
	issue.subject = HTMLParser.HTMLParser().unescape(args.subject)
	issue.category = HTMLParser.HTMLParser().unescape(args.category)
	issue.floor = HTMLParser.HTMLParser().unescape(args.floor)
	issue.wing = HTMLParser.HTMLParser().unescape(args.wing)
	issue.extension_number = HTMLParser.HTMLParser().unescape(args.extension_number)
	issue.cabin_or_workstation_number = HTMLParser.HTMLParser().unescape(args.cabin_or_workstation_number)
	issue.save(ignore_permissions=True)
	return issue.name