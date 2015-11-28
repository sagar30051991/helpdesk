frappe.ui.form.on("Role Priority Settings", "onload", function(frm){
	help = "Set High Priority Role First";
	help += "<br>e.g.<br>Department Head<br>Support Manager";
	help += "<br>Support Lead<br>Support User<br>etc";
	cur_frm.doc.help = help;
})