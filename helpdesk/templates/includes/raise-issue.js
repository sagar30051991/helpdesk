


get_subject_and_department_list = function(){
	return frappe.call({
		method: "helpdesk.py.issue.get_subject_and_department_list",
		freeze: true,
		freeze_message: "Fetching Subject and Department list",
		callback: function(r){
			if(r.message){
				service_type = r.message.service_type;
				facility = r.message.facility;

				subj_opts = "<option></option>"
				$.each(service_type, function(idx, subj){
					subj_opts += repl("<option>%(service_type)s</option>", subj);
				})

			/*	catg_opts = "<option></option>"
				$.each(r.message.location, function(idx, subj){
					catg_opts += repl("<option>%(location)s</option>", subj);
				})

				dept_opts = "<option></option>"
				$.each(departments, function(idx, dept){
					dept_opts += repl("<option value=\"%(facility)s\">%(facility)s</option>", dept);
				})
*/
				$(subj_opts).appendTo($("#service_type"));
			/*	$(dept_opts).appendTo($("#facility"));
				$(catg_opts).appendTo($("#location"));*/

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
			service_type: $("#service_type").val(),
			facility: $("#facility").val(),
			description: $("#description").val().trim(),
			location: $("#location").val().trim(),
			floor: $("#floor").val().trim(),
			area: $("#area").val().trim(),
			building: $("#building").val().trim(),
			city: $("#city").val().trim(),
			location_description: $("#loc_desc").val().trim()
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
	fields_id = [	{id:"#raised_by", label:"Email"}, {id:"#service_type", label:"Service Type"}, 
					{id:"#facility", label:"Facility"}, {id:"#location", label:"Location"},
					{id:"#building", label:"Building"}, {id:"#area", label:"Area"},
					{id:"#city", label:"City"}, {id:"#floor", label:"Floor"},
					{id:"#loc_desc", label:"Location Description"},{id:"#description", label:"Description"}
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
			"#raised_by", "#service_type", "#facility", 
			"#description", "#area","#building",
			 "#location", "#loc_desc","#floor","#city"
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
		/*callback: function(r){
			if(r.message){
				$("#extension_number").val(r.message.city || "")
				$("#floor").val(r.message.building || "")
				$("#department").val(r.message.area || "")
				$("#wing").val(r.message.facility || "")
				$("#cabin_or_workstation_number").val(r.message.description  || "")
				set_greetings(r.message.user_fullname)
			}
			else
				clear_fields(["#extension_number", "#floor", "#department", "#cabin_or_workstation_number", "#wing"])
		}*/
	});
}

set_greetings = function(user){
	msg = "";
	date = new Date();
	hours = date.getHours();
	min = date.getMinutes();

	if(hours < 12)
		msg = user? "Good Morning " + user : "Good Morning !!"
	else if(hours > 12 || (hours == 12 && min > 0))
		msg = user? "Good Afternoon " + user : "Good Afternoon !!"
	else if(hours > 16)
		msg = user? "Good Evening" + user : "Good Evening !!"

	$("#greet").html(msg)
}

frappe.ready(function() {
    get_subject_and_department_list()
	//get_conference()
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

    /*set_greetings()*/
});