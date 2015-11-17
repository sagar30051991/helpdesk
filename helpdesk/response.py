
from __future__ import unicode_literals
import json
import datetime
import mimetypes
import os
import frappe
from frappe import _
import frappe.model.document
import frappe.utils
import frappe.sessions
import werkzeug.utils
from werkzeug.local import LocalProxy
from werkzeug.wsgi import wrap_file
from werkzeug.wrappers import Response
from werkzeug.exceptions import NotFound, Forbidden
# from utils import json_to_xml

def get_response(message, status_code=0, args=None):
	# status_code 0 for error, 1 for successful execution
	frappe.response["code"] = status_code
	frappe.response["message"] = message

	if args:
		for key, val in args.iteritems():
			frappe.response[key] = val

	response = build_response("json")
	return response

def build_response(response_type=None):
	if "docs" in frappe.local.response and not frappe.local.response.docs:
		del frappe.local.response["docs"]

	response_type_map = {
		'json': as_json,
		# 'xml':as_xml
	}

	return response_type_map[frappe.response.get('type') or response_type]()

def as_json():
	make_logs()
	response = Response()
	if frappe.local.response.status_code:
		response.status_code = frappe.local.response['status_code']
		del frappe.local.response['status_code']

	response.headers[b"Content-Type"] = b"application/json; charset: utf-8"
	response.data = json.dumps(frappe.local.response, default=json_handler, separators=(',',':'))
	return response

# def as_xml():
# 	make_logs()
# 	response = Response()
# 	if frappe.local.response.status_code:
# 		response.status_code = frappe.local.response['status_code']
# 		del frappe.local.response['status_code']

# 	response.headers[b"Content-Type"] = b"application/xml; charset: utf-8"
# 	response.data = json_to_xml(frappe.local.response, as_str=True)
# 	return response

def make_logs(response = None):
	"""make strings for msgprint and errprint"""
	if not response:
		response = frappe.local.response

	# if frappe.error_log:
	# 	# frappe.response['exc'] = json.dumps("\n".join([cstr(d) for d in frappe.error_log]))
	# 	response['exc'] = json.dumps([frappe.utils.cstr(d) for d in frappe.local.error_log])

	# if frappe.local.message_log:
	# 	response['_server_messages'] = json.dumps([frappe.utils.cstr(d) for
	# 		d in frappe.local.message_log])

	# if frappe.debug_log and frappe.conf.get("logging") or False:
	# 	response['_debug_messages'] = json.dumps(frappe.local.debug_log)

def json_handler(obj):
	"""serialize non-serializable data for json"""
	# serialize date
	if isinstance(obj, (datetime.date, datetime.timedelta, datetime.datetime)):
		return unicode(obj)
	elif isinstance(obj, LocalProxy):
		return unicode(obj)
	elif isinstance(obj, frappe.model.document.BaseDocument):
		doc = obj.as_dict(no_nulls=True)
		return doc
	else:
		raise TypeError, """Object of type %s with value of %s is not JSON serializable""" % \
			(type(obj), repr(obj))


def redirect():
	return werkzeug.utils.redirect(frappe.response.location)


def handle_session_stopped():
	response = Response("""<html>
							<body style="background-color: #EEE;">
									<h3 style="width: 900px; background-color: #FFF; border: 2px solid #AAA; padding: 20px; font-family: Arial; margin: 20px auto">
											Updating.
											We will be back in a few moments...
									</h3>
							</body>
					</html>""")
	response.status_code = 503
	response.content_type = 'text/html'
	return response
