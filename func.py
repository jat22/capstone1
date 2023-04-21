from flask import Flask, redirect, render_template, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import requests, json, asyncio
from keys import REC_API_KEY, MAPS_KEY, TOMTOM_KEY

REC_BASE_URL = "https://ridb.recreation.gov/api/v1"
GEOCODE_BASE_URL = "https://api.tomtom.com/search/2/structuredGeocode.json"
ACTIVITIES = "activities"
CAMPSITES = "campsites"
EVENTS = "events"
FACILITIES = "facilities"
PERMIT = "permitentrances"
RECAREAS = "recareas"
TOURS = "tours"

############################# SEARCH FOR THINGS ################################

def resource_search(endpoint, query="", limit="", offset="", full="true", state="", activity="", lat="", long="", radius="", sort=""):
    
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

def resource_search_by_id(endpoint, id):
    resp = requests.get(f"{REC_BASE_URL}/{endpoint}/{id}",
		params={
			"apikey" : REC_API_KEY,
            "full" : "true"
		})
    return resp.json()

def activities_with_parent_resources_by_location(location_type, city="", state="", zip=""):
    coords = get_coordinates(location_type, city, state, zip)
    lat = coords[0].get('lat')
    long = coords[0].get('lon')

    recareas = min_data(resource_search(RECAREAS, lat=lat, long=long)["RECDATA"], "RecArea")
    facilities = min_data(resource_search(FACILITIES, lat=lat, long=long)["RECDATA"], "Facility")

    fac_rec_data = recareas + facilities
    print(fac_rec_data)
    fac_rec_activities =[]
    all_activities_dict = {}

    for fac_rec in fac_rec_data:
        for activity in fac_rec["activities"]:
            fac_rec_activities.append(activity)


    for a in fac_rec_activities:
        name = a["name"]
        id = a["id"]
        parent_type = a["parent_type"]
        parent_id = a["parent_id"]
        parent_name = a["parent_name"]

        if name not in all_activities_dict:
            all_activities_dict[name] = ({"name" : name, "id" : id,
                                    "parents" : [{"type" : parent_type, "id" : parent_id, "name" : parent_name}]})
        else:
            all_activities_dict[name]['parents'].append({"type" : parent_type, "id" : parent_id, "name" : parent_name})

    all_activites_parents = [all_activities_dict[act] for act in all_activities_dict]

    print(all_activites_parents)

    return all_activites_parents



def recareas_by_location(location_type, city="", state="", zip=""):
    coords = get_coordinates(location_type, city, state, zip)
    lat = coords[0].get('lat')
    long = coords[0].get('lon')

    recareas = clean_resource(resource_search(RECAREAS, lat=lat, long=long)["RECDATA"], "RecArea")
    return recareas

def campgrounds_by_location(location_type, city="", state="", zip=""):
    coords = get_coordinates(location_type, city, state, zip)
    lat = coords[0].get('lat')
    long = coords[0].get('lon')

    facilities = clean_resource(resource_search(FACILITIES, lat=lat, long=long)["RECDATA"], "Facility")
    campgrounds = filter_(facilities)

    return campgrounds

def get_resource_details(type, id):
    endpoint = ""

    if type == "RecArea":
        endpoint = "recareas"
    if type == "Facility":
        endpoint = "facilities"

    resource = clean_resource([resource_search_by_id(endpoint, id)], type)
    return resource


################################# GEOLOCATION ##################################
    
def geolocation_search(city="", state="", zip=""):
    resp = requests.get(f"{GEOCODE_BASE_URL}",
                        params = {
                            "key" : TOMTOM_KEY,
                            "countryCode" : "US",
                            "municipality" : city,
                            "countrySubdivision" : state,
                            "postalCode" : zip
                        })
    return resp.json()

def get_coordinates(search_type, city="", state="", zip=""):
    data = geolocation_search(city, state, zip)
    if search_type == "city-state":
        coordinates = [result.get('position') for result in data.get("results")
            if result.get('entityType') == "Municipality"]
        return coordinates
    if search_type == "zip":
        coordinates = [result.get('position') for result in data.get("results")
            if result.get('entityType') == "PostalCodeArea"]
        return coordinates
    
############################ CLEAN THINGS ###########################

def get_activity_names(resources):
    activities = []
    for resource in resources:
        for activity in resource.get("activities"):
            activities.append(activity.get('name'))
    return activities


def min_data(data, type):
    rec_areas = data
    clean_rec_areas = [{
        "name" : area.get(f"{type}Name"),
        "id" : area.get(f"{type}ID"),
        "activities" : clean_activities(
            area.get("ACTIVITY"), type, area.get(f"{type}ID"), area.get(f"{type}Name")),
        }
        for area in rec_areas]
    return clean_rec_areas

def clean_resource(data, type):
    if type == "RecArea":
        clean_resources = [{
            "name" : area.get("RecAreaName"),
            "id" : area.get("RecAreaID"),
            "type" : "RecArea",
            "phone" : area.get("RecAreaPhone"),
            "email" : area.get("RecAreaEmail"),
            "address" : clean_address(area.get("RECAREAADDRESS"), "RecArea"),
            "description" : area.get("RecAreaDescription"),
            "directions" : area.get("RecAreaDirections"),
            "coordinates" : area.get("GEOJSON").get("COORDINATES"),
            "activities" : clean_activities(
                area.get("ACTIVITY"), type, area.get("RecAreaID"), area.get("NameID")),
            "facilities" : name_id_only(area.get("FACILITY"), "Facility"),
            "parent_org_id" : area.get("ParentOrgID"),
            "links" : clean_links(area.get("LINK"))
            } 
            for area in data]
        
    if type == "Facility":
        clean_resources = [{
            "name" : facility.get("FacilityName"),
            "id" : facility.get("FacilityID"),
            "email" : facility.get("FacilityEmail"),
            "phone" : facility.get("FacilityPhone"),
            "address" : clean_address(facility.get("FACILITYADDRESS"), "Facility"),
            "type" : facility.get("FacilityTypeDescription"),
            "activities" : clean_activities(
                facility.get("ACTIVITY"), type, facility.get("FacilityID"), facility.get("NameID")),
            "ada" : facility.get("FacilityAdaAccess"),
            "description" : facility.get("FacilityDescription"),
            "directions" : facility.get("FacilityDirections"),
            "coordinates" : facility.get("GEOJSON").get("COORDINATES"),
            "parent_org_id" : facility.get("ParentOrgID"),
            "parent_rec_area_id" : facility.get("ParentRecAreaID"),
            "links" : clean_links(facility.get("LINK"))
            } for facility in data]
    
    return clean_resources

def filter_(facilities):
    campgrounds = [facility for facility in facilities if facility ["type"] == "Campground"]
    return campgrounds


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

def name_id_only(list, type):

    info = [{
		"id" : data.get(f"{type}ID"), 
		"name" : data.get(f"{type}Name").lower()
		} 
		for data in list]
    return info

def clean_activities(list, parentType, parentID, parentName):
    activities = [{
		"name" : data.get("ActivityName").lower(),
        "id" : data.get("ActivityID"),
        "parent_type" : parentType,
        "parent_id" : parentID,
        "parent_name" : parentName
        }
        for data in list]
    return activities

def clean_links(list):
    links = [{
        "id" : link.get("EntityLinkID"),
        "title" : link.get("Title"),
        "type" : link.get("LinkType"),
        "url" : link.get("URL")
		}
        for link in list]
    return links

def get_all_activities():
    data = resource_search("activities")["RECDATA"]
    return name_id_only(data, "Activity")


