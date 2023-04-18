from flask import Flask, redirect, render_template, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests, json, asyncio
from keys import REC_API_KEY

REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
ACTIVITIES = "activities"
CAMPSITES = "campsites"
EVENTS = "events"
FACILITIES = "facilities"
PERMIT = "permitentrances"
RECAREAS = "recareas"
TOURS = "tours"

#################### GENERAL SEARCH FUNCTIONS ###################
def resource_search(endpoint, query="", limit="", offset="", full="", state="", activity="", lat="", long="", radius="", sort=""):
    """Get request is sent to Recreaction.gov API containing search parameters.
	
	Keyword arguments:
    endpoint -- required
	query -- optional, keyword
    limit -- optional, max records returned
    offset -- optional
    full -- optional, true or false
    state -- optional, two letter state code
    activity -- optional
    latitude -- optional
    longitute -- optional
    radius -- optional, miles
    sort -- ID, Date, or Name
	Return: dict with requested data
	"""
	

    resp = requests.get(f"{REC_BASE_URL}/{endpoint}",
		params={
			"apikey" : REC_API_KEY,
			"query" : query,
			"limit" : limit,
			"offset" : offset,
			"full" : full,
			"state" : state,
			"activity" : activity,
			"latitude": lat,
			"longitude" : long,
			"radius" : radius,
			"sort" : sort
		})
    return resp.json()

def resource_by_id(endpoint, id):
    resp = requests.get(f"{REC_BASE_URL}/{endpoint}/{id}", params={"apikey" : REC_API_KEY, "full" : "true"})
    return resp.json()

def child_resources_by_parent(parent_resource_endpoint, parent_source_id, child_resource_name, query="", limit="", offset=""):
    resp = requests.get(f"{REC_BASE_URL}/{parent_resource_endpoint}/{parent_source_id}/{child_resource_name}",
		params={
			"apikey" : REC_API_KEY,
			"query" : query,
			"limit" : limit,
			"offset" : offset,
            "full" : "true"
		})
    return resp.json()

#######################LOCATION BASED SEARCH FUNCTIONS######################################

def find_campgrounds_by_location(lat, long):
    data = resource_search(FACILITIES, activity="CAMPING", lat=lat, long=long)
    return clean_campgrounds(data)

def find_recareas_by_location(state="", lat="", long=""):
    data = resource_search(RECAREAS, state=state, lat=lat, long=long)
    return clean_rec_areas(data)

def find_facilities_by_location(state="", lat="", long=""):
    data = resource_search(FACILITIES, state=state, lat=lat, long=long)
    return clean_facilities(data)

def find_activities_by_location(activity, state="", lat="", long=""):
    """ Search for activities by location and return a list of dictionaries with facility name and location where activities are located:
                [{fac_id, coordinates}]
    """
    
    recareas = find_recareas_by_location(state, lat, long)
    activity_locations = [{"id" : recarea.get("id"), "name" : recarea.get("name")} 
                          for recarea in recareas 
                          if any(a for a in recarea.get("activities") 
                                 if a.get("name") == activity)]
    return activity_locations
    
#######################RESOURCE BASED SEARCH FUNCTIONS#####################################
def get_all_activities():
    data = resource_search("activities")["RECDATA"]
    return name_id_only(data, "Activity")

def find_activities_by_recarea(recarea_id):
    data = child_resources_by_parent(RECAREAS, recarea_id, ACTIVITIES)["RECDATA"]
    activities = name_id_only(data, "Activity")
    return activities
 
def find_facilities_by_recarea(recarea_id):
    data = child_resources_by_parent(RECAREAS, recarea_id, FACILITIES)
    facilities = clean_facilities(data)
    return facilities

def find_activities_by_facility(facility_id):
    data = child_resources_by_parent(FACILITIES, facility_id, ACTIVITIES)
    activities = name_id_only(data)
    return activities
    
def find_campgrounds_by_recarea(recarea_id):
    facilities = find_facilities_by_recarea(recarea_id)
    campgrounds = filter_facilities("Campground", facilities)
    return campgrounds

########### DATA CLEANING FUNCTIONS ##############

def filter_facilities(type, facilities):
    filtered_facilities = [facility for facility in facilities if facility["FacilityTypeDescription"] == f"{type}"]
    return filtered_facilities

def clean_campgrounds(data):
    facilities = data["RECDATA"]
    filtered_facilities = filter_facilities("Campground", facilities) 
    clean_campgrounds = [{
        "name" : campground.get("FacilityName"),
        "id" : campground.get("FacilityID"),
        "email" : campground.get("FacilityEmail"),
        "phone" : campground.get("FacilityPhone"),
        "address" : clean_address(campground.get("FACILITYADDRESS"), "Facility"),
        "type" : campground.get("FacilityTypeDescription"),
        "acivities" : name_id_only(campground.get("ACTIVITY"), "Activity"),
        "ada" : campground.get("FacilityAdaAccess"),
        "description" : campground.get("FacilityDescription"),
        "directions" : campground.get("FacilityDirections"),
        "coordinates" : campground.get("GEOJSON").get("COORDINATES"),
        "parent_org_id" : campground.get("ParentOrgID"),
        "parent_rec_area_id" : campground.get("ParentRecAreaID"),
        "links" : clean_links(campground.get("LINK"))
		} 
        for campground in filtered_facilities]
    return clean_campgrounds

def clean_facilities(data):
    facilities = data["RECDATA"]
    clean_facilities = [{
        "name" : facility.get("FacilityName"),
        "id" : facility.get("FacilityID"),
        "email" : facility.get("FacilityEmail"),
        "phone" : facility.get("FacilityPhone"),
        "address" : clean_address(facility.get("FACILITYADDRESS"), "Facility"),
        "type" : facility.get("FacilityTypeDescription"),
        "activities" : name_id_only(facility.get("ACTIVITY"), "Activity"),
        "ada" : facility.get("FacilityAdaAccess"),
        "description" : facility.get("FacilityDescription"),
        "directions" : facility.get("FacilityDirections"),
        "coordinates" : facility.get("GEOJSON").get("COORDINATES"),
        "parent_org_id" : facility.get("ParentOrgID"),
        "parent_rec_area_id" : facility.get("ParentRecAreaID"),
        "links" : clean_links(facility.get("LINK"))
		} for facility in facilities]
    return clean_facilities

def clean_rec_areas(data):
    rec_areas = data["RECDATA"]
    clean_rec_areas = [{
        "name" : area.get("RecAreaName"),
        "id" : area.get("RecAreaID"),
        "phone" : area.get("RecAreaPhone"),
        "email" : area.get("RecAreaEmail"),
        "address" : clean_address(area.get("RECAREAADDRESS"), "RecArea"),
        "description" : area.get("RecAreaDescription"),
        "directions" : area.get("RecAreaDirections"),
        "coordinates" : area.get("GEOJSON").get("COORDINATES"),
        "activities" : name_id_only(area.get("ACTIVITY"), "Activity"),
        "facilities" : name_id_only(area.get("FACILITY"), "Facility"),
        "parent_org_id" : area.get("ParentOrgID"),
        "links" : clean_links(area.get("LINK"))
		} 
        for area in rec_areas]
    return clean_rec_areas

def name_id_only(list, type):
    info = [{
		"id" : data.get(f"{type}ID"), 
		"name" : data.get(f"{type}Name").lower()
		} 
		for data in list]
    return info

def clean_address(add_list, resource_type):
    addresses = [{
        "address_type" : address.get(f"{resource_type}AddressType"),
		"street_address_1" : address.get(f"{resource_type}StreetAddress1"),
		"street_address_2" : address.get(f"{resource_type}StreetAddress2"),
		"street_address_3" : address.get(f"{resource_type}StreetAddress3"),
		"city" : address.get("City"),
		"state" : address.get("AddressStateCode"),
		"postal_code" : address.get("PostalCode")
		}
    	for address in add_list]
    return addresses

def clean_links(list):
    links = [{
        "id" : link.get("EntityLinkID"),
        "title" : link.get("Title"),
        "type" : link.get("LinkType"),
        "url" : link.get("URL")
		}
        for link in list]
    return links


def do_search(type, term, state):
    if type == "activities":
        results = find_activities_by_location(activity=term, state=state)
        return results



    # camping_near_gtlbrg = find_campgrounds_by_location("35.7143", "-83.5102")

# rec_areas_in_ME = find_recareas_by_location(state="ME")

# facilities_near_gtlbrg =find_facilities_by_location(lat="35.7143", long="-83.5102")

# activities_near_gtlbrg = find_activities_by_loaction(activity="hiking", lat="35.7143", long="-83.5102")

# hotels = find_hotels_by_location(lat="35.4356", long="-83.8191")
# ACTIVITIES = "activities"
# CAMPSITES = "campsites"
# FACILITIES = "facilities"
# PERMIT = "permitentrances"
# RECAREAS = "recareas"
# TOURS = "tours"