import frappe
from utils import get_attr
from response import report_error

def handle():
	# call the respective method, create support ticket etc ..
	try:
		cmd = frappe.local.form_dict.cmd
		method = get_attr(cmd)
		args = frappe.local.form_dict.args
		result = frappe.call(method, args)
		if result:
			get_response(1, "Success")
		else:
			get_response(0, "Error occured, Please contact administrator")
	except Exception, e:
		return get_response(str(e))