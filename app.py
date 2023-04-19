from flask import Flask, redirect, render_template, url_for, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests, json
from keys import REC_API_KEY, MAPS_KEY, TOMTOM_KEY
from func import do_search, get_coordinates, geolocation_search, resource_search
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, RecArea, Facility, RecAreaFacility, Link, FacilityActivity, Activity, TripActivity, Trip, CampgroundStays, User, CheckList, CheckListItem
from forms import SignUpForm, LoginForm, NewTripForm

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
GEOCODE_BASE_URL = f"https://api.tomtom.com/search/2/geocode/"
CURR_USER = "curr_user"
CURR_TRIP = "curr_trip"

def do_login(user):
    session[CURR_USER] = user.username

def do_logout():
    if CURR_USER in session:
        del session[CURR_USER]

@app.before_request
def add_user_to_g():
    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])
    else:
        g.user = None



@app.route('/')
def show_home():
    return render_template('home.html')

@app.route('/api/search')
def show_search_results():
    search_type = request.args.get("search_type")
    location_type = request.args.get("location_type")
    city = request.args.get("city")
    state = request.args.get("state")
    zip = request.args.get("zip")

    results = do_search(search_type, location_type, city, state, zip)
    
    return results

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        try:
            user = User.signup(
                username = form.username.data,
                email = form.email.data,
                password = form.password.data
            )
            db.session.commit()
        except IntegrityError:
            flash("Username is already taken", "danger")
            return render_template('signup.html', form=form)
        
        return redirect('/')
    
    else:
        return render_template('signup.html', form = form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            return redirect('/')
        flash("Password/User incorrect", "danger")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    do_logout()
    flash("You are now logged out.", "success")
    return redirect('/')


@app.route('/trips/new', methods=["GET", "POST"])
def create_trip():
    form = NewTripForm()
    if form.validate_on_submit():
        if not g.user:
            flash("Please login to create a trip", "danger")
            return redirect("/login")
        new_trip = Trip(
            name = form.name.data,
            start_date = form.start_date.data,
            end_date = form.end_date.data,
            comments = form.comments.data,
            user = g.user.username
        )
        db.session.add(new_trip)
        db.session.commit()
        return redirect(f"/trips")
    return render_template('new-trip.html', form=form)

@app.route('/trips')
def show_trips():
    if not g.user:
        flash("DANGER WILL ROBINSON", "danger")
        return redirect("/login")
    trips = Trip.query.filter_by(user=g.user.username)
    return render_template('my-trips.html', trips=trips)

@app.route('/trips/<int:trip_id>', methods=["GET","PATCH"])
def show_a_trip(trip_id):
    if not g.user:
        flash("DANGER WILL ROBINSON", "danger")
        return redirect("/login")
    # if session[CURR_TRIP]:
    #     new_activity = TripActivity(activity=)

    # session[CURR_TRIP] = trip_id
    trip = Trip.query.get(trip_id)
    activities = [activity for activity 
                    in TripActivity.query.filter_by(trip=trip_id).all()]
    return render_template('trip.html', trip=trip, activities=activities)