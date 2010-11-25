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
