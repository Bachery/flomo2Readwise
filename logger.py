import loguru

class loguru_logger():
	def __init__(self, log_name, parameters=None):
		self.logger = loguru.logger
		self.logger.add(log_name + '.log')
		if parameters:
			self.log('TASK INFO:')
			self.log_dict(parameters)
	
	# accept any type or length of parameters
	def log(self, *info):
		self.logger.info(' '.join([str(i) for i in info]))

	def info(self, *info):
		self.log(*info)
	
	def log_dict(self, dict):
		for k, v in dict.items():
			if type(k) != str: k = str(k)
			if type(v) != str: v = str(v)
			self.log(k + ': ' + v)
