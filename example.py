from traffic_light import server
from traffic_light.job import CIJoe, Clear
from traffic_light.event import Text, NextUpdate

if __name__ == '__main__':
    server.run(
        ('', 8804), 
        [
            CIJoe('localhost', 4567, 'Local CIJoe'), 
            [Clear(), Text('Hallo Welt'), NextUpdate(5000)]
        ]
    )  
