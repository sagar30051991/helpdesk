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
	args = json.loads(args)
	query = build_query(args)
	frappe.errprint(query)
	
	resultSet = frappe.db.sql(query, as_dict=True)
	if not resultSet:
		return None
	day_wise_record = get_day_wise_records(resultSet)
	return get_data_in_flot_format(args.get("start"), args.get("end"), args.get("status"), day_wise_record)
	
def build_query(filters):
	def build_conditions(filters):
		condition = ""
		status = ""
		date_type = "opening_date"

		# status
		if filters.get("status") != "All":
			if filters.get("status") == ("Pending"):
				status = "AND status NOT IN ('Open', 'Closed')"
			else:
				status = "AND status='%s'"%(filters.get("status"))
			date_type = "resolution_date" if filters.get("status") == "Closed" else "opening_date"
		# order by
		order_by = "ORDER BY {field} ASC".format(field=date_type)
		# date conditions
		condition = "WHERE {field} BETWEEN '{start}' AND '{end}' {status} {order_by}".format(
				field=date_type,
				start=filters.get("start"),
				end=filters.get("end"),
				status=status,
				order_by=order_by
			)

		return condition

	return """SELECT name, opening_date, opening_time, resolution_date, status FROM `tabIssue` {conditions}""".format(conditions=build_conditions(filters))
	
def datetime_to_time(dt):
	import datetime, time
	return time.mktime(dt.timetuple()) * 1000

def get_flot_formatted_data(opened, closed, pending):
	data = []
	if opened:
		data.append({
			"label":"Open",
			"data": opened
		})
	if closed:
		data.append({
			"label":"Closed",
			"data": closed
		})
	if pending:
		data.append({
			"label":"Pending",
			"data": pending
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

	for i in xrange(0, days):
		date = str(add_days(start, i))
		record = records.get(date)
		
		datetime_str = datetime_to_time(get_datetime("{0} 00:00:00".format(date)))

		if not record:
			opened.append([datetime_str, 0])
			closed.append([datetime_str, 0])
			pending.append([datetime_str, 0])
		else:
			open_tickets = record.get("Open")
			if not open_tickets:
				opened.append([datetime_str, 0])
			else:
				count = len(open_tickets)
				# names = ",".join([r.get("name") for r in open_tickets])
				opened.append([datetime_str, count])

			closed_tickets = record.get("Closed")
			if not closed_tickets:
				closed.append([[datetime_str, 0]])
			else:
				count = len(closed_tickets)
				# names = ",".join([r.get("name") for r in closed_tickets])
				closed.append([datetime_str, count])

			pending_ticket = record.get("Pending")
			if not pending_ticket:
				pending.append([datetime_str, 0])
			else:
				count = len(pending_ticket)
				# names = ",".join([r.get("name") for r in pending_ticket])
				pending.append([datetime_str, count])

	if status == "All":
		return get_flot_formatted_data(opened, closed, pending)
	elif status == "Open":
		return get_flot_formatted_data(opened, None, None)
	elif status == "Closed":
		return get_flot_formatted_data(None, closed, None)
	else:
		return get_flot_formatted_data(None, None, pending)