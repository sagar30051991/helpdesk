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
	# frappe.errprint(args)
	return [{
				"label":"Open",
				"data": [[1999, 3.0], [2000, 3.9], [2001, 2.0], [2002, 1.2], [2003, 1.3]]
			},
			{
				"label":"Close",
				"data": [[1999, 2.0], [2000, 2.9], [2001, 1.0], [2002, 3.2], [2003, 5.3]]
			},
			{
				"label":"Pending",
				"data": [[1999, 3.9], [2000, 10], [2001, 3.0], [2002, 2.2], [2003, 1.9]]
			}]
	pass