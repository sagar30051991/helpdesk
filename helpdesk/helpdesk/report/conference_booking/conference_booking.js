// Copyright (c) 2013, helpdesk and contributors
// For license information, please see license.txt

frappe.query_reports["Conference Booking"] = {
	"filters": [
	{
			fieldname: "conference",
			label: __("Conference"),
			fieldtype: "Link",
			options: "Conference"
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: get_today(),
		},
		{
			fieldname:"to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: get_today()
		},
		
	]
}
