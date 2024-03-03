from OSMPythonTools.nominatim import Nominatim
from geopy.geocoders import Nominatim as noma
from geopy import distance
from . import open_street_maps_user_agent
nominatim = Nominatim()
geolocator = noma(user_agent=open_street_maps_user_agent)

def format_location_details(area:dict):
    details_dict={}
    location = geolocator.reverse(str(area["lat"])+","+str(area["lon"]),language="en")
    address=location.raw['address']
    state = address.get('state', '')
    country = address.get('country', '')
    city = address.get('city', '')
    try:
        country_code=address.get("ISO3166-2-lvl4").split("-")[0]
        state_code=address.get("ISO3166-2-lvl4").split("-")[1]
    except:
        country_code=address.get("country_code","").upper()
        state_code=""
    details_dict={"Country":country,"State":state,"City":city,"State_code":state_code,"Country_code":country_code,}
    details_dict["Type"]=area.get("type","")
    details_dict["Class"]=area.get("class","")
    details_dict["Importance"]=area.get("importance","")
    details_dict["Addresstype"]=area.get("addresstype","")
    details_dict["Name"]=area.get("name","")
    details_dict["Latitude"]=area["lat"]
    details_dict["Longitude"]=area["lon"]

    if(details_dict["Addresstype"]=="country"):
        del details_dict["State_code"], details_dict["Country"],details_dict["State"], details_dict["City"]
    elif(details_dict["Addresstype"]=="state"):
        del  details_dict["City"], details_dict["State"]
    return details_dict

def get_location_details_from_Open_Street_Maps(query:str,top=1):
    details_list=[]
    if top==1:
        #area = geolocator.geocode(query,exactly_one=True).raw
        #using OSMPythonTools as it seems to give better results
        area=nominatim.query(query).toJSON()[0]
        details_dict=format_location_details(area)
        details_list.append(details_dict)
    else:
        #areas = geolocator.geocode(query,exactly_one=False)
        areas = nominatim.query(query).toJSON()
        num_results= top if len(areas)>top else len(areas)
        for area in areas[0:num_results]:
            #details_dict=format_location_details(area.raw)
            details_dict=format_location_details(area)
            details_list.append(details_dict)      
    return details_list

def search_open_street_maps(query:str,top:int=1):
    """Searches Open Street Maps which is a Map of the world, to get results which include details like City, State, Country, State Code, Country Code, Class, Address Type, Latitude and Longitude about a location/locations.

    Args:
        query: A basic search query to satisfy the information needs. The search query should be similar to the query you would use to search on Google Maps.
        top: No of results to be returned.

    Returns:
        dict: a dictionary containing search results for the query.
    """

    details_list=[]
    if top==1:
        #area = geolocator.geocode(query,exactly_one=True).raw
        
        # using OSMPythonTools as it seems to give better results
        area=nominatim.query(query).toJSON()[0]
        details_dict=format_location_details(area)
        details_list.append(details_dict)
    else:
        areas = geolocator.geocode(query,exactly_one=False)
        areas = nominatim.query(query).toJSON()
        num_results= top if len(areas)>top else len(areas)
        for area in areas[0:num_results]:
            #details_dict=format_location_details(area.raw)
            details_dict=format_location_details(area)
            details_list.append(details_dict)      
    return details_list

def calculate_distance(start_lat:float,start_lon:float,finish_lat:float,finish_lon:float,metric:str):
    """Calculates the shortest distance on the surface of an ellipsoidal model of the earth between two points.
    
    Args:
        start_lat: Latitude of starting point
        start_lon: Longitude of starting point
        finish_lat: Latitude of finishing point
        start_lon: Longitude of finishing point
        metric: The metric to calculate the distance in. Must be one of ["miles","kms"]

    Returns:
        float: diatnce between two points.
    """
    start=(start_lat,start_lon)
    finish=(finish_lat,finish_lon)

    if metric=="miles":
        return distance.distance(start, finish).miles
    elif metric=="kms":
        return distance.distance(start, finish).km
    else:
        return "Wrong Metric"