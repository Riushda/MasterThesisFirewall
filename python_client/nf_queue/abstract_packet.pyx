class abstract_packet:

	def __init__(self, src, dst, sport, dport, subject, content):
		self.src = src
		self.dst = dst
		self.sport = sport
		self.dport = dport
		self.subject = subject
		self.content = content