from tqdm import tqdm
import rdflib
from SPARQLWrapper import SPARQLWrapper,  JSON
from rdflib import Graph, URIRef, RDF
from rdflib.namespace import Namespace, RDFS

dbp = Namespace("http://dbpedia.org/property/")
dbo= Namespace("http://dbpedia.org/ontology/")
schema=Namespace("http://schema.org/")

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setReturnFormat(JSON)

def get_name_from_sub_graph(object:rdflib.term.URIRef):
    sub_graph = Graph()
    sub_graph.parse(object)
    for sub_object in sub_graph.objects(predicate=RDFS.label, unique=True):
        if (type(sub_object)==rdflib.term.Literal) and (sub_object.language=="en" or sub_object.language==None): 
            return sub_object.value
        
def get_object_value_from_graph(graph,predicate,all_values:bool=False):
    results=[]
    for object in graph.objects(predicate=predicate, unique=True):
        if (type(object)==rdflib.term.Literal) and (object.language=="en" or object.language==None): 
            if all_values==False:
                results=[object.value]
            else:
                results.append(object.value)
        elif (type(object)==rdflib.term.URIRef):
                if all_values==False:
                    results=[get_name_from_sub_graph(object)]
                else:
                    results.append(get_name_from_sub_graph(object))
    return results

def format_results(results:dict):
    final_results={}
    for key, value in results.items():
        if len(value)==1:
            final_results[key]=value[0]
        elif len(value)>1:
            final_results[key]=value
    return final_results

def get_attraction_details_from_db_pedia(name:str):
    property_dict={"Name":[dbp.name,RDFS.label],
    "Location":dbp.location,
    "NativeName":dbp.nativeName,
    "StartDate":[dbp.startDate,dbo.buildingStartDate],
    "BuildingType":dbp.buildingType ,
    "CompleteDate":[dbp.complete,dbp.completionDate,dbp.built,dbo.buildingEndDate] ,
    "Height":dbp.height ,
    "OriginalName":dbo.originalName ,
    "OpeningDate":dbo.openingDate,
    "Architect":dbp.architect,
    }

    list_objects=["NativeName","BuildingType","Architect"]


    formatted_results={}
    name=name.replace(" ","_")
    url='http://dbpedia.org/resource/'+ name
    uri = URIRef(url)
    main_graph = Graph()
    main_graph.parse(uri)

    for key, value in property_dict.items():
        if type(value)==list:
            for i in value:
                formatted_results[key]=get_object_value_from_graph(main_graph,i)
                if len(formatted_results[key])>0:
                        break
        elif key in list_objects:
            formatted_results[key]=get_object_value_from_graph(main_graph,value,all_values=True)
        else:
            formatted_results[key]=get_object_value_from_graph(main_graph,value)
                    
    return format_results(formatted_results)

def get_airport_details_from_db_pedia(name:str):
    property_dict={"Name":[dbp.name,RDFS.label],
    "IATA":[dbo.iataLocationIdentifier,dbp.iata],
    "ICAO":[dbo.icaoLocationIdentifier,dbp.icao],
    "RunwayLength":dbo.runwayLength,
    "RunwaySurface":dbo.runwaySurface,
    "Elevation":dbo.elevation ,
    "Location":dbp.location,
    "City":[dbo.city,dbp.city]
    }
    list_objects=["RunwayLength","RunwaySurface"]

    formatted_results={}
    name=name.replace(" ","_")
    url='http://dbpedia.org/resource/'+ name
    uri = URIRef(url)
    main_graph = Graph()
    main_graph.parse(uri)

    if (uri, RDF.type,dbo.Airport) not in main_graph:
        formatted_results["Error"]=["Result not found"]
        return format_results(formatted_results)

    for key, value in property_dict.items():
        if type(value)==list:
            for i in value:
                formatted_results[key]=get_object_value_from_graph( main_graph,i)
                if len(formatted_results[key])>0:
                        break
        elif key in list_objects:
            formatted_results[key]=get_object_value_from_graph(main_graph,value,all_values=True)
        else:
            formatted_results[key]=get_object_value_from_graph(main_graph,value)
                    
    return format_results(formatted_results)

def get_university_details_from_db_pedia(name:str):
    property_dict={"Name":[dbp.name,RDFS.label],
    "NativeName":dbp.nativeName,
    "Chancellor":dbp.chancellor,
    "NoOfStudents":dbp.students ,
    "NoofDoctoralCandidates":dbp.doctoral,
    "NoofUndergradStudents":dbp.undergrad,
    "NoofPostgradStudents":dbp.postgrad,
    "NoofAcademicStaff":[dbp.academicStaff,dbo.facultySize],
    "NoofAdminstrativeStaff":dbp.administrativeStaff,
    "Type":[dbp.type,dbo.type],
    "City":[dbo.city,dbp.city],
    "FormerNames":[dbp.formerNames,dbp.formerName],
    }
    list_objects=["NativeName","Chancellor","FormerNames"]

    formatted_results={}
    name=name.replace(" ","_")
    url='http://dbpedia.org/resource/'+ name
    uri = URIRef(url)
    main_graph = Graph()
    main_graph.parse(uri)

    if (uri, RDF.type,dbo.University) not in main_graph:
        formatted_results["Error"]=["Result not found"]
        return format_results(formatted_results)

    for key, value in property_dict.items():
        if type(value)==list:
            for i in value:
                formatted_results[key]=get_object_value_from_graph(main_graph,i)
                if len(formatted_results[key])>0:
                        break
        elif key in list_objects:
            formatted_results[key]=get_object_value_from_graph(main_graph,value,all_values=True)
        else:
            formatted_results[key]=get_object_value_from_graph(main_graph,value)
                    
    return format_results(formatted_results)

def execute_sparql_city_query(name:str,country:str,state:str=None):
    query="""
            PREFIX dbo: <http://dbpedia.org/ontology/> 
            PREFIX dbr: <http://dbpedia.org/resource/> 
            PREFIX dbp: <http://dbpedia.org/property/>

            SELECT ?Label
            WHERE{ ?City a dbo:City;
            dbp:name|foaf:name '%s'@en;
            rdfs:label ?Label;
            dbo:country ?Country.

            ?Country rdfs:label '%s'@en.
            FILTER ( LANG (?Label ) = 'en' )
            }
            """%(name,country)
    
    sparql.setQuery(query)
    sparql.setTimeout(1200000)
    ret = sparql.queryAndConvert()
    if ret["results"]["bindings"]:
        for r in ret["results"]["bindings"]:
            return {"Label":r["Label"]["value"]}
    
    if state:
        name= name+ ", "+state
        query2="""
        PREFIX dbo: <http://dbpedia.org/ontology/> 
        PREFIX dbr: <http://dbpedia.org/resource/> 
        PREFIX dbp: <http://dbpedia.org/property/>

        SELECT ?Label
        WHERE{ 
         ?City a dbo:City;
        rdfs:label ?Label;
        dbo:country ?Country.

        ?Country rdfs:label '%s'@en.
        FILTER(?Label ='%s'@en).
        FILTER ( LANG (?Label ) = 'en' )
        }"""%(country,name)
        
        sparql.setQuery(query2)
        sparql.setTimeout(1200000)
        ret = sparql.queryAndConvert()
        if ret["results"]["bindings"]:
            for r in ret["results"]["bindings"]:
                return {"Label":r["Label"]["value"]}

        query3="""
        PREFIX dbo: <http://dbpedia.org/ontology/> 
        PREFIX dbr: <http://dbpedia.org/resource/> 
        PREFIX dbp: <http://dbpedia.org/property/>

        SELECT ?Label
        WHERE{ 
        ?City a dbo:City;
        rdfs:label ?Label;
        dbp:name ?name;
        dbo:country ?Country.

        ?Country rdfs:label '%s'@en.
        FILTER (?name ='%s'@en).
        FILTER ( LANG (?Label ) = 'en' )
        }"""%(country,name)
        
        sparql.setQuery(query3)
        sparql.setTimeout(1200000)
        ret = sparql.queryAndConvert()
        if ret["results"]["bindings"]:
            for r in ret["results"]["bindings"]:
                return {"Label":r["Label"]["value"]}

    return {"Error":"Result not found"}
    
def get_city_details_from_db_pedia(name:str,state:str=None,country:str=None):
         
    property_dict={"Name":[dbp.name,RDFS.label],
    "Area":[dbp.areaKm,dbo.area],
    "Country":dbo.country,
    "State":dbo.federalState,
    "PostalCode":[dbp.postalCode,dbo.postalCode],
    "Elevation":[dbp.elevationM,dbo.elevation] ,
    "MaximumElevation":[dbp.elevationMaxM,dbo.maximumElevation],
    "MiniimumElevation":[dbo.minimumElevation,dbp.elevationMinM],
    "MetroArea":[dbp.metroAreaKm,dbp.areaMetroKm,dbo.areaMetro],
    "MetroAreaPop":[dbp.metroAreaPop,dbp.populationMetro,dbo.populationMetro],
    "MetroAreaDate":dbp.metroAreaDate,
    "MetroPopDate":dbp.metroAreaPopDate,
    "UrbanArea":dbp.urbanAreaKm,
    "UrbanAreaPop":dbp.urbanAreaPop,
    "UrbanAreaDate":dbp.urbanAreaDate,
    "UrbanPopDate":dbp.urbanPopDate,
    "TotalPopulation":[dbp.populationTotal,dbo.populationTotal],
    "TotalArea":[dbp.areaTotalKm,dbo.areaTotal],
    "TotalPopDate":dbp.populationAsOf,
    "Mayor/Leader":[dbp.mayor,dbp.leaderName],
    "CommuneStatus":dbp.communeStatus,
    "NickName":dbp.nickname,
    "OtherName":[dbp.otherName,dbo.synonym]
    }
    list_objects=["CommuneStatus","Mayor","NickName","OtherName"]

    formatted_results={}

    if state or country:
        result=execute_sparql_city_query(name,country,state)
        if "Label" in result.keys():
            name=result["Label"]
        else:
            formatted_results["Error"]=["Result not found"]
            return format_results(formatted_results)
    
    name=name.replace(" ","_")
    url='http://dbpedia.org/resource/'+ name
    uri = URIRef(url)
    main_graph = Graph()
    main_graph.parse(uri)

    if (uri, RDF.type,dbo.City) not in main_graph:
        formatted_results["Error"]=["Result not found"]
        return format_results(formatted_results)

    for key, value in tqdm(property_dict.items()):
        if type(value)==list:
            for i in value:
                formatted_results[key]=get_object_value_from_graph(main_graph,i)
                if len(formatted_results[key])>0:
                        break
        elif key in list_objects:
            formatted_results[key]=get_object_value_from_graph(main_graph,value,all_values=True)
        else:
            formatted_results[key]=get_object_value_from_graph(main_graph,value)
                    
    return format_results(formatted_results)

def execute_sparql_state_query(name:str,country:str):
    query="""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
        PREFIX dbo: <http://dbpedia.org/ontology/> 
        PREFIX dbr: <http://dbpedia.org/resource/> 
        PREFIX dbp: <http://dbpedia.org/property/>

         SELECT ?Label
         WHERE{ ?State a dbo:Location;
         dbp:name|foaf:name '%s'@en;
         rdfs:label ?Label;
         dbo:country ?Country.

         ?Country rdfs:label '%s'@en.
         FILTER ( LANG (?Label ) = 'en' )
         }
        """%(name,country)
    
    sparql.setQuery(query)
    sparql.setTimeout(1200000)
    try:
        ret = sparql.queryAndConvert()

        r =ret["results"]["bindings"][-1]
        return {"Label":r["Label"]["value"]}
    except:
        return {"Error":"Result not found"}
    
def get_state_details_from_db_pedia(name:str,country:str=None):      
    property_dict={"Name":[dbp.name,RDFS.label],
    "Country":dbo.country,
    "FoundingDate":[dbo.foundingDate,dbp.admittancedate],
    "Cities":dbp.city,
    "Elevation":[dbp.elevationM,dbo.elevation],
    "MaximumElevation":[dbp.elevationMaxM,dbo.maximumElevation],
    "MiniimumElevation":[dbo.minimumElevation,dbp.elevationMinM],
    "TotalPopulation":[dbp.populationTotal,dbo.populationTotal,dbp.pop],
    "TotalArea":[dbp.areaTotalKm,dbo.areaTotal],
    "TotalPopDate":[dbp.populationAsOf,dbo.populationAsOf],
    "TimeZone":[dbo.timeZone,dbp.timezone],
    "OtherName":[dbp.otherName,dbo.synonym],
    "Demonym":dbo.demonym,
    }
    list_objects=["Cities","Country","Demonym"]

    formatted_results={}
    
    if country:
        result=execute_sparql_state_query(name,country)
        if "Label" in result.keys():
            name=result["Label"]
        else:
            formatted_results["Error"]=["Result not found"]
            return format_results(formatted_results)
    
    name=name.replace(" ","_")
    url='http://dbpedia.org/resource/'+ name
    uri = URIRef(url)
    main_graph = Graph()
    main_graph.parse(uri)

    if (uri, RDF.type,dbo.Location) not in main_graph:
        formatted_results["Error"]=["Result not found"]
        return format_results(formatted_results)

    for key, value in property_dict.items():
        if type(value)==list:
            for i in value:
                formatted_results[key]=get_object_value_from_graph(main_graph,i)
                if len(formatted_results[key])>0:
                        break
        elif key in list_objects:
            formatted_results[key]=get_object_value_from_graph(main_graph,value,all_values=True)
        else:
            formatted_results[key]=get_object_value_from_graph(main_graph,value)
                    
    return format_results(formatted_results)

def execute_sparql_query_get_leader_names(name:str):
    try:
        name=name.replace(" ","_")
        query="""
            PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
            PREFIX dbo: <http://dbpedia.org/ontology/> 
            PREFIX dbr: <http://dbpedia.org/resource/> 
            PREFIX dbp: <http://dbpedia.org/property/>

            SELECT ?LeaderName
            WHERE{dbr:%s dbp:incumbent ?Incumbent.

            ?Incumbent rdfs:label ?LeaderName .
            FILTER ( LANG (?LeaderName) = 'en' )
            }
            """%(name)
        
        sparql.setQuery(query)
        sparql.setTimeout(1200000)
        ret = sparql.queryAndConvert()
        if ret["results"]["bindings"]:
            r =ret["results"]["bindings"][-1]
            return r["LeaderName"]["value"]
        else:
            return ""
    except:
        return ""

def get_country_details_from_db_pedia(name:str):      
    # Fields removed after using github data 
    # "Currency":dbo.currency,
    # "Capital":dbp.capital,
    # "TimeZone":[dbo.timeZone,dbp.timezone],

    property_dict={"Name":[dbp.name,RDFS.label],
    "FoundingDate":[dbo.foundingDate,dbp.admittancedate],   
    "GovernmentType":[dbo.governmentType,dbp.governmentType],
    "Language":dbo.language,
    "Elevation":[dbp.elevationM,dbo.elevation],
    "MaximumElevation":[dbp.elevationMaxM,dbo.maximumElevation],
    "MiniimumElevation":[dbo.minimumElevation,dbp.elevationMinM],
    "TotalPopulation":[dbp.populationTotal,dbo.populationTotal,dbp.pop],
    "TotalArea":[dbp.areaTotalKm,dbo.areaTotal],
    "TotalPopDate":[dbp.populationAsOf,dbo.populationAsOf],
    "LeaderTitle":dbp.leaderTitle,
    "NationalAnthem":dbp.nationalAnthem,
    "OtherName":[dbp.otherName,dbo.synonym],
    "Demonym":[dbo.demonym]
    }
    list_objects=["Language","Demonym","OtherName","Leader","LeaderTitle"]

    formatted_results={}
    
    name=name.replace(" ","_")
    url='http://dbpedia.org/resource/'+ name
    uri = URIRef(url)
    main_graph = Graph()
    main_graph.parse(uri)

    if (uri, RDF.type,schema.Country) not in main_graph:
        formatted_results["Error"]=["Result not found"]
        return format_results(formatted_results)

    for key, value in tqdm(property_dict.items()):
        if type(value)==list:
            for i in value:
                formatted_results[key]=get_object_value_from_graph(main_graph,i)
                if len(formatted_results[key])>0:
                        break
        elif key in list_objects:
            formatted_results[key]=get_object_value_from_graph(main_graph,value,all_values=True)
        else:
            formatted_results[key]=get_object_value_from_graph(main_graph,value)
    
    #get leader names
    formatted_results["LeaderName"]=[]
    for title in formatted_results["LeaderTitle"]:
          formatted_results["LeaderName"].append(execute_sparql_query_get_leader_names(title))
                    
    return format_results(formatted_results)
