# import frappe

# def on_validate(doc, method):
# 	"""
# 		validate user their should be only one department head
# 	"""
# 	print "validate in"
# 	query = """ SELECT name FROM `tabUser` WHERE department='%s' AND
# 				name IN (SELECT parent FROM `tabUserRole` WHERE role='Department Head')"""%(doc.department)

# 	record = frappe.db.sql(query)
# 	if record:
# 		frappe.throw("Their can be only one Department Head for %s"%(department))