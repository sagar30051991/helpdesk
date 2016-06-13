from __future__ import unicode_literals
from frappe import _

def get_data():
	return [
		{
			"label": _("Documents"),
			"icon": "icon-star",
			"items": [
				{
					"type": "doctype",
					"name": "Issue",
					"description": _("Support queries from employees."),
				},
				{
					"type": "doctype",
					"name": "Conference Booking",
					"description": _("Conference Booking")
				},
				{
					"type": "doctype",
					"name": "ToDo",
					"description": _("ToDo"),
				},
				{
					"type": "doctype",
					"name": "Subject",
					"description": _("List Of Subjects")
				},
				{
					"type": "doctype",
					"name": "Category",
					"description": _("List Of Categories")
				},
				{
					"type": "doctype",
					"name": "Priority",
					"description": _("Support Ticket Priority."),
				},
				{
					"type": "doctype",
					"name": "Ticket Escalation History",
					"description": _("Support Ticket Escalation History.")
				},
            ]
        },
        {
			"label": _("Setup"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "doctype",
					"name": "MSSQL Configuration",
					"description": _("Setup MS-SQL database server for support users.")
				},
				{
					"type": "doctype",
					"name": "Role Priority Settings",
					"description": _("Setup Role Priority.")
				},
				{
					"type": "doctype",
					"name": "Ticket Escalation Settings",
					"description": _("Support Ticket Escalation Settings.")
				}
			]
		},
		{
			"label": _("Page"),
			"icon": "icon-cog",
			"items": [
				{
					"type": "page",
					"name": "dashboard",
					"icon": "icon-sitemap",
					"label": _("Helpdesk Dashboard"),
					"description": _("Dashboard for Helpdesk"),
				},
			]
		},
    ]
