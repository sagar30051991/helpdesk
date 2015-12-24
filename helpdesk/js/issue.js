frappe.ui.form.on("Issue", {
	onload: function(frm) {
		if(inList(user_roles, "Administrator")){
			cur_frm.toggle_reqd("department", true)
		}
		else{
			this.frm.toggle_enable("department", false)
		}
	},
});