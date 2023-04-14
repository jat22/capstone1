from flask import Flask, redirect, render_template, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests, json
from keys import REC_API_KEY
from func import resource_search, resource_by_id, child_resources_by_parent, key_format_endpoint, find_recareas_by_location, find_campgrounds_by_location

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///playlist-app'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "I'LL NEVER TELL!!"

debug = DebugToolbarExtension(app)

REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
ACTIVITIES = "activities"
CAMPSITES = "campsites"
FACILITIES = "facilities"
PERMIT = "permitentrances"
RECAREAS = "recareas"
TOURS = "tours"

camping_near_gtlbrg = find_campgrounds_by_location("35.7143", "-83.5102")

rec_areas_in_ME = find_recareas_by_location(state="ME")


