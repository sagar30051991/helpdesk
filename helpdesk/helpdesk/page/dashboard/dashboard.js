frappe.provide("helpdesk");

frappe.pages['dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Helpdesk Dashboard',
		single_column: true
	});

	new helpdesk.DashboardGridView(wrapper);
	frappe.breadcrumbs.add("HelpDesk")
}

helpdesk.DashboardGridView = frappe.views.GridReportWithPlot.extend({
	init: function(wrapper) {
		this._super({
			title: __("HelpDesk"),
			page: wrapper,
			parent: $(wrapper).find('.layout-main'),
			page: wrapper.page,
			doctypes: ["Issue"],
		});
		this.make_page(wrapper)
	},
	make_page: function(wrapper){
		var me = this;

		this.page = wrapper.page;

		this.status = this.page.add_field({fieldtype:"Select", fieldname: "status", 
			abel: __("Ticket Status"), options:["Open", "Pending", "Close"],});
		// this.technician = this.page.add_field({fieldtype:"Link", label:"Technician",
		// 	fieldname:"technician", options:"Supplier", input_css: {"z-index": 3}});
		this.technician = this.page.add_field({fieldtype:"Link", label:"Department",
			fieldname:"department", options:"Department"});
		this.range = this.page.add_field({fieldtype:"Select", label: __("Range"), fieldname: "range",
			options:[{label: __("Daily"), value: "Daily"}, {label: __("Weekly"), value: "Weekly"},
				{label: __("Monthly"), value: "Monthly"}, {label: __("Quarterly"), value: "Quarterly"},
				{label: __("Yearly"), value: "Yearly"}]})
	},
	// filters: [
	// 	{fieldtype:"Link", fieldname: "dept", label: __("Department"), options:"Department"},
	// 	{fieldtype:"Date", fieldname: "from_date", label: __("From Date")},
	// 	{fieldtype:"Date", fieldname: "to_date", label: __("To Date")},
		// {fieldtype:"Select", label: __("Range"), fieldname: "range",
		// 	options:[{label: __("Daily"), value: "Daily"}, {label: __("Weekly"), value: "Weekly"},
		// 		{label: __("Monthly"), value: "Monthly"}, {label: __("Quarterly"), value: "Quarterly"},
		// 		{label: __("Yearly"), value: "Yearly"}]}
	// ],
});