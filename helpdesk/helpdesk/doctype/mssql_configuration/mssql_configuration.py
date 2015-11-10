# -*- coding: utf-8 -*-
# Copyright (c) 2015, helpdesk and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

class MSSQLConfiguration(Document):
	pass

def get_mssql_config():
    config = frappe.get_doc("MSSQL Configuration", "MSSQL Configuration")
    return {
        "server": config.server,
        "port": config.port,
        "user": config.user,
        "password": config.password,
        "database": config.database
    }
