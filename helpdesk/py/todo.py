import frappe
from datetime import datetime, timedelta
import datetime
from frappe.utils import get_datetime, time_diff_in_hours

def validate_todo(doc, method):
	if doc.reference_type == "Issue":
		validate_due_date(doc)
		validate_assigned_by(doc)

def validate_due_date(doc):
	# get the time limit for the role from escalation settings
	now = get_datetime().now()
	datetime_str = "{date} {time}".format(date=doc.date, time=doc.due_time)
	
	if time_diff_in_hours(datetime_str, str(now)) < 0:
		frappe.throw("Can not assign past date")

	query = """	SELECT
				    er.time
				FROM
				    `tabTicket Escalation Settings Record` AS er
				INNER JOIN
				    `tabTicket Escalation Settings` AS tes
				ON
				    er.parent=tes.name
				AND er.role='%s'
				AND tes.is_default=1"""%(doc.role)

	result = frappe.db.sql(query, as_dict=True)
	if not result:
		frappe.throw("Can not find the Role in Escalation Settings")
	else:
		time = result[0].get("time")

		datetime_str = "{date} {time}".format(date=doc.date, time=doc.due_time)
		time_diff = time_diff_in_hours(datetime_str, str(now))
		
		if time < time_diff:
			dttm = (now + timedelta(hours=time)).strftime("%d-%m-%Y %H:%M:%S")
			frappe.throw("Invalid Due Date and Time, Due Date & time shoud be : %s"%(dttm))

def validate_assigned_by(doc):
	"""Do not allow low authority user to assign ticket to higher authority"""