#!/usr/bin/python3

import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
print("dir_path: ", dir_path) 
sys.path.insert(0, dir_path)

sys.path.insert(0, '/home/mosud/dev/Creovue')


#from app import app as application
from Creovue import app as application