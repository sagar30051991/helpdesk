import json
import frappe
from time import strptime

def get_json_request(args):
	try:
		if not args:
			raise Exception("Request Parameters Not Found")

		return json.loads(args)
	except Exception, e:
		raise Exception("Invalid JSON request")

def get_attr(cmd):
	"""get method object from cmd"""
	if '.' in cmd:
		method = frappe.get_attr(cmd)
	else:
		method = globals()[cmd]
	return method

def is_valid_datetime(val, date_format):
	try:
		strptime(val, date_format)
	except Exception, e:
		raise Exception("Invalid date value format")