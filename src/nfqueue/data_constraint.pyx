from lib import abstract_packet
from threading import Lock

class Types : 
	SUBJECT_TYPE = 0 # only match the topic, data should be None 
	INT_TYPE = 1 
	STRING_TYPE = 2 
	INT_RANGE_TYPE = 3 

class DataConstraint:

	def __init__(self, index, type, field, data):
		self.index = index
		self.type = type # indicate the type of values in data (or 0 to indicate to only match subject)
		self.field = field
		self.data = data # array of values, value : int | string | [int, int]	

	def __str__(self) -> str:
		type_str = "unknown"
		if self.type==Types.SUBJECT_TYPE:
			type_str = "SUBJECT_TYPE"
		if self.type==Types.INT_TYPE:
			type_str = "INT_TYPE"
		elif self.type==Types.STRING_TYPE:
			type_str = "STRING_TYPE"
		elif self.type==Types.INT_RANGE_TYPE:
			type_str = "INT_RANGE_TYPE"

		return "index:"+str(self.index)+" type:"+type_str+" field:"+self.field+" data:"+str(self.data)


class ConstraintList:
	def __init__(self):
		self.size = 0
		self.constraints_list = []
		self.mutex = Lock()

	def show(self):
		self.mutex.acquire()

		for constraint in self.constraints_list:
			print(constraint)
			
		self.mutex.release()

	def add_constraint(self, index, type, field, data):
		self.mutex.acquire()

		constraint = DataConstraint(index, type, field, data)
		self.constraints_list.append(constraint)
		self.size += 1

		self.mutex.release()
	
	def del_constraint(self, index):
		self.mutex.acquire()

		removed_index = -1
		for i in range(self.size):
			constraint : DataConstraint = self.constraints_list[i]

			if constraint.index==index:
				del self.constraints_list[i]
				self.size -= 1
				removed_index = i
				break
		
		self.mutex.release()

		return removed_index

	def match_data(self, type, data_constraint : DataConstraint, packet):
		
		for data in packet.content:
			field = None
			value = None
			if len(data)>1 : # (field : value) pattern
				field = data[0]
				value = data[1]
			else : # (value) pattern then considered as (subject, value)
				field = packet.subject
				value = data[0]

			if field==data_constraint.field :

				match = False

				for constraint in data_constraint.data :
					if type==Types.INT_TYPE:
						if constraint==int(value) :
							match = True
					elif type==Types.STRING_TYPE:
						if constraint==value :
							match = True
					elif type==Types.INT_RANGE_TYPE:
						if type(value)!=list or len(value)!=2 : # if value not an array or not an array of 2 elements
							match = False
						elif constraint[0]<=int(value) and int(value)<=constraint[1]:
							match = True
					else :
						pass # should never reach there
								
					if match : 
						break
							
				if not match:
					return False

		return True

	# check that the packet correctly matches all constraints associated with its mark
	def match_packet(self, packet):
		self.mutex.acquire()

		for i in range(self.size):
			constraint : DataConstraint = self.constraints_list[i]

			if packet.mark == constraint.index :

				if constraint.type==Types.SUBJECT_TYPE:
					if packet.subject != constraint.field :
						self.mutex.release()
						return False
					break
				else :
					match = self.match_data(constraint.type, constraint, packet)
					if not match:
						self.mutex.release()
						return False
		
		self.mutex.release()
		
		return True