# # Copyright (c) 2013, helpdesk and contributors
# # For license information, please see license.txt

# from __future__ import unicode_literals
# import frappe
# from frappe import msgprint, _

# def execute(filters=None):
# 	columns, data = [], []
# 	columns = get_columns(filters)
# 	entries = get_entries(filters)
# 	# conference = get_conference();
# 	data = []
# 	for d in entries:
# 		data.append([
# 			d.name, d.customer, d.territory, d.posting_date, d.item_code,
# 			item_details.get(d.item_code, {}).get("item_group"), item_details.get(d.item_code, {}).get("brand"),
# 			d.qty, d.base_net_amount, d.sales_person, d.allocated_percentage, d.contribution_amt
# 		])

# 	return columns, data



# def get_entries(filters):
# 	# date_field = filters["doc_type"] == "Sales Order" and "transaction_date" or "posting_date"
# 	conditions, values = get_conditions(filters)
# 	entries = frappe.db.sql("""select status, conference,city,building,location 
#  							from `tabConference Booking`
#  							{0} """.format(get_conditions), as_dict=1,debug=1)

# 	return entries



# def get_conditions(filters, date_field):
# 	conditions = [""]
# 	values = []

# 	if filters.get("conference") :
# 		conditions.append(" conference "= '{0}'
#  							and "from_date" >= {1} and "to_date" <= {2}
#  	print conditions,"hiiiiiiiiiiii"
#  	return conditions						
	


# # def get_conference():
# # 	conference = {}
# # 	as_dict = frappe.db.sql("""select status, conference,city,building,location 
# # 							from `tabConference Booking`""", as_dict=1,debug=1)
# # 	print as_dict,"as_dict"
# # 	for d in frappe.db.sql("""select status, conference,city,building,location 
# # 							from `tabConference Booking`""", as_dict=1,debug=1):
# # 		conference.setdefault(d['conference'], d)
# # 	print conference,"conference"	
# # 	return conference

# def get_columns(filters):
# 	if not filters.get("conference"):
# 		msgprint(_("Please select the conference first"), raise_exception=1)

# 	return [filters["conference"] + ":Link/" + ":140",
# 		_("City") + ":Data:140",
# 		_("Building") + ":Data:140",
# 		_("Status") + ":Data:140",
# 		_("Location") + ":Data:140"]