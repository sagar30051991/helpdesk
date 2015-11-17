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
			"email":{
				"is_mandatory": 1,
				"length": 35,
				"type": "string"
			},
			"password":{
				"is_mandatory": 1,
				"length": 15,
				"type": "string"
			}
		},
	}
}