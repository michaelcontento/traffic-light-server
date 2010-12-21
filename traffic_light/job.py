from httplib import HTTPConnection
from urllib import quote
from random import seed, randint

from traffic_light.event import NextUpdate, Text, LampRed, LampYellow, LampGreen
from traffic_light.mode import ModeOn, ModeOff, ModeBlink

class Job:
    def __init__(self):
        self.state = {
            'red': LampRed(ModeOff()),
            'yellow': LampYellow(ModeOff()),
            'green': LampGreen(ModeOff()),
            'ttl': NextUpdate(3000)
        }

    def run(self):
        return [v for (k, v) in self.state.items()]

class RandomLights(Job):
    def _randomMode(self):
        if randint(0, 1) == 0:
            return ModeOn()
        else:
            return ModeOff()
        
    def run(self):
        return [
            LampRed(self._randomMode()),
            LampYellow(self._randomMode()),
            LampGreen(self._randomMode())                
        ]

class Clear(Job):
    def run(self):
        return [
            LampRed(ModeOff()),
            LampYellow(ModeOff()),
            LampGreen(ModeOff()),
            Text(''),
        ]

class CIJoe(Job):
    def __init__(self, host, port, name=''):
        Job.__init__(self)
        self.host = host
        self.port = port
        self.name = name

    def run(self):
        try:
            conn = HTTPConnection(self.host, self.port)
            conn.request('GET', '/ping')
            response = conn.getresponse()           
        except Exception as exception:
            self.state['red'] = LampRed(ModeBlink(250))
            self.state['text'] = Text(self.name + "\n" + str(exception))
            return Job.run(self)

        self.state['text'] = Text(self.name)
        if response.status == 412:
            if response.read() == 'building':
                self.state['yellow'] =  LampYellow(ModeOn())
            else:
                self.state['red'] = LampRed(ModeOn())
        else:
               self.state['green'] = LampGreen(ModeOn())

        return Job.run(self)

class Hudson(Job):
    def __init__(self, host, port, job):
        Job.__init__(self)
        self.host = host
        self.port = port
        self.job  = job

    def run(self):
        try:
            conn = HTTPConnection(self.host, self.port)
            conn.request('GET', '/job/' + quote(self.job) + '/api/xml?xpath=.//color')
            response = conn.getresponse()           
        except Exception as exception:
            self.state['red'] = LampRed(ModeBlink(250))
            self.state['text'] = Text(self.job + "\n" + str(exception))
            return Job.run(self)

        self.state['text'] = Text(self.job)
        if response.status != 200:
            self.state['reg'] = LampRed(ModeOn())
        else:
            color = response.read()[7:-8]
            if color == 'blue':
                self.state['green'] = LampGreen(ModeOn())
            elif color == 'red':
                self.state['red'] = LampRed(ModeOn())
            else:
                self.state['yellow'] = LampYellow(ModeOn())

        return Job.run(self)
