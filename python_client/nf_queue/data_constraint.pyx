class data_constraint:

	# TODO : check how to add 3 types of constraint with data

	SUBJECT_TYPE = 0 # only match the topic  
	INT_TYPE = 1 
	STRING_TYPE = 2 
	INT_RANGE_TYPE = 3 

	def __init__(self, type, field, data):
		self.type = type
		self.field = field
		self.data = data
