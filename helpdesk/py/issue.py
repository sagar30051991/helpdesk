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
		# "departments": frappe.db.get_all("Department", fields="name as department"),
		"service_type": frappe.db.get_all("Service Type", fields="name as service_type")
		# "categories": frappe.db.get_all("Service Type", fields="name as service_type")
	}

@frappe.whitelist(allow_guest=True)
# def raise_issue(raised_by, department, description, subject):
def raise_issue(**args):
	import json
	import HTMLParser

	args = frappe._dict(args)
	
	issue = frappe.new_doc("Issue")
	issue.raised_by = args.raised_by
	issue.facility = HTMLParser.HTMLParser().unescape(args.facility)
	issue.description = HTMLParser.HTMLParser().unescape(args.description)
	issue.service_type = HTMLParser.HTMLParser().unescape(args.service_type)
	issue.location = HTMLParser.HTMLParser().unescape(args.location)
	issue.building = HTMLParser.HTMLParser().unescape(args.building)
	issue.floor = HTMLParser.HTMLParser().unescape(args.floor)
	issue.area = HTMLParser.HTMLParser().unescape(args.area)
	issue.city = HTMLParser.HTMLParser().unescape(args.city)
	# #write 
	# issue.loc_desc = HTMLParser.HTMLParser().unescape(args.loc_desc)
	# issue.subject = HTMLParser.HTMLParser().unescape(args.subject)

	issue.save(ignore_permissions=True)
	return issue.name