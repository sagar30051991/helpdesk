$(document).ready(function() {
    get_subject_and_department_list()
    $('.btn-raise').click(function() {
        // $(".btn-raise").prop("disabled", true);
        if(validate_inputs())
        	raise_support_issue()
     });
});

get_subject_and_department_list = function(){
	return frappe.call({
		method: "helpdesk.py.issue.get_subject_and_department_list",
		freeze: true,
		freeze_message: "Fetching Subject and Department list",
		callback: function(r){
			if(r.message){
				subjects = r.message.subjects;
				departments = r.message.departments;

				subj_opts = ""
				$.each(subjects, function(idx, subj){
					subj_opts += repl("<option>%(subject)s</option>", subj);
				})

				dept_opts = ""
				$.each(departments, function(idx, dept){
					dept_opts += repl("<option>%(department)s</option>", dept);
				})

				$(subj_opts).appendTo($("#subject"));
				$(dept_opts).appendTo($("#department"));

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
			subject: $("#subject").val().trim(),
			department: $("#department").val().trim(),
			description: $("#description").val().trim()
		},
		callback: function(r){
			if(r.message)
				frappe.msgprint("Support Ticket "+ r.message +" is created sucessfully")
			else
				frappe.msgprint("Error while Saving Support Ticket, Please try after some time")
		}
	});
}

validate_inputs = function(){
	missing_fields = []
	raised_by = $("#raised_by").val().trim()
	subject = $("#subject").val().trim()
	department = $("#department").val().trim()
	description = $("#description").val().trim()

	if(!$("#raised_by").val().trim())
		missing_fields.push("Raised By")
	if(!$("#subject").val().trim())
		missing_fields.push("Subject")
	if(!$("#department").val().trim())
		missing_fields.push("Department")
	if(!$("#description").val().trim())
		missing_fields.push("Description")

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