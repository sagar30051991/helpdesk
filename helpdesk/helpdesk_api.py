import frappe

@frappe.whitelist()
def reportIssue(args):
	result = False
	try:
		result = True
	except Exception, e:
		raise Exception("Not Yet Implemented")
	finally:
		return result

@frappe.whitelist()
def getIssueStatus(args):
	try:
		result = True
	except Exception, e:
		raise Exception("Not Yet Implemented")
	finally:
		return result

@frappe.whitelist()
def getList(args):
	try:
		result = True
	except Exception, e:
		raise Exception("Not Yet Implemented")
	finally:
		return result

@frappe.whitelist()
def updateIssue(args):
	try:
		result = True
	except Exception, e:
		raise Exception("Not Yet Implemented")
	finally:
		return result

@frappe.whitelist()
def deleteIssue(args):
	try:
		result = True
	except Exception, e:
		raise Exception("Not Yet Implemented")
	finally:
		return result

@frappe.whitelist()
def getIssueHistory(args):
	try:
		result = True
	except Exception, e:
		raise Exception("Not Yet Implemented")
	finally:
		return result