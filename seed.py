from app import db
from models import Facility, RecArea, Activity, Link, RecAreaFacility, FacilityActivity, User, Trip, TripActivity, CampgroundStays, CheckList, CheckListItem



db.drop_all()
db.create_all()

user1 = User()