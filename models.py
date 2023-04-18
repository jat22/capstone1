from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

from func import get_all_activities

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

class Facility(db.Model):
	__tablename__ = "facilities"

	id = db.Column(db.Integer,
		primary_key=True,
        autoincrement=False)
	name = db.Column(db.Text,
        nullable=False) 
	type = db.Column(db.Text)
	email = db.Column(db.Text)
	phone = db.Column(db.Text)
	physical_address1 = db.Column(db.Text)
	physical_address2 = db.Column(db.Text)
	physical_address3 = db.Column(db.Text)
	physical_city = db.Column(db.Text)
	physical_state = db.Column(db.Text)
	lat = db.Column(db.Float)
	long = db.Column(db.Float)
	directions = db.Column(db.Text)
	ada = db.Column(db.Text)
	description = db.Column(db.Text)

	def __repr__(self):
		return f"<Facility #{self.id}: {self.name}, {self.type}>"

	
class RecArea(db.Model):
	__tablename__ = "rec_areas"

	id = db.Column(db.Integer,
		primary_key=True,
		autoincrement=False)
	name = db.Column(db.Text,
        nullable=False) 
	email = db.Column(db.Text)
	phone = db.Column(db.Text)
	physical_address1 = db.Column(db.Text)
	physical_address2 = db.Column(db.Text)
	physical_address3 = db.Column(db.Text)
	physical_city = db.Column(db.Text)
	physical_state = db.Column(db.Text)
	lat = db.Column(db.Float)
	long = db.Column(db.Float)
	directions = db.Column(db.Text)
	description = db.Column(db.Text)

	def __repr__(self):
		return f"<RecArea #{self.id}: {self.name}>"
	
class Activity(db.Model):
	__tablename__ = "activities"

	id = db.Column(db.Integer,
		primary_key=True)
	name = db.Column(db.Text,
		nullable=False)
	
	def __repr__(self):
		return f"<Activity #{self.id}: {self.name}>"
	
	@classmethod
	def update_activities(self):
		activities = get_all_activities()
		existing_act_ids = [id[0] for id in db.session.query(Activity.id).all()]

		for activity in activities:
			if activity["id"] not in existing_act_ids:
				new_activity = Activity(
					id=activity["id"],
					name=activity["name"]
				)
			db.session.add(new_activity)
		db.session.commit()
	
class Link(db.Model):
	__tablename__ = "links"

	id = db.Column(db.Integer,
		primary_key=True,
		autoincrement=False)
	title = db.Column(db.Text)
	type = db.Column(db.Text)
	url = db.Column(db.Text)
	rec_area = db.Column(db.Integer,
		db.ForeignKey('rec_areas.id'))
	facility = db.Column(db.Integer,
		db.ForeignKey('facilities.id'))
	
	def __repr__(self):
		return f"<Link {self.title}>"
	
class RecAreaFacility(db.Model):
	__tablename__ = "recarea_facilities"

	facility = db.Column(db.ForeignKey("facilities.id"),
		    primary_key=True)
	recarea = db.Column(db.ForeignKey("rec_areas.id"),
		    primary_key=True)
	
class FacilityActivity(db.Model):
	__tablename__ = "facility_activities"

	activity = db.Column(db.ForeignKey('activities.id'),
		    primary_key=True)
	facility = db.Column(db.ForeignKey('facilities.id'),
		    primary_key=True)

class User(db.Model):
	__tablename__ = "users"

	username = db.Column(db.Text,
			primary_key=True,
			autoincrement=False)
	email = db.Column(db.Text,
		   	nullable=False)
	password = db.Column(db.Text,
		    nullable=False)
	first_name = db.Column(db.Text)
	last_name = db.Column(db.Text)
	phone = db.Column(db.Text)
	street_address = db.Column(db.Text)
	city = db.Column(db.Text)
	state = db.Column(db.Text)
	
	def __repr__(self):
		return f"<User:{self.username}>"
		
	@classmethod
	def signup(cls, username, email, password):
		hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

		user = User(username=username, email=email, password=hashed_pwd)

		db.session.add(user)

	@classmethod
	def authenticate(cls, username, password):
		user = cls.query.filter_by(username=username).first()

		if user:
			if bcrypt.check_password_hash(user.password, password):
				return user
		
		return False

	
class Trip(db.Model):
	__tablename__ = "trips"

	id = db.Column(db.Integer,
		primary_key=True)
	name = db.Column(db.Text)
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)
	comments = db.Column(db.Text)
	user = db.Column(db.ForeignKey("users.username"))
	

	def __repr__(self):
		return f"<Trip: {self.name} for {self.user}>"
	
class TripActivity(db.Model):
	__tablename__ = "trip_activities"
	id = db.Column(db.Integer,
		primary_key=True)
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)
	activity = db.Column(db.ForeignKey("activities.id"))
	facility = db.Column(db.ForeignKey("facilities.id"))
	trip = db.Column(db.ForeignKey("trips.id"))

class CampgroundStays(db.Model):
	__tablename__ = "campground_stays"
	id = db.Column(db.Integer,
		primary_key=True)
	start_date = db.Column(db.Date)
	end_date = db.Column(db.Date)
	trip = db.Column(db.ForeignKey("trips.id"))
	facility = db.Column(db.ForeignKey("facilities.id"))

class CheckList(db.Model):
	__tablename__ = "checklists"
	id = db.Column(db.Integer,
		primary_key=True)
	title = db.Column(db.Text)
	trip = db.Column(db.ForeignKey("trips.id"))

class CheckListItem(db.Model):
	__tablename__ = "checklist_items"
	id = db.Column(db.Integer,
		primary_key=True)
	title = db.Column(db.Text)
	notes = db.Column(db.Text)
	checklist = db.Column(db.ForeignKey("checklists.id"))