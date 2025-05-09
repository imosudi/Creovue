#!/usr/bin/env python3

import time
from flask import Flask, jsonify, render_template, request
from flask_moment import Moment

app = Flask(__name__)


moment = Moment(app)


import Creovue.routes