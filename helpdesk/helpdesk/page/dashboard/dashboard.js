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
		
		var me = this;

		this.wrapper = $('<div class="grid-report"></div>').appendTo(this.page.main);
		this.page.main.find(".page").css({"padding-top": "0px"});
		
		this.plot_area = $('<div class="plot"></div>').appendTo(this.wrapper);

		this.make_waiting();
		this.refresh();
	},
	refresh: function(){
		this.check_mandatory_fields()
		var me = this;
		this.waiting.toggle(true);
		return frappe.call({
			method: "helpdesk.helpdesk.page.dashboard.dashboard.get_support_ticket_data",
			type: "GET",
			args: {
				args:{
						start: this.page.fields_dict.start.get_parsed_value(),
						end: this.page.fields_dict.end.get_parsed_value(),
						status: this.page.fields_dict.status.get_parsed_value(),
						user: frappe.user.name
				}
			},
			callback: function(r){
				if(r.message){
					// me.data = me.get_plot_data ? me.get_plot_data(r.message) : null;
					me.data = r.message;
					me.waiting.toggle(false);
					me.render_plot();
				}
				else{
					me.plot_area.toggle(false);
					me.waiting.html("Support Ticket Records Not found");
					me.waiting.toggle(true);
				}
			}
		});
	},
	make_filters: function(wrapper){
		var me = this;
		this.page = wrapper.page;

		this.page.set_primary_action(__("Refresh"),
			function() { me.refresh(); }, "icon-refresh")

		this.start = this.page.add_field({fieldtype:"Date", label:"From Date", fieldname:"start", reqd:1,
			default:dateutil.add_days(dateutil.get_today(), -30)});
		this.end = this.page.add_field({fieldtype:"Date", label:"To Date", fieldname:"end", reqd:1,
			default:dateutil.get_today()});
		this.status = this.page.add_field({fieldtype:"Select", fieldname: "status", 
			label: __("Ticket Status"), options:["All", "Open", "Pending", "Closed"], default:"All"});
		this.department = this.page.add_field({fieldtype:"Link", label:"Department",
			fieldname:"department", options:"Department"});
	},
	make_waiting: function() {
		this.waiting = frappe.messages.waiting(this.wrapper, __("Loading Report")+"...");
	},
	get_plot_data: function(plot_data){
		// parse data in flot data format
		var data = []
		$.each(plot_data, function(i, d) {
			records = d["data"]
			new_records = []
			$.map(records, function(val, idx){

			});
		});
	},
	render_plot: function() {
		var plot_data = this.data
		if(!plot_data) {
			this.plot_area.toggle(false);
			return;
		}
		frappe.require('assets/frappe/js/lib/flot/jquery.flot.js');
		frappe.require('assets/frappe/js/lib/flot/jquery.flot.downsample.js');

		this.plot = $.plot(this.plot_area.toggle(true), plot_data, this.get_plot_options());

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
	get_plot_options: function() {
		return {
			grid: { hoverable: true, clickable: true },
			xaxis: { mode: "time",
				min: dateutil.str_to_obj(this.page.fields_dict.start.get_parsed_value()).getTime(),
				max: dateutil.str_to_obj(this.page.fields_dict.end.get_parsed_value()).getTime() 
			},
			series: { downsample: { threshold: 1000 } }
		}
	},
	check_mandatory_fields: function(){
		start = this.page.fields_dict.start.get_parsed_value()
		end = this.page.fields_dict.end.get_parsed_value()

		if(!(start && end)){
			frappe.throw("From Date and To Date are mandatory");
		}
		else if(!start){
			frappe.throw("From Date is mandatory");
		}
		else if(!end){
			frappe.throw("To Date is mandatory");
		}
	}
});