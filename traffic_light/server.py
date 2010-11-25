from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from email.Utils import formatdate

from traffic_light.job import Job
from traffic_light.event import Event, Text, NextUpdate, LampRed, LampGreen, LampYellow
from traffic_light.mode import ModeOff, ModeBlink

class RequestHandler(BaseHTTPRequestHandler):
    job_list = []
    current_job = -1
    
    def _parse_job(self, job):
        response = ''

        if isinstance(job, Job):
            response += self._parse_job(job.run())
        elif isinstance(job, Event):
            response += str(job)
        elif isinstance(job, list):
            for sub_job in job:
                response += self._parse_job(sub_job)
        else:
            # TODO: Excpetion?
            pass
            
        return response

    def do_GET(self):
        if self.path != '/':
            return

        RequestHandler.current_job += 1
        if RequestHandler.current_job >= len(RequestHandler.job_list):
            RequestHandler.current_job = 0

        try:
            job = RequestHandler.job_list[RequestHandler.current_job]
            response_code = 200
            response_body = self._parse_job(job)
        except Exception as detail:
            response = [
                Text(str(detail)),
                NextUpdate(5000),
                LampRed(ModeBlink(250)),
                LampGreen(ModeOff()),
                LampYellow(ModeOff())
            ]

            response_code = 500
            response_body = self._parse_job(response)
        
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


def run(server_address, job_list):
    RequestHandler.job_list = job_list
    httpd = HTTPServer(server_address, RequestHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
