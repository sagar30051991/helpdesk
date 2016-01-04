import frappe
from datetime import datetime, timedelta
# import datetime
from frappe.utils import get_datetime, time_diff_in_hours

def validate_todo(doc, method):
	if doc.reference_type == "Issue" and doc.status != "Closed":
		validate_issue_status(doc.reference_name, doc.status)
		validate_due_date(doc)
		validate_assigned_by(doc)

def validate_issue_status(issue, todo_status):
	if frappe.db.get_value("Issue", issue, "status") == "Closed":
		frappe.throw("Can not assign Closed ticket to another user")

def validate_due_date(doc):
	# get the time limit for the role from escalation settings
	now = get_datetime().now()
	datetime_str = "{date} {time}".format(date=doc.date, time=doc.due_time)

	datetime_str = datetime.strptime(datetime_str.split(".")[0], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
	now_str = now.strftime("%Y-%m-%d %H:%M:%S")

	# if time_diff_in_hours(datetime_str, now_str) < 0:
	# 	frappe.throw("Can not assign past date")

	creation = datetime.strptime(doc.creation, "%Y-%m-%d %H:%M:%S.%f")

	if creation.replace(microsecond=0) == now.replace(microsecond=0):
		# current user highest role in doc.role
		if doc.assigned_by == frappe.session.user:
			doc.role = get_highest_role(frappe.session.user)
			doc.assigned_to_role = get_highest_role(doc.owner)
		else:
			doc.role = get_highest_role(doc.assigned_by)
			doc.assigned_to_role = get_highest_role(doc.owner)

	query = """	SELECT
				    er.time
				FROM
				    `tabTicket Escalation Settings Record` AS er
				JOIN
				    `tabTicket Escalation Settings` AS tes
				ON
				    er.parent=tes.name
				AND er.role='%s'
				AND tes.is_default=1"""%(doc.role or "Administrator")

	result = frappe.db.sql(query, as_dict=True)
	if not result:
		frappe.throw("Can not find the Role in Escalation Settings")
	else:
		time = result[0].get("time")
		if creation.replace(microsecond=0) == now.replace(microsecond=0):
			set_due_dttm(doc, now, time)
		elif time_diff_in_hours(datetime_str, now_str) < 0:
			set_due_dttm(doc, now, time)
		else:
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
				    rp.role IN (%s)"""%(",".join(["'%s'"%(role) for role in get_roles(doc.assigned_by)]))
	
	assigned_by_priority = frappe.db.sql(query, as_list=True)[0][0]
	owner_role_priority = get_role_priority(get_highest_role(doc.owner))

	if owner_role_priority.get("priority") > assigned_by_priority:
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
		return priority[0]

def get_highest_role(user):
	# return highest role of user
	from frappe.utils.user import get_roles
	usr_roles = [role for role in get_roles(user)]
	
	highest_role = None
	query = "SELECT role, priority FROM `tabRole Priority` ORDER BY priority DESC"
	records = frappe.db.sql(query, as_dict=True)
	for rec in records:
		if rec.get("role") in usr_roles:
			return rec.get("role")

	if not highest_role:
		frappe.throw("You can not assign Ticket to any other user")

def set_due_dttm(doc, now, time):
	due_dttm = now + timedelta(hours=time)
	doc.due_time = due_dttm.strftime("%H:%M:%S")
	doc.date = due_dttm.strftime("%Y-%m-%d ")