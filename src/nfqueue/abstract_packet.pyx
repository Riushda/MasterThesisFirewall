class AbstractPacket:

	def __init__(self, mark, src, dst, sport, dport, subject, content):
		self.mark = mark
		self.src = src
		self.dst = dst
		self.sport = sport
		self.dport = dport
		self.subject = subject
		self.content = content # array of tuple (field, value) or (value)

	def __str__(self) -> str:
		return "packet : mark:"+str(self.mark)+" src:"+self.src+" dst:"+self.dst \
					+" sport:"+str(self.sport)+" dport:"+str(self.dport)+"\n	 field:"+self.subject+" data:"+str(self.content)