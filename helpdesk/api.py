import frappe
import handler
from response import get_response
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
		import traceback
		print traceback.format_exc()
		return get_response(message=str(e))