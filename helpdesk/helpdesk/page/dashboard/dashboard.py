import frappe

@frappe.whitelist()
def get_support_ticket_data(args):
	"""
		args:{
			status: All, Closed, Open, Pending,
			start: val
			end: val
		}
		Support Ticket Data in following format
		{
			"lable":"Issue Status"
			"data": [["date","Issue 1"], ...,["date","Issue N"]]
		}
	"""
	import datetime, time
	now = datetime.datetime.now()
	time.mktime(datetime.datetime.now().timetuple()) * 1000
	# return [{
	# 			"label":"Open",
	# 			"data": [["28-09-2015", 3.0], ["28-10-2015", 3.9], ["28-11-2015", 2.0], ["28-12-2015", 1.2], ["28-01-2016", 1.3]]
	# 		},
	# 		{
	# 			"label":"Close",
	# 			"data": [["22-09-2015", 2.0], ["22-10-2015", 2.9], ["22-11-2015", 1.0], ["22-12-2015", 3.2], ["22-01-2016", 5.3]]
	# 		},
	# 		{
	# 			"label":"Pending",
	# 			"data": [["21-09-2015", 3.9], ["22-10-2015", 10], ["22-11-2015", 3.0], ["22-12-2015", 2.2]]
	# 		}]
	return [{
				"label":"Open",
				"data": [[1446010871000, 3.9], [1448689271000, 2.0]]
			},
			{
				"label":"Close",
				"data": [[1445496132000, 2.9], [1448174532000, 1.0]]
			},
			{
				"label":"Pending",
				"data": [[1444462993000, 10], [1447141393000, 3.0]]
			}]