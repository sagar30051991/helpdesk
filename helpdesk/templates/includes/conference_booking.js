//console.log("in conference")

get_conference = function(){
	return frappe.call({
		method: "helpdesk.helpdesk.doctype.conference_booking.conference_booking.get_conference",
		freeze: true,
		freeze_message: "Fetching Subject and Department list",
		callback: function(r){
			if(r.message){
				console.log(r.message)
				conference = r.message.conference;

				conf_opts = "<option></option>"
				$.each(conference, function(idx, conf){
					conf_opts += repl("<option>%(conference)s</option>", conf);
				})

			
				$(conf_opts).appendTo($("#conference"));
			
			}
			else
				frappe.msgprint("Error while fetching Subject and Department, Please try after some time")
		}
	});
}


conference_booking = function(){
	console.log("conference_booking")
	console.log($("#email_id").val(),"email_id")
	console.log($("#conference").val(),"conference")
	return frappe.call({
		method: "helpdesk.helpdesk.doctype.conference_booking.conference_booking.make_conference_booking",
		freeze: true,
		freeze_message: "Creating New conference",
		args: {
			email_id: $("#email_id").val(),
			conference: $("#conference").val(),
			building: $("#building").val(),
			location: $("#location").val(),
			area: $("#area").val(),
			city: $("#city").val(),
			facility: $("#facility").val(),
			date: $("#date").val(),
			from_time: $("#from_time").val(),
			to_time: $("#to_time").val(),
			attendess_name: $("#attendees").val(),
			agenda: $("#agenda").val()
		},
		callback: function(r){
			if(r.message)
				frappe.msgprint("Conference  "+ r.message +" is Book sucessfully")
			else
				frappe.msgprint("Error while Saving conference Ticket, Please try after some time")

			/*$(".btn-conference").prop("disabled", false);*/
			clear_fields();
		}
	});
}

validate_inputs = function(){
	missing_fields = []
	fields_id = [	{id:"#email_id", label:"Email"}, {id:"#conference", label:"Conference"}, 
					{id:"#building", label:"Building"}, {id:"#location", label:"Location"},
					{id:"#area", label:"Area"}, {id:"#city", label:"City"},
					{id:"#facility", label:"Facility"}, {id:"#date", label:"Date"},
					{id:"#from_time", label:"From Time"},{id:"#to_time", label:"To Time"},
					{id:"#attendees", label:"attendees"},{id:"#agenda", label:"Agenda"}
				]
	$.each(fields_id, function(i, field){
		//console.log($(field.id).val(),"valid_email valid_email")
		if(!$(field.id).val())
			missing_fields.push(field.label)
	})

	if(!missing_fields.length){
		if(!valid_email($("#email_id").val())){
			frappe.msgprint("<center>Valid email required</center>", "Validation Error")
			return false
		}
		else
			return true
	}
	else{
		frappe.msgprint("<center>Mandatory fields required in conference booking<br>" + 
			missing_fields.join("<br>") +"</center>", "Validation Error")
		return false
	}

}

clear_fields = function(fields){ 
	//console.log(fields,"fields")
	fields_id = [
			"#email_id","#city","#building", 
			"#location","#from_time","#to_time","#date",
			"#attendees","#agenda","#conference","#area","#facility"
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
		args: { user: $("#email_id").val().trim() },
	});
}

frappe.ready(function() {
    get_conference()
	
    // Binding events to fields
    //console.log($('.btn-'))
    $('.btn-conference').click(function() {
        if(validate_inputs()){
        	$(".btn-conference").prop("disabled", true);
        	conference_booking()
        }
     });

   $('.btn-clear').click(function() {
    	clear_fields()
    });

    $('#email_id').change(function(){
    	fetch_and_render_user_details()
    })

    /*set_greetings()*/
});