frappe.ui.form.on("ToDo", {
	reference_type: function(frm){
		check_and_toggle_reqd();
	},
	refresh: function(frm){
		check_and_toggle_reqd();
	},
	onload: function(frm){
		check_and_toggle_reqd();
	},
});

function check_and_toggle_reqd(){
	if(cur_frm.doc.reference_type == "Issue"){
			set_fields_to_mandatory(true);
	}
	else{
			set_fields_to_mandatory(false);
	}
}

function set_fields_to_mandatory(is_mandatory){
	cur_frm.toggle_reqd("role", is_mandatory);
	cur_frm.toggle_reqd("assigned_to_role", is_mandatory);
	cur_frm.toggle_reqd("assigned_by", is_mandatory);
	cur_frm.toggle_reqd("reference_name", is_mandatory);
	cur_frm.toggle_reqd("date", is_mandatory);
	cur_frm.toggle_reqd("due_time", is_mandatory);
}