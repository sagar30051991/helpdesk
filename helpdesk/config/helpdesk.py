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
			]
		},
    ]
