frappe.pages['dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Helpdesk Dashboard',
		single_column: true
	});

	var options = {
		doctype: "Issue",
		parent: page
	};

	// page.dashboard_view = new frappe.views.DispachOrderGantt(options,page,wrapper);
}