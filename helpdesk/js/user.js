frappe.ui.form.on("User", {
	onload: function(frm){
		cur_frm.toggle_reqd("department", true);
	},
});