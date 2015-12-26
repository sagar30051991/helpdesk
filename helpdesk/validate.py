import json
import frappe
from response import get_response
from utils import get_json_request
from utils import get_attr
from conf import api_request_schema as schema
from utils import is_valid_datetime

def validate_request():
	validate_url()
	
	args  = get_json_request(frappe.local.form_dict.args)
	cmd = frappe.local.form_dict.cmd
	# method = cmd.split(".")[2] if cmd != "login" else cmd
	method = cmd.split(".")[2] if cmd not in ["login", "logout"] else cmd

	# if method != "login": validate_user_against_session_id(args)
	if method not in ["login", "logout"]: validate_user_against_session_id(args)
	validate_request_parameters(method, args)

def validate_url():
	parts = frappe.request.path[1:].split("/")
	call = cmd = None

	if len(parts) > 1:
		call = parts[1]

	if len(parts) > 2:
		cmd = parts[2]

	# if call == "login" and len(parts) == 2:
	# 	frappe.local.form_dict.cmd = "login"

	if call in ["login", "logout"] and len(parts) == 2:
		frappe.local.form_dict.cmd = call

	elif call== "issue" and len(parts) == 3:
		try:
			cmd = "helpdesk.helpdesk_api.{0}".format(cmd)
			method = get_attr(cmd)
			frappe.local.form_dict.cmd = cmd
		except Exception, e:
			raise Exception("Invalid API-URL")
	else:
		raise Exception("Invalid API-URL")

def validate_request_parameters(method, args):
	"""validate the request parameters check all the fields"""
	validate_request_fields(method, args)
	validate_request_methods[method](args)

def validate_request_fields(method, args):
	"""validate all the request fields for mandetory, length and type"""
	fields_dict = schema.get(method)
	if not fields_dict:
		raise Exception("Field schema is missing, Please contact Administrator")
	else:
		validate_mandatory_fields(fields_dict, args)
		validate_fields_length_and_type(fields_dict, args)

def validate_mandatory_fields(fields_dict, args):
	# check the request for missing/mandatory or for extra fields
	missing_fields = ["'%s'"%(field) for field in fields_dict.get("fields").keys() if field not in args.keys() and fields_dict.get("fields").get(field).get("is_mandatory")]
	extra_fields = ["'%s'"%(field) for field in args.keys() if field not in fields_dict.get("fields").keys()]
	
	if missing_fields and extra_fields:
		raise Exception(
				"Mandatory field{0} {1} {2} missing also request contains extra_field{3} {4}".format(
					"s" if len(missing_fields) >= 2 else "",
					",".join(missing_fields),
					"are" if len(missing_fields) >= 2 else "is",
					"s" if len(extra_fields) >= 2 else "",
					",".join(extra_fields))
				)
	elif missing_fields:
		raise Exception("Request is missing following mandatory fields : {0}".format(",".join(missing_fields)))
	elif extra_fields:
		raise Exception("Request contains following extra_fields : {0}".format(",".join(extra_fields)))

def validate_fields_length_and_type(fields_dict, args):
	all_fields = fields_dict.get("fields")
	if not all_fields:
		raise Exception("Field schema is missing, Please contact Administrator")
	else:
		invalid_fields = []
		len_exceeded = []
		for field, prop in all_fields.iteritems():
			# check the field length
			if prop.get("length") and isinstance(args.get(field), basestring) and len(args.get(field)) > prop.get("length"):
				len_exceeded.append("'%s'"%(field))

			# check the field type
			if not isinstance(args.get(field), prop.get("type")):
				invalid_fields.append(field)

		if len_exceeded:
			raise Exception(
					"Request parameters length exceeded for following field(s) : {0}".format(",".join(len_exceeded))
				)

def validate_login_request(args):
	# TODO
	pass

def validate_logout_request(args):
	# TODO
	pass

def validate_report_issue_request(args):
	try:
		issue = is_issue_already_exists(args)
		if not issue:
			is_valid_user(args.get("user"))
			is_valid_subject(args.get("subject"))
			is_valid_department(args.get("department"))
			if not check_user_permission(args, ptype="create"):
				raise Exception("User don't have permissions to create the ticket".format(args.get("ticket_id")))
		else: 
			raise Exception("Similer Issue is already Created by the user, Please check Issue : {0}".format(",".join(issue)))
	except Exception, e:
		raise e

def validate_get_issue_status_request(args):
	try:
		if not does_issue_exists(args.get("ticket_id")):
			raise Exception("{0} Support Ticket Does Not Exists".format(args.get("ticket_id")))
		else:
			# ticket exists check if user is the owner of ticket or allowed to access the issue
			if not check_user_permission(args):
				raise Exception("User don't have permissions to access the ticket".format(args.get("ticket_id")))
	except Exception, e:
		raise e

def validate_get_list_request(args):
	if not check_user_permission(args):
		raise Exception("User don't have permissions to access the ticket".format(args.get("ticket_id")))

	fields_dict = schema.get("getIssueList").get("fields")
	validate_filters_parameter(fields_dict, args)
	validate_sort_by_parameter(fields_dict, args)
	validate_order_by_parameter(fields_dict, args)
	validate_limit_parameter(fields_dict, args)

	frappe.local.form_dict.args = json.dumps(args)

def validate_update_issue_request(args):
	try:
		if not does_issue_exists(args.get("ticket_id")):
			raise Exception("{0} Support Ticket Does Not Exists".format(args.get("ticket_id")))
		else:
			# check if request contains any other fields other than sid & user
			if not [key for key in args.keys() if key not in ["user", "sid", "ticket_id"]]:
				raise Exception("Nothing to update")
			else:
				# only admin should be able to change the department
				dept = args.get("department")
				is_valid_department(dept)
				is_valid_subject(args.get("subject"))
				if dept and dept != frappe.db.get_value("Issue", args.get("ticket_id"), "department"):
					if args.get("user") != "Administrator":
						# raise Exception("Only Administrator is allowed to update the department")
						raise Exception("Invalid department value")
				# check if user is assigned_to user
				if frappe.db.get_value("Issue", args.get("ticket_id"), "owner") != args.get("user"):
					user = frappe.db.get_value(
							"ToDo",
							{
								"reference_type": "Issue",
								"reference_name": args.get("ticket_id"),
								"owner": args.get("user")
							},
							"owner"
						)
					if not user and user != args.get("user"):
						raise Exception("User don't have permissions to update the support ticket")
	except Exception, e:
		raise e

def validate_delete_issue_request(args):
	# TODO
	pass

def validate_issue_history_request(args):
	try:
		tes = frappe.db.get_value("Ticket Escalation History", {"ticket_id":args.get("ticket_id")}, "name")
		if tes:
			is_valid_user(args.get("user"))
			if not check_user_permission(args, ptype="read"):
				raise Exception("User don't have permissions to read the ticket escalation history")
		else: 
			raise Exception("Ticket Escalation History not found for support ticket : {0}".format(args.get("ticket_id")))
	except Exception, e:
		raise e

def is_valid_user(email):
	user = frappe.db.get_value("User", {"email":email}, ["email","enabled", "first_name"], as_dict=True)
	if not user and user.get("email") == email:
		raise Exception("Invalid email id")
	elif not user.get("enabled"):
		raise Exception("{0}'s Profile has been disabled, Please contact Administrator".format(user.get("first_name")))
	# TODO check if support user ??
	else:
		return True			# valid user

def is_valid_department(department):
	if not frappe.db.get_value("Department", department, "name") == department:
		raise Exception("Invalid Department")
	else:
		return True

def is_issue_already_exists(args):
	query = """ SELECT DISTINCT name FROM tabIssue WHERE raised_by='%s' AND status='Open'
				AND subject='%s' AND department='%s'"""%(
					args.get("user"),
					args.get("subject"),
					args.get("department")
				)
	issue = frappe.db.sql(query, as_list=True)
	if issue:
		return [i[0] for i in issue]

def does_issue_exists(issue):
	if not frappe.db.get_value("Issue", issue, "name"):
		return False
	else:
		return True

def check_user_permission(args, ptype="read"):
	issue = args.get("ticket_id")
	user = args.get("user")
	# check if user is owner or not
	if frappe.db.get_value("Issue", issue, "owner") != user:
		# check if user have permissions to read issue
		if not frappe.has_permission("Issue", ptype=ptype, user=user):
			return False
		else:
			return True
	else:
		return True

def validate_limit_parameter(fields_dict, args):
	"""validate limit parameter"""
	
	limit = fields_dict.get("limit")
	if not args.get("limit"):
		args.update({"limit":limit.get("default")})
	elif args.get("limit") > limit.get("max_value"):
		raise Exception("Max value for limit parameter is {0}".format(limit.get("max_value")))
	elif args.get("limit") <= 0:
		raise Exception("Invalid limit parameter value")

def validate_order_by_parameter(fields_dict, args):
	"""validate order by parameter"""
	order_by = fields_dict.get("order_by")
	if not args.get("order_by"):
		args.update({"order_by":order_by.get("default")})
	elif args.get("order_by") not in order_by.get("options"):
		raise Exception("Invalid order by value, value should either {0}".format(" or ".join(order_by.get("options"))))

def validate_sort_by_parameter(fields_dict, args):
	"""validate sort by parameter"""
	sort_by = fields_dict.get("sort_by")
	if not args.get("sort_by"):
		args.update({"sort_by":sort_by.get("default")})
	elif args.get("sort_by") not in sort_by.get("options"):
		raise Exception("Invalid order by value, value should one of the following [{0}]".format(",".join(sort_by.get("options"))))

def validate_filters_parameter(fields_dict, args):
	"""validate filters parameter"""
	_filter_sch = fields_dict.get("filter")
	_filter = args.get("filter")
	if not _filter:
		default_filter = {
			"field":_filter_sch.get("default_field"),
			"operation": _filter_sch.get("default_operation"),
			"value": args.get("user")
		}
		args.update({"filter":default_filter})
	elif [key for key in _filter.keys() if key not in ["field", "operation", "value"]]:
		raise Exception("Invalid filter format")
	elif _filter.get("field") not in _filter_sch.get("allowed_field"):
		raise Exception("Invalid field, field should be one of following [{0}]".format(",".join(_filter_sch.get("allowed_field"))))
	elif _filter.get("operation") not in _filter_sch.get("allowed_operations"):
		raise Exception("Invalid operation, operation should be one of following [{0}]".format(",".join(_filter_sch.get("allowed_operations"))))
	elif not _filter.get("value"):
		raise Exception("Value field is missing in filter")
	elif not (isinstance(_filter.get("value"), basestring) or isinstance(_filter.get("value"), list)):
		raise Exception("Invalid type for value field")
	if _filter.get("field") == "status":
		val = _filter.get("value")
		if isinstance(val, list):
			for status in val:
				if status not in ["Open", "Closed", "Replied", "Hold"]:
					raise Exception("Invalid status value, value should be Open, Closed, Hold or Replied")
		elif val not in ["Open", "Closed", "Replied", "Hold"]:
			raise Exception("Invalid status value, value should be Open, Closed, Hold or Replied")

	if _filter: is_valid_field_and_operation_combo(_filter_sch, _filter)

def is_valid_field_and_operation_combo(fields_dict, _filter):
	# TODO add like
	op = _filter.get("operation")
	field = _filter.get("field")
	val = _filter.get("value")
	date_format = "%Y-%m-%d %H:%M:%S"

	if op in ["IN", "NOT IN"] and not isinstance(val, list):
		raise Exception("For {0} operation type of value field must be List".format(op))
	elif op not in ["IN", "NOT IN"] and not isinstance(val, basestring):
		raise Exception("For {0} operation type of value field must be String".format(op))

	if field in ["resolution_date", "opening_date"]:
		if op in ["IN", "NOT IN"]:
			for v in val:
				is_valid_datetime(v, date_format)
		else:
			is_valid_datetime(val, date_format)
	else:
		if op in ["IN", "NOT IN"]:
			for v in val:
				if not isinstance(v, basestring):
					raise Exception("Value field in the filter should contain the list of string elements")
		if op in [">", "<", ">=", "<="]:
			raise Exception("{0} operation can not be used on '{1}' field".format(op, field))

def validate_user_against_session_id(args):
	sid = args.get("sid")
	user = args.get("user")

	if not user:
		raise Exception("user field is missing")
	elif user != frappe.db.get_value("Sessions", {"sid":sid}, "user"):
		raise Exception("Invalid User")

def is_valid_subject(subject):
	if subject == frappe.db.get_value("Subject", subject, "name"):
		return True
	else:
		msg = "{msg} [{desc}]".format(
					msg="Invalid Support Ticket Subject, Subject should be one of the following",
					desc=" or ".join(["'%s'"%subj.get("name") for subj in frappe.db.get_all("Subject", order_by="name")])
				)
		raise Exception(msg)

validate_request_methods = {
	"login": validate_login_request,
	"logout": validate_logout_request,
	"reportIssue": validate_report_issue_request,
	"updateIssue": validate_update_issue_request,
	"deleteIssue": validate_delete_issue_request,
	"getIssueList": validate_get_list_request,
	"getIssueStatus": validate_get_issue_status_request,
	"getIssueHistory": validate_issue_history_request
}