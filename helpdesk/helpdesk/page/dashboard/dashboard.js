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
		this.bind_filters()
		
		var me = this;

		this.wrapper = $('<div class="grid-report"></div>').appendTo(this.page.main);
		this.page.main.find(".page").css({"padding-top": "0px"});
		this.plot_area = $('<div class="plot"></div>').appendTo(this.wrapper);
		
		this.summary = $('<div id="summary"></div>').appendTo(this.page.main);
		
		this.wrapper.css({
			"border-style":"solid",
			"border-width": "2px",
			"border-radius": "10px"
		})
		this.summary.css({
			"border-style":"none solid solid",
			"border-width": "2px",
			"border-radius": "10px"
		})

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
						dept: this.page.fields_dict.department.get_parsed_value(),
						user: frappe.user.name
				}
			},
			callback: function(r){
				if(r.message.plot_data){
					me.data = r.message.plot_data;
					me.waiting.toggle(false);
					me.render_plot();
				}
				else{
					me.plot_area.toggle(false);
					me.waiting.html("Support Ticket Records Not found");
					me.waiting.toggle(true);
				}

				delete r.message["plot_data"]
				me.render_summery_info(r.message);
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
	bind_filters:function(){
		var me = this
		this.start.$input.change(function(){
			me.validate_fields_and_refresh();
		});
		this.end.$input.change(function(){
			me.validate_fields_and_refresh();
		});
		this.status.$input.change(function(){
			me.validate_fields_and_refresh();
		});
		this.department.$input.change(function(){
			me.validate_fields_and_refresh();
		});
	},
	make_waiting: function() {
		this.waiting = frappe.messages.waiting(this.wrapper, __("Loading Report")+"...");
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

		this.setup_plot_hover();
	},
	render_summery_info: function(info){
		html = '<div class="row"><div class="col-md-6"><div class="row"><div class="col-md-12" align="center"><h3>\
		Helpdesk Support Ticket Summary</h3></div></div><br><div class="row"><div class="col-md-7" align="right">\
		<b>Total Number Of Tickets</b></div><div class="col-md-5"><span class="open-notification">'+
		info.total_tickets +'</span></div></div><div class="row"><div class="col-md-7" align="right"><b>Open Tickets</b>\
		</div><div class="col-md-5"><span class="open-notification">'+info.open_tickets +'</span></div></div>\
		<div class="row"><div class="col-md-7" align="right"><b>Pending Tickets</b></div><div class="col-md-5">\
		<span class="open-notification">'+ info.pending_tickets +'</span></div></div><div class="row">\
		<div class="col-md-7" align="right"><b>Closed Tickets</b></div><div class="col-md-5"><span class="open-notification">'+ 
		info.closed_tickets +'</span></div></div></div><div class="col-md-6"><div class="row"><div class="col-md-12" \
		align="center"><h3>Links</h3></div></div><div class="row" id="links" align="center"></div></div></div><br>'


		links_info = [
			{
				"title": "ToDo",
				"icon": "octicon octicon-list-unordered",
				"bgcolor": "#4aa3df",
				"link":"#List/ToDo"
			},
			{
				"title": "Support Ticket",
				"icon": "octicon octicon-issue-opened",
				"bgcolor": "#4aa3df",
				"link": "#List/Issue"
			},
			{
				"title": "Desk",
				"icon": "octicon octicon-briefcase",
				"bgcolor": "#4aa3df",
				"link": "#Module/HelpDesk"
			}
		]

		$("#summary").html(html)
		this.render_links_icon(links_info)
	},
	render_links_icon:function(links_info){
		$.each(links_info, function(i, m) {
			html = '<div style="display:inline-block;margin-left: 10px;margin-right: 10px;">\
			<a href="%(link)s"><div class="app-icon" style="background-color: %(bgcolor)s" \
			title="%(title)s" align="center"><i class="%(icon)s" title="%(title)s"></i></div>\
			</a><div class="case-label text-ellipsis"><span class="case-label-text" style="color:\
			 black;text-shadow: none;">%(title)s</span></div></div>'

			$(repl(html, m)).appendTo($("#links"));
		});
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
				// 'background-color': '#fee',
				'background-color': '#ffffd2',
				opacity: 0.80
			}).appendTo("body").fadeIn(200);
		}

		this.previousPoint = null;
		this.wrapper.find('.plot').bind("plothover", function (event, pos, item) {
			if (item) {
				if (me.previousPoint != item.dataIndex) {
					me.previousPoint = item.dataIndex;

					$("#" + me.tooltip_id).remove();
					idx = item.dataIndex
					names = item.series.data[idx][2]
					showTooltip(item.pageX, item.pageY,
						me.get_tooltip_text(item.series.label, item.datapoint[0], item.datapoint[1], names));
				}
			}
			else {
				$("#" + me.tooltip_id).remove();
				me.previousPoint = null;
			}
	    });

	},
	get_tooltip_text: function(label, x, y, names) {
		var date = dateutil.obj_to_user(new Date(x));
	 	var value = format_number(y, null, 0);
	 	html =  "<table border=1 style='border-collapse: collapse;'><tr>"
	 	html += "<td colspan='2' align='center'><b>"+ label +" Tickets</b></td></tr>"
	 	html += "<tr><td><b>Date</b></td><td style='padding: 5px;'>"+ date 
	 	html += "</td></tr><tr><td><b>No. Of Tickets</b></td>"
	 	html += "<td style='padding: 5px;' align='right'>"+ value 
	 	html += "</td></tr><tr><td><b>Ticket ID's</b></td>"
	 	html += "<td style='padding: 5px;'>" + names + "</td></tr></table>"
		return html
	},
	get_plot_options: function() {
		return {
			grid: { hoverable: true, clickable: true },
			xaxis: { mode: "time",
				min: dateutil.str_to_obj(this.page.fields_dict.start.get_parsed_value()).getTime(),
				max: dateutil.str_to_obj(this.page.fields_dict.end.get_parsed_value()).getTime() 
			},
			yaxis: { autoscaleMargin: 1 },
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
	},
	validate_fields_and_refresh: function(me){
		this.check_mandatory_fields();

		start = new Date(this.page.fields_dict.start.get_parsed_value());
		end = new Date(this.page.fields_dict.end.get_parsed_value());
		dept = this.page.fields_dict.department.get_parsed_value();
		status = this.page.fields_dict.status.get_parsed_value();

		if(end < start){
			frappe.throw("To Date must be greater than From Date");
		}
		this.refresh();
	}
});