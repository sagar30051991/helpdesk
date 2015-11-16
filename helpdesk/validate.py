import frappe
from response import get_response
from utils import get_json_request
from utils import get_attr

def validate_request():
	validate_url()

	args  = get_json_request(frappe.local.form_dict.args)
	method = frappe.local.form_dict.cmd

	validate_request_parameters(method, args)

def validate_url():
	parts = frappe.request.path[1:].split("/")
	call = cmd = None

	if len(parts) > 1:
		call = parts[1]

	if len(parts) > 2:
		cmd = parts[2]

	if call=="method" and len(parts) == 3:
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
	validate_mandatory_fields(method, args)

def validate_mandatory_fields(method, args):
	"""validate request for all the mandetory fields"""
	pass
