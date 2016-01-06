import frappe

def boot_session(bootinfo):
	department = None
	if frappe.session['user'] != "Guest":
		department = frappe.db.get_value("User",frappe.session['user'], "department")
	bootinfo.department = department or ""