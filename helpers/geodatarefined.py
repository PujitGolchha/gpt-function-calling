
from helpers.dbpedia import *
from helpers.openstreetmaps import *
from helpers import download_file
from pathlib import Path

path = Path(__file__).parent.absolute()
country_codes_dict=download_file(str(path)+"\country_codes_dict.pkl")
country_names_dict=download_file(str(path)+"\country_names_dict.pkl")

# function to get details about a city
def get_city_details(name:str,state:str=None, country:str=None):
    """Gets basic details of a city from the database, which may include details like the address, state-code, country-code, latitude, longitude, postal code, area, elevation, population, leader/mayor and additional names, whichever are available for a city.

     Args:
          name: Name of the city.
          state: Name of the state the city is part of. Defaults to None.
          country: Name of the country the city is part of. Defaults to None.

     Returns:
          dict: a dictionary containing details about a city.
     """
    
    query=name
    if state!=None:
        query= query+ ", "+ state
    if country!=None:
        query= query+ ", "+ country

    results=get_location_details_from_Open_Street_Maps(query=query,top=5)
    open_street_result_found=False
    for result in results:
        state_result_found=True
        if state!=None:
            if result["State"]==state:
                state_result_found=True
            else:
                state_result_found=False
        
        country_result_found=True
        if country!=None:
            if result["Country"]==country:
                country_result_found=True
            else:
                country_result_found=False
        
        if state_result_found and country_result_found and ("city" in result["Addresstype"] or "town" in result["Addresstype"]):
            open_street_result_found =True
            open_street_result=result
            break

    

    final_result={}
    if open_street_result_found:

        final_result=open_street_result

        #country cannot be empty if state is specified
        if country==None and state!=None:
            country=final_result["Country"]

        dp_pedia_result=get_city_details_from_db_pedia(name,state,country)

        if "Error" not in dp_pedia_result.keys() and (dp_pedia_result["Country"]==final_result["Country"] or dp_pedia_result["State"]==final_result["State"]) and len(dp_pedia_result.keys())>0:
                del dp_pedia_result["Country"]
                final_result= {**final_result,**dp_pedia_result}
    else:
        dp_pedia_result=get_city_details_from_db_pedia(name,state,country)
        final_result=dp_pedia_result
    
    return final_result

# function to get details about a state
def get_state_details(name:str, country:str=None):
    """Gets basic details of a state from the database, which may include details like the founding date, address, state-code, country-code, latitude, longitude, area, elevation, population, additional names, timezone, demonym and names of some cities in the state, whichever are available for a state.

     Args:
          name: Name of the state.
          country: Name of the country the state is part of. Defaults to None.

     Returns:
          dict: a dictionary containing details about a state.
     """
    
    query=name
    if country!=None:
        query= query+ ", "+ country

    results=get_location_details_from_Open_Street_Maps(query=query,top=5)
    open_street_result_found=False
    for result in results:
        
        country_result_found=True
        if country!=None:
            if result["Country"]==country:
                country_result_found=True
            else:
                country_result_found=False
        
        if  country_result_found and ("state" in result["Addresstype"]):
            open_street_result_found =True
            open_street_result=result
            break


    final_result={}
    if open_street_result_found:
        final_result=open_street_result
        dp_pedia_result=get_state_details_from_db_pedia(name,country)

        if "Error" not in dp_pedia_result.keys() and dp_pedia_result["Country"]==final_result["Country"] and len(dp_pedia_result.keys())>0:
                del dp_pedia_result["Country"]
                final_result= {**final_result,**dp_pedia_result}
    else:
        dp_pedia_result=get_state_details_from_db_pedia(name,country)
        final_result=dp_pedia_result

    
    return final_result

# function to get details about a country
def get_country_details(name:str):
    """Gets basic details of a country from the database, which may include details like the founding date, country-code, latitude, longitude, area, elevation, population, additional names, timezones, demonym, currency, capital, government type, national anthem, region, subregion, phonecode, names and title of leaders, names and geo coordinates of states in the country, whichever are available for a country.

     Args:
          name: Name of the country.

     Returns:
          dict: a dictionary containing details about a country.
     """
    query=name
   

    results=get_location_details_from_Open_Street_Maps(query=query,top=5)
    open_street_result_found=False
    for result in results:  
        if  ("country" in result["Addresstype"]):
            open_street_result_found =True
            open_street_result=result
            break


    final_result={}
    if open_street_result_found:
        final_result=open_street_result
        dp_pedia_result=get_country_details_from_db_pedia(name)

        if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>0:
                final_result= {**final_result,**dp_pedia_result}
        final_result={**final_result,**country_codes_dict[final_result["Country_code"]]}

    else:
        dp_pedia_result=get_country_details_from_db_pedia(name)
        if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>0:
            final_result= {**final_result,**dp_pedia_result}
        try:
            final_result={**final_result,**country_names_dict[name]}
        except:
            final_result=final_result
    return final_result

# function to get details about an attraction
def get_attraction_details(name:str,city:str=None,state:str=None,country:str=None):
    """Gets basic details of an attraction from the database, which may include details like the address, state-code, country-code, latitude, longitude, start date, completion date, opening date, additional names, height, building type and architect, whichever are available for an attraction.

     Args:
          name: Name of the attraction.
          city: Name of the city the attraction is part of. Defaults to None.
          state: Name of the state the attraction is part of. Defaults to None.
          country: Name of the country the attraction is part of. Defaults to None.

     Returns:
          dict: a dictionary containing details about an attraction.
     """

    query=name
    if state!=None:
        query= query+ ", "+ state
    if city!=None:
        query= query+ ", "+ city
    if country!=None:
        query= query+ ", "+ country

    results=get_location_details_from_Open_Street_Maps(query=query,top=5)
    open_street_result_found=False
    for result in results:

        city_result_found=True
        if city!=None:
            if result["City"]==city:
                city_result_found=True
            else:
                city_result_found=False
                
        state_result_found=True
        if state!=None:
            if result["State"]==state:
                state_result_found=True
            else:
                state_result_found=False
        
        country_result_found=True
        if country!=None:
            if result["Country"]==country:
                country_result_found=True
            else:
                country_result_found=False
        
        if state_result_found and country_result_found and  city_result_found:
            open_street_result_found =True
            open_street_result=result
            break
   

    final_result={}
    if open_street_result_found:
        final_result=open_street_result
        dp_pedia_result=get_attraction_details_from_db_pedia(final_result["Name"])
        if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>=2 :
            final_result= {**final_result,**dp_pedia_result}
        else:
            dp_pedia_result=get_attraction_details_from_db_pedia(name)
            if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>=2:
                final_result= {**final_result,**dp_pedia_result}
    else:
        dp_pedia_result=get_attraction_details_from_db_pedia(name)
        final_result=dp_pedia_result
    
    return final_result

# function to get details about an airport
def get_airport_details(name:str,city:str=None,state:str=None,country:str=None):
    """Gets basic details of an airport from the database, which may include details like the address, state-code, country-code, latitude, longitude, elevation, IATA Code, ICAO Code, runway length and runway surface, whichever are available for an airport.

     Args:
          name: Name of the airport.
          city: Name of the city the airport is part of. Defaults to None.
          state: Name of the state the airport is part of. Defaults to None.
          country: Name of the country the airport is part of. Defaults to None.

     Returns:
          dict: a dictionary containing details about an airport.
     """

    query=name
    if city!=None:
        query= query+ ", "+ city
    if state!=None:
        query= query+ ", "+ state  
    if country!=None:
        query= query+ ", "+ country

    results=get_location_details_from_Open_Street_Maps(query=query,top=5)
    open_street_result_found=False
    for result in results:

        city_result_found=True
        if city!=None:
            if result["City"]==city:
                city_result_found=True
            else:
                city_result_found=False
                
        state_result_found=True
        if state!=None:
            if result["State"]==state:
                state_result_found=True
            else:
                state_result_found=False
        
        country_result_found=True
        if country!=None:
            if result["Country"]==country:
                country_result_found=True
            else:
                country_result_found=False
        
        if state_result_found and country_result_found and  city_result_found:
            open_street_result_found =True
            open_street_result=result
            break
   

    final_result={}
    if open_street_result_found:
        final_result=open_street_result
        dp_pedia_result=get_airport_details_from_db_pedia(final_result["Name"])
        if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>0:
            final_result= {**final_result,**dp_pedia_result}
        else:
            dp_pedia_result=get_airport_details_from_db_pedia(name)
            if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>0:
                final_result= {**final_result,**dp_pedia_result}
    else:
        dp_pedia_result=get_airport_details_from_db_pedia(name)
        final_result=dp_pedia_result
    
    return final_result

# function to get details about an university
def get_university_details(name:str,city:str=None,state:str=None,country:str=None):
    """Gets basic details of an university from the database, which may include details like the address, state-code, country-code, latitude, longitude, Chancellor, No of Students, No of Undergraduates, No of Doctoral Candidates, No of Postgrad Students, No of Academic Staff, No of Adminstrative Staff, type and other names, whichever are available for an university.

     Args:
          name: Name of the university.
          city: Name of the city the university is part of. Defaults to None.
          state: Name of the state the university is part of. Defaults to None.
          country: Name of the country the university is part of. Defaults to None.

     Returns:
          dict: a dictionary containing details about an university.
     """

    query=name
    if state!=None:
        query= query+ ", "+ state
    if city!=None:
        query= query+ ", "+ city
    if country!=None:
        query= query+ ", "+ country

    results=get_location_details_from_Open_Street_Maps(query=query,top=5)
    open_street_result_found=False
    for result in results:

        city_result_found=True
        if city!=None:
            if result["City"]==city:
                city_result_found=True
            else:
                city_result_found=False
                
        state_result_found=True
        if state!=None:
            if result["State"]==state:
                state_result_found=True
            else:
                state_result_found=False
        
        country_result_found=True
        if country!=None:
            if result["Country"]==country:
                country_result_found=True
            else:
                country_result_found=False

        
        if state_result_found and country_result_found and city_result_found and "university" in result["Type"]:
            open_street_result_found =True
            open_street_result=result
            break
   

    final_result={}
    if open_street_result_found:
        final_result=open_street_result
        dp_pedia_result=get_university_details_from_db_pedia(final_result["Name"])
        #using len 4 because Indian Institute of Technology Kharagpur returns only 1
        if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>4:
            final_result= {**final_result,**dp_pedia_result}
        else:
            dp_pedia_result=get_university_details_from_db_pedia(name)
            if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>4:
                final_result= {**final_result,**dp_pedia_result}  
            else:
                if city!=None:
                    name= name+ " "+ city
        
                dp_pedia_result=get_university_details_from_db_pedia(name)
                if "Error" not in dp_pedia_result.keys() and len(dp_pedia_result.keys())>4:
                    final_result= {**final_result,**dp_pedia_result}   
                   
    else:
        dp_pedia_result=get_university_details_from_db_pedia(name)
        final_result=dp_pedia_result
    
    return final_result

# function to get basic details of a geo entity
def searchdetails(name:str,entity_type:str,city:str=None,state:str=None,country:str=None):
    """Gets basic details of a geo entity from the database. All details whichever are available are returned. The address, state-code, country-code, latitude, longitude are usually included for all entities.  Area, elevation, population, additional names are usually included for city, state, and country. Based on entity type, other details are described below.
       For a city: postal code, leader/mayor.
       For a state: founding date, timezone, demonym, names of some cities in the state.
       For a country: founding date, timezones, demonym, currency, capital, government type, national anthem, region, subregion, names and titles of leaders, names and coordinates of states in the country.
       For an attraction: start date, completion date, opening date, additional names, height, building type and architect.
       For an airport: elevation, IATA Code, ICAO Code, runway length, runway surface.
       For an university: type, other names, Chancellor and No of Students, Undergraduates, Postgraduates, PHD's, Academic and Admin Staff.

     Args:
          name: Name of the entity.
          entity_type: Type of entity. Must be one of ['city', 'state', 'country', 'university','airport','attraction'].
          city: Name of the city the entity is part of. Defaults to None.
          state: Name of the state the entity is part of. Defaults to None.
          country: Name of the country the entity is part of. Defaults to None.

     Returns:
          dict: a dictionary containing details about a geo entity.
     """

    query_dict={"name":name}
    if entity_type=="country":
        formatted_results= get_country_details(**query_dict)
    elif entity_type=="state": 
        query_dict["country"]=country
        formatted_results=get_state_details(**query_dict)
    elif entity_type=="city": 
        query_dict["country"]=country
        query_dict["state"]=state
        formatted_results=get_city_details(**query_dict)
    elif entity_type=="attraction": 
        query_dict["country"]=country
        query_dict["state"]=state
        query_dict["city"]=city
        formatted_results=get_attraction_details(**query_dict)
    elif entity_type=="airport": 
        query_dict["country"]=country
        query_dict["state"]=state
        query_dict["city"]=city
        formatted_results=get_airport_details(**query_dict)
    elif entity_type=="university": 
        query_dict["country"]=country
        query_dict["state"]=state
        query_dict["city"]=city
        formatted_results=get_university_details(**query_dict)
    else:
        formatted_results={"Error":"Wrong Function Parameters"}

    return formatted_results

