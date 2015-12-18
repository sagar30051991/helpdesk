import json
import frappe
from utils import get_attr
from utils import get_json_request
from response import get_response
from helpdesk_api import login, logout

def handle():
	# call the respective method, create support ticket etc ..
		cmd = frappe.local.form_dict.cmd

		if cmd == "login":
			return login(frappe.local.form_dict.args)
		elif cmd == "logout":
			return logout(frappe.local.form_dict.args)
		else:
			return execute_cmd(cmd)

def execute_cmd(cmd):
	try:
		manage_user()
		method = get_attr(cmd)
		
		# check if method is whitelisted
		if frappe.session['user'] == 'Guest' and (method not in frappe.guest_methods):
			return get_response(message="Not Allowed", args={"http_status_code":403})
		elif not method in frappe.whitelisted:
			return get_response(message="Not Allowed", args={"http_status_code":403})
		else:
			args = get_json_request(frappe.local.form_dict.args)
			result = frappe.call(method, args)
			if result:
				if isinstance(result, dict):
					return get_response(message="Success", status_code=1, args=result)
				else:
					return get_response(message="Success", status_code=1)
			else:
				return get_response(message="Error occured, Please contact administrator")
	except Exception, e:
		raise e

# @frappe.whitelist(allow_guest=True)
# def login(args):
# 	args = json.loads(args)
# 	try: 
# 		if args.get("user") and args.get("password"):
# 			frappe.clear_cache(user = args["user"])
# 			frappe.local.login_manager.authenticate(args["user"],args["password"])
# 			frappe.local.login_manager.post_login()
# 			return get_response(
# 						message="Logged In",
# 						status_code=1,
# 						args={
# 							"sid":frappe.session.sid,
# 							"user": args.get("user")
# 						}
# 					)
# 		else:
# 			raise Exception("Invalid Input")
# 	except frappe.AuthenticationError,e:
# 		# http_status_code = getattr(e, "http_status_code", 500)
# 		return get_response(message="Authentication Error, Please check user id and password")

# @frappe.whitelist(allow_guest=True)
# def logout(args):
# 	args = json.loads(args)
# 	try: 
# 		if args.get("user") and args.get("sid"):
# 			manage_user()
# 			frappe.local.login_manager.logout()
# 			frappe.db.commit()
# 			print "hello"
# 			return get_response(
# 						message="Logged Out",
# 						status_code=1,
# 					)
# 		else:
# 			raise Exception("Invalid Input")
# 	except frappe.AuthenticationError,e:
# 		return get_response(message="Logout unsuccessful")

def manage_user():
	args = json.loads(frappe.form_dict.args)
	sid = args.get('sid')

	if not sid:
		raise Exception("sid not provided")

	else:
		try:
			frappe.form_dict["sid"] = sid 
			loginmgr = frappe.auth.LoginManager()
			return True
		except frappe.SessionStopped,e:
			raise Exception(e.message)
