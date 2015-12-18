import frappe
import json
from response import get_response

@frappe.whitelist(allow_guest=True)
def login(args):
	args = json.loads(args)
	try: 
		if args.get("user") and args.get("password"):
			frappe.clear_cache(user = args["user"])
			frappe.local.login_manager.authenticate(args["user"],args["password"])
			frappe.local.login_manager.post_login()
			return get_response(
						message="Logged In",
						status_code=1,
						args={
							"sid":frappe.session.sid,
							"user": args.get("user")
						}
					)
		else:
			raise Exception("Invalid Input")
	except frappe.AuthenticationError,e:
		# http_status_code = getattr(e, "http_status_code", 500)
		return get_response(message="Authentication Error, Please check user id and password")

@frappe.whitelist(allow_guest=True)
def logout(args):
	args = json.loads(args)
	try: 
		if args.get("user") and args.get("sid"):
			manage_user()
			frappe.local.login_manager.logout()
			frappe.db.commit()
			print "hello"
			return get_response(
						message="Logged Out",
						status_code=1,
					)
		else:
			raise Exception("Invalid Input")
	except frappe.AuthenticationError,e:
		return get_response(message="Logout unsuccessful")

@frappe.whitelist()
def reportIssue(args):
	result = {}
	try:
		# create new support ticket
		issue = frappe.new_doc("Issue")
		issue.raised_by = args.get("user")
		issue.owner = args.get("user")
		set_values(issue, args)
		issue.save()
		
		result = {
			"ticket_id":issue.name,
			"display_msg": "Support Ticket Created Sucessfully" 
		}
		send_new_ticket_notification(issue)
	except Exception, e:
		raise Exception("Error while creating Support ticket")
	finally:
		return result

@frappe.whitelist()
def getIssueStatus(args):
	result = {}
	try:
		issue = frappe.get_doc("Issue", args.get("ticket_id"))
		todos = frappe.db.get_values(
						"ToDo",
						{
							"reference_type": "Issue",
							"reference_name": args.get("ticket_id")
						},
						["owner", "assigned_by"],
						as_dict=True
					)
		assigned_to = list(set([todo.get("owner") for todo in todos]))
		assigned_by = list(set([todo.get("assigned_by") for todo in todos]))

		result = {
			"ticket_id": issue.name,
			"subject": issue.subject,
			"status": issue.status,
			"assigned_to": ",".join(assigned_to) if assigned_to else "NA",
			"assigned_by": ",".join(assigned_by) if assigned_by else "NA",
			"display_msg": "Sucessfully Fetched Support ticket",
		}
		return result
	except Exception, e:
		raise Exception("Error while fetching support ticket")
	finally:
		return result

@frappe.whitelist()
def getIssueList(args):
	"""
	sample request
	{
	  "code": 1,
	  "order_by": "DESC",
	  "sort_by": "name",
	  "filter": {
	    "field": "ticket_id",
	    "operation": "=",
	    "value": "10"
	  },
	  "limit": 20,
	  "user": "makarand.b@indictranstech.com",
	  "sid": "1beb53e98c7f2294d325f797cfe4d48e222b07d7ecc5b542d4ec1567",
	}
	"""
	result = {}
	try:
		_fields = {
			"condition":build_condition(args),
			"fields": ",".join([
							"creation", "opening_date", "owner", "raised_by", 
							"first_responded_on", "modified_by", "opening_time",
							"subject", "description", "department",
							"resolution_details", "resolution_date", "name as ticket_id",
							"modified"
						])
		}
		args.update(_fields)
		query = """ SELECT %(fields)s FROM `tabIssue` WHERE %(condition)s ORDER BY 
					%(sort_by)s %(order_by)s LIMIT %(limit)s"""%(args)
		issues = frappe.db.sql(query, as_dict=True)
		result = {
			"total_records": len(issues),
			"issues": issues
		}
	except Exception, e:
		print e
		raise Exception("Not Yet Implemented")
	finally:
		return result

@frappe.whitelist()
def updateIssue(args):
	result = {}
	try:
		issue = frappe.get_doc("Issue", args.get("ticket_id"))
		#TODO Need To Confirm
		if issue.status == "Closed":
			raise Exception("Can not update the Closed ticket")

		set_values(issue, args)
		issue.save()
		result = {
			"ticket_id": issue.name,
			"display_msg": "Sucessfully Updated Support ticket",
		}
	except Exception, e:
		raise Exception("Error while updating support ticket")
	finally:
		return result


@frappe.whitelist()
def getIssueHistory(args):
	try:
		result = True
		tes_dn = frappe.db.get_value("Ticket Escalation History", {"ticket_id":args.get("ticket_id")}, "name")
		tes = frappe.get_doc("Ticket Escalation History", tes_dn)

		escalation_record = {}
		for r in tes.items:
			escalation_record.update({
				r.idx: {
					"assigned_to": r.assigned_to,
					"assigned_by": r.assigned_by,
					"todo_id": r.todo,
					"todo_status": r.todo_status,
					"due_date": r.due_date
				}
			})

		result = {
			"ticket_id": tes.ticket_id,
			"status": tes.status,
			"opening_date": tes.opening_date,
			"opening_time": tes.opening_time,
			"is_assigned": tes.is_assigned,
			"currently_assigned_to": tes.current_owner,
			"currently_assigned_to_role": tes.current_role,
			"assigned_to_date": tes.assigned_on,
			"escalation_record": escalation_record,
			"escalation_history_id": tes.name
		}
	except Exception, e:
		raise Exception("Error while fetching support ticket history")
	finally:
		return result

# @frappe.whitelist()
# def deleteIssue(args):
# 	try:
# 		result = True
# 	except Exception, e:
# 		raise Exception("Not Yet Implemented")
# 	finally:
# 		return result

def set_values(issue, args):
	issue.subject = args.get("subject")
	issue.description = args.get("description")
	issue.department = args.get("department")

def build_condition(args):
	filters = args.get("filter")
	condition = ""
	field = filters.get("field") if filters.get("field") != "ticket_id" else "name"
	val = filters.get("value")
	op = filters.get("operation")

	if filters == "default_filter":
		return ""
	elif field != "raised_by":
		if op in ["NOT IN", "IN"]:
			condition = "{0} {1} ({2})".format(field, op, ",".join(["'%s'"%(v) for v in val]))
		else:
			condition = "{0}{1}'{2}'".format(field, op, val)

		condition = "raised_by='{user}' AND {cond}".format(user=args.get('user'), cond=condition)
	else:
		condition = "{0}{1}'{2}'".format(field, op, val)

	perm = 	"""or (tabIssue.name in (select tabToDo.reference_name from tabToDo where
			(tabToDo.owner = '{user}' and tabToDo.status = 'Open') or tabToDo.assigned_by = '{user}'
			and tabToDo.reference_type = 'Issue' and tabToDo.reference_name=tabIssue.name))\
			""".format(user=args.get("user"))

	return "{condition} {permissions}".format(condition=condition, permissions=perm)

# def build_condition(filters):
# 	if filters == "default_filter":
# 		return ""
# 	else:
# 		field = filters.get("field") if filters.get("field") != "ticket_id" else "name"
# 		val = filters.get("value")
# 		op = filters.get("operation")
# 		if op in ["NOT IN", "IN"]:
# 			return "{0} {1} ({2})".format(field, op, ",".join(["'%s'"%(v) for v in val]))
# 		else:
# 			return "{0}{1}'{2}'".format(field, op, val)

def send_new_ticket_notification(doc):
	from utils import send_mail, build_table

	ticket = {
		"total":6,
		# "head": ["Ticket ID", "Department", "Opening Date", "Opening Time", "Subject", "Raised By"]
		1:["Ticket ID", doc.name],
		2:["Department", doc.department],
		3:["Opening Date", doc.opening_date],
		4:["Opeing Time", doc.opening_time],
		5:["Subject", doc.subject],
		6:["Raised By", doc.raised_by]
	}
	args = {
		"email": doc.raised_by,
		"user": doc.raised_by,
		"issue": doc.name,
        "action": "new_ticket",
        "ticket_detail": build_table(ticket, is_horizontal=True)
	}
	send_mail(args, "[HelpDesk][New Ticket] HelpDesk Notifications")