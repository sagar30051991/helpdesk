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
		raise Exception("Invalid date value format, Date format should be : {0}".format(date_format))

def autoname_todo(doc, method):
    from frappe.naming import make_autoname
    doc.name = make_autoname('ToDo.#######')

def send_mail(args, subject):
    """send mail to user"""
    from frappe.utils.user import get_user_fullname

    try:
        sender = None
        template = email_templates.get(args.get("action"))

        args.update({
        	"fullname": get_user_fullname(args.get("user")) or "Guest"
        })
        frappe.sendmail(recipients=args.get("email"), sender=sender, subject=subject,
            message=frappe.get_template(template).render(args))

        return True
    except Exception, e:
        import traceback
        print "notify", traceback.format_exc()
        return False
 
def build_table(data, has_header=True, is_horizontal=False):
    """
    build html table
    inupt: data:dict
    format: {
                "head":["SR","HEADER1", "HEADET2"],
                total: 5                            #total number of rows
                1: [1, "col1", "col2"]              # first row
                2: [2, "col1", "col2"]              # second row
            }
    """
    # building table head
    thead = ""
    if has_header and not is_horizontal:
        th = "".join(["<th>%s</th>"%(th) for th in data.get("head")])
        thead = "<thead><tr align='center'>{th}</tr><thead>".format(th=th)

    records = ""
    order = data.get("order")
    for idx in xrange(1, data.get("total") + 1):
        if not is_horizontal:
            td = "".join(["<td align='center' style='padding:3px'>%s</td>"%(td) for td in data.get(idx)])
        else:
            td = "".join(["<td style='padding:3px' align='%s'>%s</td>"%(
                                "right" if i == 0 else "left",
                                "<b>%s<b>"%(td) if i == 0 else td
                            ) for i,td in enumerate(data.get(idx))])
        tr = "<tr>%s</tr>"%(td)
        records += tr

    tbody = "<tbody>%s<tbody>"%(records)
    table = """<table border="1px" style="border-collapse: collapse;" width="100%">{thead}{tbody}</table>
            """.format(thead=thead or "", tbody=tbody)
    
    return table

def create_scheduler_log(err_msg, err_traceback, method):
    se = frappe.new_doc('Scheduler Log')
    se.method = method
    se.error = "%s\n%s"%(err_msg, err_traceback)
    se.save(ignore_permissions=True)

def get_dept_head_user(dept):
    query = """ SELECT
                    ur.parent
                FROM
                    tabUserRole ur
                JOIN
                    tabUser u
                ON
                    ur.parent=u.name
                WHERE
                    ur.role="Department Head"
                AND u.department='{dept}'
            """.format(dept=dept)
    return frappe.db.sql(query, as_list=True)[0][0]

def get_users_email_ids(users):
    query = """ SELECT 
                    email
                FROM
                    tabUser
                WHERE
                    name IN ({users})
            """.format(users=",".join(["'%s'"%(user) for user in users]))
    emails = frappe.db.sql(query, as_list=True)
    if emails:
        return [email[0] for email in emails]

email_templates = {
	"open_tickets": "templates/email/open_ticket_template.html",
	"new_ticket": "templates/email/new_ticket_template.html",
    "escalate_ticket": "templates/email/escalate_ticket_template.html",
    "cant_escalate_tickets": "templates/email/cant_escalate_ticket_template.html",
    "user_issue_notification": "templates/email/user_issue_raised.html"
}