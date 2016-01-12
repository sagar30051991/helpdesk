"""
	Request Schema's and global defaults
	format: 

	"method":{
		"fields":{
			"field_name":{
				"is_mandatory": 0 or 1,
				"length": (10 length of field value),
				"type": type
			}
		}
	}
"""

api_request_schema = {
	"login":{
		"fields": {
			"user":{
				"is_mandatory": 1,
				"length": 35,
				"type": basestring
			},
			"password":{
				"is_mandatory": 1,
				"length": 15,
				"type": basestring
			}
		},
	},
	"logout":{
		"fields": {
			"user":{
				"is_mandatory": 1,
				"length": 35,
				"type": basestring
			},
			"sid":{
				"is_mandatory": 1,
				"length": 60,
				"type": basestring
			}
		},
	},
	"reportIssue":{
		"fields":{
			"subject": {
				"is_mandatory": 1,
				"length": 200,
				"type": basestring
			},
			"description": {
				"is_mandatory": 1,
				"length": 400,
				"type": basestring
			},
			"user": {
				"is_mandatory": 1,
				"length": 35,
				"type": basestring
			},
			"department": {
				"is_mandatory": 1,
				"length": 30,
				"type": basestring
			},
			"category": {
				"is_mandatory": 1,
				"length": 30,
				"type": basestring
			},
			"floor": {
				"is_mandatory": 1,
				"length": 30,
				"type": basestring
			},
			"wing": {
				"is_mandatory": 1,
				"length": 30,
				"type": basestring
			},
			"extension_number": {
				"is_mandatory": 1,
				"length": 30,
				"type": basestring
			},
			"cabin_or_workstation_number": {
				"is_mandatory": 1,
				"length": 30,
				"type": basestring
			},
			"sid": {
				"is_mandatory": 1,
				"length": 60,
				"type": basestring
			}
		}
	},
	"getIssueStatus": {
		"fields": {
			"ticket_id": {
				"is_mandatory": 1,
				"length": 20,
				"type": basestring
			},
			"user": {
				"is_mandatory": 1,
				"length": 35,
				"type": basestring
			},
			"sid": {
				"is_mandatory": 1,
				"length": 60,
				"type": basestring
			}
		}
	},
	"getIssueList": {
		"fields": {
			"user": {
				"is_mandatory": 1,
				"length": 35,
				"type": basestring
			},
			"sid": {
				"is_mandatory": 1,
				"length": 60,
				"type": basestring
			},
			"filter": {
				"type": dict,
				"allowed_field": [
						"resolution_date", "subject", 
						"ticket_id", "department",
						"status", "opening_date"
					],
				"default_field": "raised_by",
				# TODO add like, not like op
				"allowed_operations": ["IN", "NOT IN", "<>", "=", ">", "<", ">=", "<="],
				"default_operation": "="
			},
			"order_by": {
				"type": basestring,
				"options": ["ASC", "DESC"],
				"default": "DESC"
			},
			"sort_by": {
				"type": basestring,
				"length": 20,
				"default": "name",
				"options": ["name", "subject", "opening_date", "modified"]
			},
			"limit": {
				"type": int,
				"default": 20,
				"max_value": 50,
			}
		}
	},
	"updateIssue":{
		"fields":{
			"user": {
				"is_mandatory": 1,
				"length": 35,
				"type": basestring
			},
			"ticket_id": {
				"is_mandatory": 1,
				"length": 20,
				"type": basestring
			},
			"subject": {
				"length": 200,
				"type": basestring
			},
			"description": {
				"length": 400,
				"type": basestring
			},
			"department": {
				"length": 30,
				"type": basestring
			},
			"category": {
				"length": 30,
				"type": basestring
			},
			"floor": {
				"length": 30,
				"type": basestring
			},
			"wing": {
				"length": 30,
				"type": basestring
			},
			"extension_number": {
				"length": 30,
				"type": basestring
			},
			"cabin_or_workstation_number": {
				"length": 30,
				"type": basestring
			},
			"sid": {
				"is_mandatory": 1,
				"length": 60,
				"type": basestring
			}
		}
	},
	"getIssueHistory": {
		"fields": {
			"user": {
				"is_mandatory": 1,
				"length": 35,
				"type": basestring
			},
			"ticket_id": {
				"is_mandatory": 1,
				"length": 20,
				"type": basestring
			},
			"sid": {
				"is_mandatory": 1,
				"length": 60,
				"type": basestring
			}
		}
	},
	# "deleteIssue": {
	# 	"fields": {
	# 		"ticket_id": {
	# 			"is_mandatory": 1,
	# 			"length": 20,
	# 			"type": basestring
	# 		},
	# 		"user": {
	# 			"is_mandatory": 1,
	# 			"length": 35,
	# 			"type": basestring
	# 		},
	# 		"sid": {
	# 			"is_mandatory": 1,
	# 			"length": 60,
	# 			"type": basestring
	# 		}
	# 	}
	# },
}