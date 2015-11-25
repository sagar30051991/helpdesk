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

def send_mail(args, subject):
    """send mail to user"""
    from frappe.utils.user import get_user_fullname

    try:
        sender = None
        template = email_templates.get(args.get("action"))

        args.update({
        	"fullname": get_user_fullname(args.get("user"))
        })

        frappe.sendmail(recipients=args.get("email"), sender=sender, subject=subject,
            message=frappe.get_template(template).render(args))

        return True
    except Exception, e:
        import traceback
        print "notify", traceback.format_exc()
        return False
 
email_templates = {
	"open_tickets": "templates/email/open_ticket_template.html"
}
