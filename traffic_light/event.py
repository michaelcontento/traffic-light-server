from traffic_light.mode import Mode

class Event:
    def __str__(self):
        raise NotImplementedError('Subclass must implement this')


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
    color_red    = 'red'
    color_yellow = 'yellow'
    color_green  = 'green'

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

