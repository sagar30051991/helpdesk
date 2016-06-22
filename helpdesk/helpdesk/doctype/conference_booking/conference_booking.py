	# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import now_datetime, now, cstr
from frappe import msgprint
from helpdesk.utils import send_mail
import datetime
import time
from helpdesk.utils import email_templates
from frappe.model.document import Document
from frappe.utils import now
from frappe.utils.user import is_website_user

sender_field = "email_id"
class ConferenceBooking(Document):

	def validate(self):
		self.notify_to_user()

	 #fetch from after login details.       
	def notify_to_user(self):

		args = {
			"email_id": self.email_id,
			"conference_booking":{
				"date": self.date,
				"from_time": self.from_time,
				"to_time": self.to_time,
				"conference": self.conference,
				"building": self.building,
				"location": self.location,
				"area": self.area,
				"city": self.city,
				"facility": self.facility,
				"agenda": self.agenda,
				"attendees" :self.attendees
			}
		}
		template = email_templates.get("conference_notification")
		message = frappe.get_template(template).render(args)
		print args.get("email_id"),"argssssssssssssssssssssss"
		print message, "Adsaaaaaaaaaaaaaaaaaa"
		print args
		frappe.sendmail(recipients=args.get("email_id"),subject="subject", message= frappe.get_template(template).render(args))


@frappe.whitelist(allow_guest=True)
def get_conference():
	print frappe.db.get_all("Conference", fields="name as conference"),"get_conference in get"
	return {
		# "departments": frappe.db.get_all("Department", fields="name as department"),
		"conference":frappe.db.get_all("Conference", fields="name as conference")
		# "categories": frappe.db.get_all("Service Type", fields="name as service_type")
	}

@frappe.whitelist(allow_guest=True)
def make_conference_booking(**args):
	import json
	import HTMLParser
	print "in conference_booking"
	print args,"args coming from js"
	print  args,"args"
	args = frappe._dict(args)
	print HTMLParser.HTMLParser().unescape(args.city),"city city city"


	cb_obj = frappe.new_doc("Conference Booking")
	cb_obj.email_id = HTMLParser.HTMLParser().unescape(args.email_id)
	cb_obj.city = HTMLParser.HTMLParser().unescape(args.city)
	cb_obj.building = HTMLParser.HTMLParser().unescape(args.building)
	cb_obj.location = HTMLParser.HTMLParser().unescape(args.location)
	cb_obj.date = HTMLParser.HTMLParser().unescape(args.date)
	cb_obj.from_time = HTMLParser.HTMLParser().unescape(args.from_time)
	cb_obj.to_time = HTMLParser.HTMLParser().unescape(args.to_time)
	cb_obj.attendees = HTMLParser.HTMLParser().unescape(args.attendess_name)
	cb_obj.agenda = HTMLParser.HTMLParser().unescape(args.agenda)
	cb_obj.conference = HTMLParser.HTMLParser().unescape(args.conference)
	cb_obj.area = HTMLParser.HTMLParser().unescape(args.area)
	cb_obj.facility = HTMLParser.HTMLParser().unescape(args.facility)
	cb_obj.save(ignore_permissions=True)
	return cb_obj.name


