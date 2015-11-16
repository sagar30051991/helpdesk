import frappe
import handler
from response import report_error
from validate import validate_request

def handle():
	"""
	Handler for `/helpdesk` methods

	### Examples:

	`/helpdesk/method/{methodname}` will call a whitelisted method
	"""
	try:
		validate_request()
		return handler.handle()
	except Exception, e:
		return get_response(0, str(e))