get_subject_and_department_list = function(){
	return frappe.call({
		method: "helpdesk.py.issue.get_subject_and_department_list",
		freeze: true,
		freeze_message: "Fetching Subject and Department list",
		callback: function(r){
			if(r.message){
				subjects = r.message.subjects;
				departments = r.message.departments;

				subj_opts = "<option></option>"
				$.each(subjects, function(idx, subj){
					subj_opts += repl("<option>%(subject)s</option>", subj);
				})

				catg_opts = "<option></option>"
				$.each(r.message.categories, function(idx, subj){
					catg_opts += repl("<option>%(category)s</option>", subj);
				})

				dept_opts = "<option></option>"
				$.each(departments, function(idx, dept){
					dept_opts += repl("<option value=\"%(department)s\">%(department)s</option>", dept);
				})

				$(subj_opts).appendTo($("#subject"));
				$(dept_opts).appendTo($("#department"));
				$(catg_opts).appendTo($("#category"));

			}
			else
				frappe.msgprint("Error while fetching Subject and Department, Please try after some time")
		}
	});
}

raise_support_issue = function(){
	return frappe.call({
		method: "helpdesk.py.issue.raise_issue",
		freeze: true,
		freeze_message: "Creating New Support Ticket",
		args: {
			raised_by: $("#raised_by").val().trim(),
			subject: $("#subject").val(),
			department: $("#department").val(),
			description: $("#description").val().trim(),
			category: $("#category").val().trim(),
			floor: $("#floor").val().trim(),
			wing: $("#wing").val().trim(),
			extension_number: $("#extension_number").val().trim(),
			cabin_or_workstation_number: $("#cabin_or_workstation_number").val().trim()
		},
		callback: function(r){
			if(r.message)
				frappe.msgprint("Support Ticket "+ r.message +" is created sucessfully")
			else
				frappe.msgprint("Error while Saving Support Ticket, Please try after some time")

			$(".btn-raise").prop("disabled", false);
			clear_fields();
		}
	});
}

validate_inputs = function(){
	missing_fields = []
	fields_id = [	{id:"#raised_by", label:"Email"}, {id:"#subject", label:"Subject"}, 
					{id:"#department", label:"Department"}, {id:"#department", label:"Department"},
					{id:"#extension_number", label:"Extension Number"}, {id:"#floor", label:"Floor"},
					{id:"#wing", label:"Wing"}, {id:"#cabin_or_workstation_number", label:"Cabin Or Workstation Number"},
					{id:"#category", label:"Category"},{id:"#description", label:"Description"}
				]
	$.each(fields_id, function(i, field){
		if(!$(field.id).val().trim())
			missing_fields.push(field.label)
	})

	if(!missing_fields.length){
		if(!valid_email($("#raised_by").val().trim())){
			frappe.msgprint("<center>Valid email required</center>", "Validation Error")
			return false
		}
		else
			return true
	}
	else{
		frappe.msgprint("<center>Mandatory fields required in Issue<br>" + 
			missing_fields.join("<br>") +"</center>", "Validation Error")
		return false
	}

}

clear_fields = function(fields){
	fields_id = [
			"#raised_by", "#subject", "#department", 
			"#description", "#extension_number", "#floor",
			"#wing", "#cabin_or_workstation_number", "#category",
			"#department"
		]
	
	if(fields)
		fields_id = fields
	
	$.each(fields_id, function(i, id){
		$(id).val("")
	})
}

fetch_and_render_user_details = function(){
	return frappe.call({
		method: "helpdesk.py.user.get_user_details",
		freeze: true,
		freeze_message: "Creating New Support Ticket",
		args: { user: $("#raised_by").val().trim() },
		callback: function(r){
			if(r.message){
				$("#extension_number").val(r.message.extension_number || "")
				$("#floor").val(r.message.floor || "")
				$("#department").val(r.message.department || "")
				$("#wing").val(r.message.wing || "")
				$("#cabin_or_workstation_number").val(r.message.cabin_or_workstation_number  || "")
			}
			else
				clear_fields(["#extension_number", "#floor", "#department", "#cabin_or_workstation_number", "#wing"])
		}
	});
}

frappe.ready(function() {
    get_subject_and_department_list()
	
    // Binding events to fields

    $('.btn-raise').click(function() {
        if(validate_inputs()){
        	$(".btn-raise").prop("disabled", true);
        	raise_support_issue()
        }
     });

    $('.btn-clear').click(function() {
    	clear_fields()
    });

    $('#raised_by').change(function(){
    	fetch_and_render_user_details()
    })
});