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

	        
	def notify_to_user(self):
		args = { "email_id": self.email_id,"conference_booking":{} }
		
		template = email_templates.get("conference_notification")
		# message = frappe.get_template(template).render(args)
		# print args.get("email_id"),"argssssssssssssssssssssss"
		# print message, "Adsaaaaaaaaaaaaaaaaaa"
		
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
def conference_booking(**args):
	import json
	import HTMLParser
	print "in conference_booking"
	print args,"args coming from js"
	print  args,"args"
	args = frappe._dict(args)
	print HTMLParser.HTMLParser().unescape(args.city),"city city city"


	conference_booking = frappe.new_doc("Conference Booking")
	conference_booking.email_id = HTMLParser.HTMLParser().unescape(args.email_id)
	conference_booking.city = HTMLParser.HTMLParser().unescape(args.city)
	conference_booking.building = HTMLParser.HTMLParser().unescape(args.building)
	conference_booking.location = HTMLParser.HTMLParser().unescape(args.location)
	conference_booking.date = HTMLParser.HTMLParser().unescape(args.date)
	conference_booking.from_time = HTMLParser.HTMLParser().unescape(args.from_time)
	conference_booking.to_time = HTMLParser.HTMLParser().unescape(args.to_time)
	conference_booking.attendees = HTMLParser.HTMLParser().unescape(args.attendess)
	conference_booking.agenda = HTMLParser.HTMLParser().unescape(args.agenda)
	conference_booking.conference = HTMLParser.HTMLParser().unescape(args.conference)
	conference_booking.area = HTMLParser.HTMLParser().unescape(args.area)
	conference_booking.facility = HTMLParser.HTMLParser().unescape(args.facility)
	conference_booking.save(ignore_permissions=True)
	return conference_booking.name


