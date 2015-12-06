# -*- coding: utf-8 -*-
from __future__ import unicode_literals

app_name = "helpdesk"
app_title = "HelpDesk"
app_publisher = "helpdesk"
app_description = "helpdesk"
app_icon = "octicon octicon-briefcase"
app_color = "grey"
app_email = "makarand.b@indictranstech.com"
app_version = "0.0.1"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/helpdesk/css/helpdesk.css"
# app_include_js = "/assets/helpdesk/js/helpdesk.js"

# include js, css files in header of web template
# web_include_css = "/assets/helpdesk/css/helpdesk.css"
# web_include_js = "/assets/helpdesk/js/helpdesk.js"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "helpdesk.install.before_install"
# after_install = "helpdesk.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "helpdesk.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
	"Issue": "helpdesk.py.issue.get_permission_query_conditions",
}
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Issue": {
		"on_update": "helpdesk.helpdesk.doctype.ticket_escalation_history.ticket_escalation_history.issue_on_update",
		"on_trash": "helpdesk.helpdesk.doctype.ticket_escalation_history.ticket_escalation_history.issue_on_trash"
	},
	"ToDo": {
		"validate": "helpdesk.py.todo.validate_todo",
		"on_update": "helpdesk.helpdesk.doctype.ticket_escalation_history.ticket_escalation_history.todo_on_update",
		"on_trash": "helpdesk.helpdesk.doctype.ticket_escalation_history.ticket_escalation_history.todo_on_trash",
		"autoname": "helpdesk.utils.autoname_todo"
	},
	"User": {
		"validate": "helpdesk.py.user.validate_user"
	}
}

# Scheduled Tasks
# ---------------

scheduler_events = {
	"all": [
		"helpdesk.tasks.sync_db"
	],
	"hourly": [
		"helpdesk.tasks.ticket_escallation"
	],
	# "daily": [
	# 	"helpdesk.tasks.daily"
	# ],
	# "weekly": [
	# 	"helpdesk.tasks.weekly"
	# ]
	# "monthly": [
	# 	"helpdesk.tasks.monthly"
	# ]
}

fixtures = ["Property Setter", "Custom Field"]

# Testing
# -------

# before_tests = "helpdesk.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "helpdesk.event.get_events"
# }
