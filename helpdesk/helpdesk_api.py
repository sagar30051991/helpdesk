import frappe

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
	try:
		result = args
	except Exception, e:
		raise Exception("Not Yet Implemented")
	finally:
		return result

@frappe.whitelist()
def updateIssue(args):
	result = {}
	try:
		issue = frappe.get_doc("Issue", args.get("ticket_id"))
		set_values(issue, args)
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
	except Exception, e:
		raise Exception("Not Yet Implemented")
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
