import sys
import os
sys.path.insert(0, os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]), os.pardir, os.pardir)))

from traffic_light import server
from traffic_light.job import Hudson

server.run(('', 8804), [Hudson('localhost', 80, 'My Project')])
