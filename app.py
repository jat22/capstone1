from flask import Flask, redirect, render_template, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests, json
from keys import REC_API_KEY
from func import find_recareas_by_location, find_campgrounds_by_location, find_activities_by_location, find_facilities_by_location, find_activities_by_recarea, find_facilities_by_recarea, find_activities_by_facility, resource_search, get_all_activities

from models import db, connect_db, RecArea, Facility, RecAreaFacility, Link, FacilityActivity, Activity, TripActivity, Trip, CampgroundStays, User, CheckList, CheckListItem

app = Flask(__name__)
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///rec_trips'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = "secrets"

debug = DebugToolbarExtension(app)

connect_db(app)

db.create_all()

REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
ACTIVITIES = "activities"
CAMPSITES = "campsites"
FACILITIES = "facilities"
PERMIT = "permitentrances"
RECAREAS = "recareas"
TOURS = "tours"
    


# camping_near_gtlbrg = find_campgrounds_by_location("35.7143", "-83.5102")

# rec_areas_in_ME = find_recareas_by_location(state="ME")

# facilities_near_gtlbrg =find_facilities_by_location(lat="35.7143", long="-83.5102")

# activities_near_gtlbrg = find_activities_by_loaction(activity="hiking", lat="35.7143", long="-83.5102")

# hotels = find_hotels_by_location(lat="35.4356", long="-83.8191")