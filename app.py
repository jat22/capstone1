from flask import Flask, redirect, render_template, url_for, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests, json
from keys import REC_API_KEY
from func import do_search
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
CURR_USER = "curr_user"

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

@app.route('/search')
def show_search_results():
    type = request.args.get("type")
    term = request.args.get("term")
    state = request.args.get("state")
    results = do_search(type, term, state)
    return render_template('search.html', results=results)

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
    return render_template('trips.html', trips=trips)