from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from email.Utils import formatdate

class Event:
	pass

class NextUpdate(Event):
	def __init__(self, interval):
		self.interval = interval

	def __str__(self):
		return 'ttl ' + str(self.interval) + '\n'

class Text(Event):
	def __init__(self, message):
		self.message = message

	def __str__(self):
		return 'text ' + str(len(self.message)) + ' ' + self.message + '\n'

class Lamp(Event):
	color_red = 'red'
	color_yellow = 'yellow'
	color_green = 'green'

	def __init__(self, color, mode):
		self.color = color
		self.mode  = mode

		if not isinstance(mode, Mode):
			raise ValueError('mode must be derived from Mode class')

	def __str__(self):
		return 'lamp ' + str(self.color) + ' ' + self.mode.__str__() + '\n'

class LampGreen(Lamp):
	def __init__(self, mode):
		Lamp.__init__(self, Lamp.color_green, mode)

class LampYellow(Lamp):
	def __init__(self, mode):
		Lamp.__init__(self, Lamp.color_yellow, mode)

class LampRed(Lamp):
	def __init__(self, mode):
		Lamp.__init__(self, Lamp.color_red, mode)
class Mode:
	def __str__(self):
		raise NotImplementedError('Subclass must implement this')

class ModeOn(Mode):
	def __str__(self):
		return 'on'

class ModeOff(Mode):
	def __str__(self):
		return 'off'

class ModeBlink(Mode):
	def __init__(self, interval):
		self.interval = interval

	def __str__(self):
		return 'blink ' + str(self.interval)

class RequestHandler(BaseHTTPRequestHandler):
	job_list = []
	current_job = -1
	
	def do_GET(self):
		if self.path != '/':
			return

		try:
			RequestHandler.current_job += 1
			if RequestHandler.current_job >= len(RequestHandler.job_list):
				RequestHandler.current_job = 0

			job = RequestHandler.job_list[RequestHandler.current_job]
			
			response_code = 200
			response_body = ''

			if isinstance(job, Job):
				for event in job.run():
					response_body += str(event)
			elif isinstance(job, list):
				for elem in job:
					if isinstance(elem, Job):
						for event in elem.run():
							response_body += str(event)
					elif isinstance(elem, Event):
						response_body += str(elem)
					else:
						print 'STRANGE 2'
			elif isinstance(job, Event):
				response_body += str(elem)
			else:
				print 'STRANGE'
		except Exception as detail:
			response = [
				Text(str(detail)),
				NextUpdate(5000),
				LampRed(ModeBlink(250)),
				LampGreen(ModeOff()),
				LampYellow(ModeOff())
			]

			response_code = 500
			response_body = ''
			for event in response:
				response_body += str(event) 
		
		# Set response code and some basic headers
		self.send_response(response_code)
		self.send_header('Content-Type', 'text/plain')
		self.send_header('Content-Length', len(response_body))

		# Avoid caching 
		self.send_header('Cache-Control', 'no-cache')
		self.send_header('Expires', '-1')
		self.send_header('pragma', 'no-cache')

		# Send header and body
		self.end_headers()
		self.wfile.write(response_body)

class Job:
	def run(self):
		raise NotImplementedError('Subclass must implement this')

class Delay(Job):
	def __init__(self, interval):
		self.interval = interval

	def run(self):
		return [NextUpdate(self.interval)]


from httplib import HTTPConnection
class CIJoe(Job):
	def __init__(self, host, port):
		self.host = host
		self.port = port

	def run(self):
		lampRed = LampGreen(ModeOff())
		lampYellow = LampGreen(ModeOff())
		lampGreen = LampGreen(ModeOff())

		conn = HTTPConnection(self.host, self.port)
		conn.request('GET', '/ping')
		response = conn.getresponse()		

		if response.status == 412:
			if response.read() == 'building':
				lampYellow = LampYellow(ModeOn())
			else:
				lampRed = LampRed(ModeOn())
		else:
			lampGreen = LampGreen(ModeOn())

		return [lampRed, lampYellow, lampGreen]

if __name__ == '__main__':
	RequestHandler.job_list = [
		Delay(100), 
		[
			CIJoe('localhost', 4567), 
			Text('Traffic Light Server'), 
			NextUpdate(100)
		],
		Delay(200), 
		Delay(300)
	] 

	httpd = HTTPServer(('', 8804), RequestHandler)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()
