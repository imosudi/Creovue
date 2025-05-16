#!/usr/bin/python3

import os
import sys

#dir_path = os.path.dirname(os.path.realpath(__file__))

dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(0, dir_path)

#from app import app as application
from Creovue import app as application