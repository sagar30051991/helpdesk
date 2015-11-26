// Ticket Escalation Settings

frappe.ui.form.on("Ticket Escalation Settings", "is_default", function(frm){
	if(cur_frm.doc.is_default){
		frappe.confirm("Set this settings profile as default ?",
			function(){
				cur_frm.doc.is_default = 1;
				cur_frm.refresh_fields();
			},
			function(){
				cur_frm.doc.is_default = 0;
				cur_frm.refresh_fields();
			}
		)
	}
});

frappe.ui.form.on("Ticket Escalation Settings", "refresh", function(frm){
	if(cur_frm.docname === "Default"){
		cur_frm.toggle_enable("escalation_hierarchy", false);
	}
});