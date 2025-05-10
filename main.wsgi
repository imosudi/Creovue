#!/usr/bin/env python3
import os
import sys
import platform

# Get Python version
py_vers = (".").join(platform.python_version().split(".")[:2])

# Set base directory path
dir_path = os.path.dirname(os.path.realpath(__file__))
base_path = dir_path.rstrip("Creovue") if dir_path.endswith("Creovue") else os.path.dirname(dir_path)

# Add virtual environment site-packages to path
python_path = os.path.join(base_path, f"venv/lib/python{py_vers}/site-packages")
sys.path.insert(0, python_path)

# Add application directory to path
sys.path.insert(0, dir_path)

# Import application
from main import app as application