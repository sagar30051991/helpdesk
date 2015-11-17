import json
import frappe
from utils import get_attr
from response import get_response

def handle():
	# call the respective method, create support ticket etc ..
		cmd = frappe.local.form_dict.cmd

		if cmd == "login":
			return login(frappe.local.form_dict.args)
		else:
			return execute_cmd(cmd)

def execute_cmd():
	try:
		manage_user()

		method = get_attr(cmd)
		args = frappe.local.form_dict.args
		result = frappe.call(method, args)
		
		if result:
			return get_response(1, "Success")
		else:
			return get_response(0, "Error occured, Please contact administrator")
	except Exception, e:
		raise e

@frappe.whitelist(allow_guest=True)
def login(args):
	args = json.loads(args)
	try: 
		if args.get("email") and args.get("password"):
			frappe.clear_cache(user = args["email"])
			frappe.local.login_manager.authenticate(args["email"],args["password"])
			frappe.local.login_manager.post_login()
			return get_response(
						message="Logged In",
						status_code=1,
						args={
							"sid":frappe.session.sid,
							"user": args.get("email")
						}
					)
		else:
			raise Exception("Invalid Input")
	except frappe.AuthenticationError,e:
		# http_status_code = getattr(e, "http_status_code", 500)
		return get_response("Authentication Error")

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
