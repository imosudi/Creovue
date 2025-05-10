# main.wsgi
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, "/home/mosud/dev/creovue/Creovue")

from main import app as application
