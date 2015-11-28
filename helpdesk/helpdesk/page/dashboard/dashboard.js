frappe.provide("helpdesk");

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

	setTimeout(function(){
		new helpdesk.DashboardGridView(options, wrapper, page);	
	}, 1)
	frappe.breadcrumbs.add("HelpDesk")
}

helpdesk.DashboardGridView = Class.extend({
	init: function(opts, wrapper, page) {
		$.extend(this, opts);
		this.make_filters(wrapper)
		
		// this.filter_inputs = {};
		// this.preset_checks = [];
		var me = this;

		this.wrapper = $('<div class="grid-report"></div>').appendTo(this.page.main);
		this.page.main.find(".page").css({"padding-top": "0px"});
		
		this.plot_area = $('<div class="plot"></div>').appendTo(this.wrapper);

		this.make_waiting();
		// this.refresh();
		this.refresh();
	},
	refresh: function(){
		var me = this;
		this.waiting.toggle(true);
		return frappe.call({
			method: "helpdesk.helpdesk.page.dashboard.dashboard.get_support_ticket_data",
			type: "GET",
			args: {
				args:{
						start: this.page.fields_dict.start.get_parsed_value(),
						end: this.page.fields_dict.end.get_parsed_value(),
						status: this.page.fields_dict.status.get_parsed_value()
				}
			},
			callback: function(r){
				if(r.message){
					me.data = r.message
					me.waiting.toggle(false);
					me.render_plot();
				}
			}
		});
	},
	make_filters: function(wrapper){
		var me = this;

		this.page = wrapper.page;

		this.page.set_primary_action(__("Refresh"),
			function() { me.refresh(); }, "icon-refresh")

		this.status = this.page.add_field({fieldtype:"Select", fieldname: "status", 
			label: __("Ticket Status"), options:["All", "Open", "Pending", "Close"], default:"All"});
		this.range = this.page.add_field({fieldtype:"Select", label: __("Range"), fieldname: "range",
			options:[{label: __("Daily"), value: "Daily"}, {label: __("Weekly"), value: "Weekly"},
				{label: __("Monthly"), value: "Monthly"}, {label: __("Quarterly"), value: "Quarterly"},
				{label: __("Yearly"), value: "Yearly"}], default: "Weekly"});
		this.start = this.page.add_field({fieldtype:"Date", label:"Start Date", fieldname:"start"});
		this.end = this.page.add_field({fieldtype:"Date", label:"End Date", fieldname:"end"});
		this.department = this.page.add_field({fieldtype:"Link", label:"Department",
			fieldname:"department", options:"Department"});
	},
	make_waiting: function() {
		this.waiting = frappe.messages.waiting(this.wrapper, __("Loading Report")+"...");
	},
	// get_data_and_refresh: function(){

	// },
	render_plot: function() {
		// var plot_data = this.get_support_ticket_data ? this.get_support_ticket_data() : null;
		// var plot_data = this.get_plot_data ? this.get_plot_data() : null;
		var plot_data = this.data
		if(!plot_data) {
			this.plot_area.toggle(false);
			return;
		}
		console.log(this.data)
		frappe.require('assets/frappe/js/lib/flot/jquery.flot.js');
		frappe.require('assets/frappe/js/lib/flot/jquery.flot.downsample.js');

		// this.plot = $.plot(this.plot_area.toggle(true), plot_data,
		// 	this.get_plot_options());
		this.plot = $.plot(this.plot_area.toggle(true), plot_data)

		// this.setup_plot_hover();
	},
	setup_plot_check: function() {
		var me = this;
		me.wrapper.bind('make', function() {
			me.wrapper.on("click", ".plot-check", function() {
				var checked = $(this).prop("checked");
				var id = $(this).attr("data-id");
				if(me.item_by_name) {
					if(me.item_by_name[id]) {
						me.item_by_name[id].checked = checked ? true : false;
					}
				} else {
					$.each(me.data, function(i, d) {
						if(d.id==id) d.checked = checked;
					});
				}
				me.render_plot();
			});
		});
	},
	setup_plot_hover: function() {
		var me = this;
		this.tooltip_id = frappe.dom.set_unique_id();
		function showTooltip(x, y, contents) {
			$('<div id="' + me.tooltip_id + '">' + contents + '</div>').css( {
				position: 'absolute',
				display: 'none',
				top: y + 5,
				left: x + 5,
				border: '1px solid #fdd',
				padding: '2px',
				'background-color': '#fee',
				opacity: 0.80
			}).appendTo("body").fadeIn(200);
		}

		this.previousPoint = null;
		this.wrapper.find('.plot').bind("plothover", function (event, pos, item) {
			if (item) {
				if (me.previousPoint != item.dataIndex) {
					me.previousPoint = item.dataIndex;

					$("#" + me.tooltip_id).remove();
					showTooltip(item.pageX, item.pageY,
						me.get_tooltip_text(item.series.label, item.datapoint[0], item.datapoint[1]));
				}
			}
			else {
				$("#" + me.tooltip_id).remove();
				me.previousPoint = null;
			}
	    });

	},
	get_tooltip_text: function(label, x, y) {
		var date = dateutil.obj_to_user(new Date(x));
	 	var value = format_number(y);
		return value + " on " + date;
	},
	get_plot_data: function() {
		// var data = [];
		// var me = this;
		// $.each(this.data, function(i, item) {
		// 	if (item.checked) {
		// 		data.push({
		// 			label: item.name,
		// 			data: $.map(me.columns, function(col, idx) {
		// 				if(col.formatter==me.currency_formatter && !col.hidden && col.plot!==false) {
		// 					return me.get_plot_points(item, col, idx)
		// 				}
		// 			}),
		// 			points: {show: true},
		// 			lines: {show: true, fill: true},
		// 		});

		// 		// prepend opening
		// 		data[data.length-1].data = [[dateutil.str_to_obj(me.from_date).getTime(),
		// 			item.opening]].concat(data[data.length-1].data);
		// 	}
		// });

		// return data.length ? data : false;
	},
	get_plot_options: function() {
		return {
			grid: { hoverable: true, clickable: true },
			xaxis: { mode: "time",
				min: dateutil.str_to_obj(this.from_date).getTime(),
				max: dateutil.str_to_obj(this.to_date).getTime() 
			},
			series: { downsample: { threshold: 1000 } }
		}
	}
});