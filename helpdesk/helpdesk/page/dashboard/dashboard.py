import frappe
import json
from frappe.utils import date_diff, add_days, get_datetime, getdate

@frappe.whitelist()
def get_support_ticket_data(args):
	"""
		args:{
			status: All, Closed, Open, Pending,
			start: val
			end: val,
			user: uname
		}
		Support Ticket Data in following format
		{
			"lable":"Issue Status"
			"data": [["date","count"], ...,["date","count"]]
		}

		dummy data = [{
					"label":"Open",
					"data": [[1446010871000, 3.9], [1448689271000, 0], [1448789271000, 2.0]]
				},
				{
					"label":"Close",
					"data": [[1445496132000, 2.9], [1448174532000, 1.0]]
				},
				{
					"label":"Pending",
					"data": [[1444462993000, 10], [1447141393000, 3.0]]
				}]

	"""
	# TODO check permissions
	# only fetch the issue whose issue->owner or todo->[owner or assigned by] is user
	args = json.loads(args)
	query = build_query(args)
	
	resultSet = frappe.db.sql(query, as_dict=True)
	if not resultSet:
		return {
			"total_tickets": 0,
			"open_tickets": 0,
			"closed_tickets": 0,
			"pending_tickets": 0,
			"plot_data": None
		}
	day_wise_record = get_day_wise_records(resultSet)
	return get_data_in_flot_format(args.get("start"), args.get("end"), args.get("status"), day_wise_record)
	
def build_query(filters):
	def build_conditions(filters):
		condition = ""
		status = ""
		department = ""
		date_type = "i.opening_date"

		# status
		if filters.get("status") != "All":
			if filters.get("status") == ("Pending"):
				status = "AND i.status NOT IN ('Open', 'Closed')"
			else:
				status = "AND i.status='%s'"%(filters.get("status"))
			date_type = "i.resolution_date" if filters.get("status") == "Closed" else "i.opening_date"

		# order by
		order_by = "ORDER BY {field} ASC".format(field=date_type)
		# department
		if filters.get("dept"):
			department = "AND i.department='%s'"%(filters.get("dept"))

		# TODO system manager, Administrator, Department Head ticket filters
		names = ""
		if "System Manager" in frappe.get_roles(filters.get("user")):
			names = ""
		elif "Department Head" in frappe.get_roles(filters.get("user")):
			names = "AND i.department='{dept}' AND i.name IN (SELECT t.reference_name FROM tabToDo AS t WHERE \
				(t.owner='{user}' AND t.status='Open') OR t.assigned_by='{user}' AND t.reference_type='Issue' \
				AND t.reference_name=i.name) OR i.owner='{user}'".format(
					user=filters.get("user"),
					dept=frappe.db.get_value("User", filters.get("user"), "department")
				)
		else:
			names = "AND i.name IN (SELECT t.reference_name FROM tabToDo AS t WHERE (t.owner='{user}' AND t.status='Open') \
				OR t.assigned_by='{user}' AND t.reference_type='Issue' AND t.reference_name=i.name) OR i.owner='{user}'".format(
					user=filters.get("user")
				)
		
		condition = "WHERE {field} BETWEEN '{start}' AND '{end}' {names} {dept} {status} {order_by}".format(
				field=date_type,
				start=filters.get("start"),
				end=filters.get("end"),
				dept=department,
				status=status,
				order_by=order_by,
				names=names
			)

		return condition

	return """	SELECT DISTINCT
					i.name, i.status,
					i.opening_time, i.resolution_date,
					i.opening_date
				FROM
					`tabIssue` AS i
					{conditions}""".format(conditions=build_conditions(filters))

def datetime_to_time(dt):
	import datetime, time
	return time.mktime(dt.timetuple()) * 1000

def get_flot_formatted_data(opened, closed, pending):
	data = []
	if opened:
		data.append({
			"label":"Open",
			"data": opened,
			"points": {"show": True},
			"lines": {"show": True, "fill": True},
		})
	if closed:
		data.append({
			"label":"Closed",
			"data": closed,
			"points": {"show": True},
			"lines": {"show": True, "fill": True},
		})
	if pending:
		data.append({
			"label":"Pending",
			"data": pending,
			"points": {"show": True},
			"lines": {"show": True, "fill": True},
		})

	return data

def get_day_wise_records(resultSet):
	day_wise_record = {}

	for r in resultSet:
		label = "Pending" if r.get("status") not in ("Open", "Closed") else r.get("status")
		date = get_datetime(r.get("resolution_date")).date() if r.get("status") == "Closed" else getdate(r.get("opening_date"))
		date = str(date)
		record = day_wise_record.get(date)
		if not record:
			day_wise_record.update({
				date:{
					label:[r]
				}
			})
		else:
			lebel_wise_record = record.get(label)
			if not lebel_wise_record:
				record.update({
					label:[r]
				})
			else:
				lebel_wise_record.append(r)
				record.update({
					label: lebel_wise_record
				})
	return day_wise_record

def get_data_in_flot_format(start, end, status, records):
	days = date_diff(end, start) + 1
	data = []
	
	opened = []
	closed = []
	pending = []

	c_open = 0
	c_closed = 0
	c_pending = 0

	for i in xrange(0, days):
		date = str(add_days(start, i))
		record = records.get(date)
		
		datetime_str = datetime_to_time(get_datetime("{0} 00:00:00".format(date)))

		if not record:
			opened.append([datetime_str, 0, "NA"])
			closed.append([datetime_str, 0, "NA"])
			pending.append([datetime_str, 0, "NA"])
		else:
			open_tickets = record.get("Open")
			if not open_tickets:
				opened.append([datetime_str, 0, "NA"])
			else:
				count = len(open_tickets)
				c_open += count
				names = get_names_as_html_string([r.get("name") for r in open_tickets])
				opened.append([datetime_str, count, names])

			closed_tickets = record.get("Closed")
			if not closed_tickets:
				closed.append([[datetime_str, 0, "NA"]])
			else:
				count = len(closed_tickets)
				c_closed += count
				names = get_names_as_html_string([r.get("name") for r in closed_tickets])
				closed.append([datetime_str, count, names])

			pending_ticket = record.get("Pending")
			if not pending_ticket:
				pending.append([datetime_str, 0, "NA"])
			else:
				count = len(pending_ticket)
				c_pending += count
				names = get_names_as_html_string([r.get("name") for r in pending_ticket])
				pending.append([datetime_str, count, names])

	plot_data = None
	if status == "All":
		plot_data = get_flot_formatted_data(opened, closed, pending)
	elif status == "Open":
		plot_data = get_flot_formatted_data(opened, None, None)
	elif status == "Closed":
		plot_data = get_flot_formatted_data(None, closed, None)
	else:
		plot_data = get_flot_formatted_data(None, None, pending)

	data = {
		"total_tickets": c_open + c_closed + c_pending,
		"open_tickets": c_open,
		"closed_tickets": c_closed,
		"pending_tickets": c_pending,
		"plot_data": plot_data
	}

	return data

def get_names_as_html_string(names):
	if len(names) > 2:
		total = len(names) - 2
		names = names[:2]
		names.append("and {0} more".format(total))
	return "<br>".join([r for r in names])

# def get_allowed_issue_names_query(user):
# 	query = """SELECT name FROM tabIssue"""

@frappe.whitelist()
def get_user_department(user):
	return frappe.db.get_value("User",user, "department")