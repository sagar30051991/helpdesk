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
	from frappe.utils.user import get_roles
	query = """	SELECT
				    MAX(rp.priority)
				FROM
				    `tabRole Priority` rp
				WHERE
				    rp.role IN (%s)"""%(["'%s'"%(role) for role in get_roles(doc.assigned_by)])
	
	assigned_by_priority = frappe.db.sql(query, as_list=True)[0][0]
	owner_priority = get_role_priority(doc.role)
	if owner_priority > assigned_by_priority:
		frappe.throw("Can not assign the ToDo to higher authority")

def get_role_priority(role=None):
	filters = {
		"parent": "Role Priority Settings"
	}
	if role:
		filters.update({"role": role})

	priority = frappe.db.get_values("Role Priority", filters, ["role", "priority"], as_dict=True)
	if not priority:
		frappe.throw("Can Not find the priority for the selected role")
	elif not role:
		return priority
	else:
		return priority