import frappe
from response import get_response
from utils import get_json_request
from utils import get_attr
from conf import api_request_schema as schema

def validate_request():
	validate_url()

	args  = get_json_request(frappe.local.form_dict.args)
	method = frappe.local.form_dict.cmd

	validate_request_parameters(method, args)
	if method != "login": validate_user_against_session_id(args)

def validate_url():
	parts = frappe.request.path[1:].split("/")
	call = cmd = None

	if len(parts) > 1:
		call = parts[1]

	if len(parts) > 2:
		cmd = parts[2]

	if call == "login" and len(parts) == 2:
		frappe.local.form_dict.cmd = "login"

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
	"""validate request fields for all the mandetory, length and type"""
	fields_dict = schema.get(method)
	if not fields_dict:
		raise Exception("Field schema is missing, Please contact Administrator")
	else:
		# validate_mandatory_fields(fields_dict, args)
		validate_fields_length(fields_dict, args)
		validate_fields_type(fields_dict, args)

def validate_user_against_session_id(args):
	sid = args.get("sid")
	user = args.get("user")

	if not user:
		raise Exception("user field is missing")
	elif user != frappe.db.get_value("Sessions", {"sid":sid}, "user"):
		raise Exception("Invalid User")

def validate_login_request(args):
	# raise Exception("not yet implemented")
	pass

def validate_report_issue_request(args):
	raise Exception("not yet implemented")

def validate_get_issue_status_request(args):
	raise Exception("not yet implemented")

def validate_get_list_request(args):
	raise Exception("not yet implemented")

def validate_update_issue_request(args):
	raise Exception("not yet implemented")

def validate_delete_issue_request(args):
	raise Exception("not yet implemented")

def validate_issue_history_request(args):
	raise Exception("not yet implemented")

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
	all_felds = fields_dict.get("fields")
	if not all_felds:
		raise Exception("Field schema is missing, Please contact Administrator")
	else:
		invalid_fields = []
		len_exceeded = []
		for field, prop in all_felds.iteritems():
			if len(args.get(field)) > prop.get("length"):
				len_exceeded.append("'%s'"%(field))
			# elif type(args.get(field)) != type(str):
			# 	invalid_fields.append(field)

		if len_exceeded:
			raise Exception(
					"Request parameters length exceeded for following field(s) : {0}".format(",".join(len_exceeded))
					)

def validate_fields_type(fields_dict, args):
	all_felds = fields_dict.get("fields")
	if not all_felds:
		raise Exception("Field schema is missing, Please contact Administrator")
	else:
		invalid_fields = []

validate_request_methods = {
	"login": validate_login_request,
	"reportIssue": validate_report_issue_request,
	"getIssueStatus": validate_get_issue_status_request,
	"getList": validate_get_list_request,
	"updateIssue": validate_update_issue_request,
	"deleteIssue": validate_delete_issue_request,
	"getIssueHistory": validate_issue_history_request
}