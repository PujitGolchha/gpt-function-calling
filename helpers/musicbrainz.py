import musicbrainzngs as mbz
from . import music_brainz_app, music_brainz_contact, music_brainz_version

mbz.set_useragent(app=music_brainz_app,version=music_brainz_version,contact=music_brainz_contact)

#function to get track details from recording id
def gettrackdetailsfromrecordingid(id):
     keys = ['id', 'title', 'length']
     result=mbz.get_recording_by_id(id,includes="artists")["recording"]
     formatted_results= {x:result[x] for x in keys if x in result}
     if "artist-credit-phrase" in result:
          formatted_results["artists"]= result["artist-credit-phrase"]
     if "artist-credit" in result:
          formatted_results["artist_details"]=[]
          for relation in result["artist-credit"]:
               try:
                    formatted_results["artist_details"].append({"type":relation["artist"]["type"],"name":relation["artist"]["name"],"id":relation["artist"]["id"]})
               except:
                    continue        
     return formatted_results

#function to get track details from recording id
def gettrackdetailsfromrecordingidrefined(id):
    keys = ['id', 'title', 'length']
    result=mbz.get_recording_by_id(id,includes=["artists","artist-rels"])["recording"]
    formatted_results= {x:result[x] for x in keys if x in result}
    if "artist-credit-phrase" in result:
        formatted_results["artists"]= result["artist-credit-phrase"]
    if "artist-credit" in result:
        formatted_results["artist_details"]=[]
        for relation in result["artist-credit"]:
            try:
                formatted_results["artist_details"].append({"type":relation["artist"]["type"],"name":relation["artist"]["name"],"id":relation["artist"]["id"]})
            except:
                continue   
    if "artist-relation-list" in result:
        formatted_results["other_artist_details"]=[]
        for relation in result["artist-relation-list"]:
            try:
                formatted_results["other_artist_details"].append({"type":relation["type"],"name":relation["artist"]["name"],"id":relation["artist"]["id"]})
            except:
                continue      
    return formatted_results

#function to get all track details of an album from release id of an album
def gettracksfromreleaseid(id):
     #get the first release
     release=mbz.get_release_by_id(id,includes=["recordings"])["release"]["medium-list"][0]

     #get all tracks' details from recording(dict on its own) and track number from position
     tracks_details=[{**i["recording"],**{"track_number":i["position"]}} for i in release["track-list"]]

     for i in tracks_details:
          i["artists"]=gettrackdetailsfromrecordingid(i["id"])["artists"]
          
     return tracks_details

#function to get artist details from artist id
def getartistdetailsfromartistid(id):
     try:
          keys = ['id', 'name', 'type',"life-span"]

          result=mbz.get_artist_by_id(id,includes="artist-rels")["artist"]
          formatted_results= {x:result[x] for x in keys if x in result}
          if "area" in result:
               formatted_results["Main work Area"]=result["area"]["name"]
          if "begin-area" in result:
               formatted_results["begin-area"]=result["begin-area"]
          artists=[]
          if formatted_results["type"]=="Person" or formatted_results["type"]=="Character":
               if "country" in result:
                    formatted_results["country"]=result["country"]
               if "gender" in result:
                    formatted_results["gender"]=result["gender"]
          elif formatted_results["type"]=="Group" or formatted_results["type"]=="Orchestra" or formatted_results["type"]=="Choir":
               for artist_relation in result["artist-relation-list"]:
                    if artist_relation["direction"]=="backward" and artist_relation["type"]!= 'tribute':
                         details={"ID":artist_relation["artist"]["id"],"Name":artist_relation["artist"]["name"]}
                         if "attribute-list" in artist_relation:
                              details["Attribute"]=artist_relation["attribute-list"]
                         artists.append(details)

               formatted_results["artists"]=artists
     except:
          formatted_results={}
          formatted_results["Error"]="Result not found"
            
     return formatted_results

#function to get album details from release group id
def getalbumdetailsfromreleasegroupid(id):
    keys = ['id', 'title',"first-release-date"]
    #get the first release
    result=mbz.get_release_group_by_id(id,includes=["artist-credits"])["release-group"]
    #get all tracks' detailsi
    formatted_results= {x:result[x] for x in keys if x in result}
    formatted_results["artists"]= result["artist-credit-phrase"]
    return formatted_results

#function to get album details
def getalbumdetails(query:str,artist_name:str=None,track_name:str=None,strict=True,limit=1000):
     """Gets basic details of an album based on Musicbrainz data

     Args:
          query: Name of the album.
          artist_name: Name of an artist who contributed to the album. Defaults to None.
          track_name:  Name of a track part of the album. Defaults to None.

     Returns:
          dict: a dictionary conatining details about a track.
     """

     query_dict={"query":query,"strict":strict,"limit":limit,"type":"Album"}
     if artist_name!= None:
          query_dict["artist"]=artist_name
    
     
     results=mbz.search_release_groups(**query_dict)["release-group-list"]
     result_found=False
     for result in results:
          if result["title"]==query:
               if track_name!= None:
                    #loop through all releases
                    for release in result["release-list"]:
                         if(release["title"]==query and release["status"]!="Cancelled"):
                              tracks=[trackdetails['title'] for trackdetails in gettracksfromreleaseid(release["id"])]
                              if track_name in tracks:
                                   release_id=release["id"]
                                   result_found=True
                         if result_found==True:
                              break
               
               else:
                    for release in result["release-list"]:
                         if(release["title"]==query and release["status"]!="Cancelled"):
                              release_id=release["id"]
                              result_found=True
                         
                         if result_found==True:
                              break
          
          if result_found==True:
               break

     formatted_results={}
     if  result_found==True:
          formatted_results=getalbumdetailsfromreleasegroupid(result["id"])
          formatted_results["tracks"]=gettracksfromreleaseid(release_id)
          formatted_results["release_id"]=release_id
     else:
          
          formatted_results["Error"]="Result not found"
     
     return formatted_results

#function to get artist details
def getartistdetails(query:str,country:str=None,strict=True,limit=1000):
     """Gets basic details of an artist based on Musicbrainz data

     Args:
          query: Name of artist.
          country: Alpha-2 country code of the artist. Defaults to None.

     Returns:
          dict: a dictionary containing details about the artist.
     """
     
     query_dict={"query":query,"strict":strict,"limit":limit}
     if country!= None:
          query_dict["country"]=country
     
     result_found=False
     results=mbz.search_artists(**query_dict)["artist-list"]
     for result in results:
          if result["name"] in query:
               result_found=True
               break
     formatted_results={}
     if  result_found==True:
          formatted_results= getartistdetailsfromartistid(result["id"])
     else:
          formatted_results["Error"]="Result not found"
     
     return formatted_results

#function to get track details
def gettrackdetails(query:str,artist_name:str=None,country=None,album_name:str=None,strict=True,limit=1000):
     """Gets basic details of a track based on Musicbrainz data

     Args:
           query: Name of track.
           artist_name: Name of a artist who contributed to the track. Defaults to None.
           album_name:  Name of the album the track is part of. Defaults to None.

     Returns:
           dict: a dictionary conatining details about a track.
     """

     query_dict={"query":query,"strict":strict,"limit":limit,"type":"Soundtrack"}
     if country!= None:
        query_dict["country"]=country
     if artist_name!= None:
          query_dict["artist"]=artist_name

     result_found=False
     results=mbz.search_recordings(**query_dict)["recording-list"]
     
     for result in results:
          if result["title"]==query:
               #iterate over all releases if album name is specified
               if album_name!=None:
                    for release in result["release-list"]:
                         if(release["title"]==album_name and release["status"]!="Cancelled" and release["release-group"]["title"]==album_name):
                              result_found=True
                              release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                "release-group-title":release["release-group"]["title"],
                                                "release-group-type":release["release-group"]["primary-type"]}
                              break
                         elif(release["release-group"]["title"]==album_name):
                              result_found=True
                              release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                "release-group-title":release["release-group"]["title"],
                                                "release-group-type":release["release-group"]["primary-type"]}
                              break
               else:
                    release_details={"id":result["release-list"][0]["id"],"release-group-id":result["release-list"][0]["release-group"]["id"],
                                                "release-group-title":result["release-list"][0]["release-group"]["title"],
                                                "release-group-type":result["release-list"][0]["release-group"]["primary-type"]}
                    result_found=True
          
          if result_found==True:
                    break

     if result_found!=True:
          query_dict["type"]="Single"
     
          results=mbz.search_recordings(**query_dict)["recording-list"]
          for result in results:
               if result["title"]==query:
                    if album_name!=None:
                         for release in result["release-list"]:
                              if(release["title"]==album_name and release["status"]!="Cancelled" and release["release-group"]["title"]==album_name):
                                   result_found=True
                                   release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                  "release-group-title":release["release-group"]["title"],
                                                  "release-group-type":release["release-group"]["primary-type"]}
                                   break
                              elif(release["release-group"]["title"]==album_name):
                                   result_found=True
                                   release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                  "release-group-title":release["release-group"]["title"],
                                                  "release-group-type":release["release-group"]["primary-type"]}
                                   break
                    else:
                         release_details={"id":result["release-list"][0]["id"],"release-group-id":result["release-list"][0]["release-group"]["id"],
                                                  "release-group-title":result["release-list"][0]["release-group"]["title"],
                                                  "release-group-type":result["release-list"][0]["release-group"]["primary-type"]}
                         result_found=True
               
               if result_found==True:
                         break
          
     
     formatted_results={}
     if  result_found==True:
          formatted_results=gettrackdetailsfromrecordingid(result["id"])
          formatted_results["release_details"]= release_details
     else:
          formatted_results["Error"]="Result not found"
     
     return formatted_results

# updated function to get track details (only used for hard questions - includes roles and names of secondary artists related to the track)
def gettrackdetailsrefined(query:str,artist_name:str=None,country=None,album_name:str=None,strict=True,limit=1000):
     """Gets basic details of a track based on Musicbrainz data

     Args:
           query: Name of track.
           artist_name: Name of a artist who contributed to the track. Defaults to None.
           album_name:  Name of the album the track is part of. Defaults to None.

     Returns:
           dict: a dictionary conatining details about a track.
     """

     query_dict={"query":query,"strict":strict,"limit":limit,"type":"Soundtrack"}
     if country!= None:
        query_dict["country"]=country
     if artist_name!= None:
          query_dict["artist"]=artist_name

     result_found=False
     results=mbz.search_recordings(**query_dict)["recording-list"]
     
     for result in results:
          if result["title"] in query or query in result["title"]:
               #iterate over all releases if album name is specified
               if album_name!=None:
                    for release in result["release-list"]:
                         if(release["title"]==album_name and release["status"]!="Cancelled" and release["release-group"]["title"]==album_name):
                              result_found=True
                              release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                "release-group-title":release["release-group"]["title"],
                                                "release-group-type":release["release-group"]["primary-type"]}
                              break
                         elif(release["release-group"]["title"]==album_name):
                              result_found=True
                              release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                "release-group-title":release["release-group"]["title"],
                                                "release-group-type":release["release-group"]["primary-type"]}
                              break
               else:
                    release_details={"id":result["release-list"][0]["id"],"release-group-id":result["release-list"][0]["release-group"]["id"],
                                                "release-group-title":result["release-list"][0]["release-group"]["title"],
                                                "release-group-type":result["release-list"][0]["release-group"]["primary-type"]}
                    result_found=True
          
          if result_found==True:
                    break

     if result_found!=True:
          query_dict["type"]="Single"
     
          results=mbz.search_recordings(**query_dict)["recording-list"]
          for result in results:
               if result["title"] in query or query in result["title"]:
                    if album_name!=None:
                         for release in result["release-list"]:
                              if(release["title"]==album_name and release["status"]!="Cancelled" and release["release-group"]["title"]==album_name):
                                   result_found=True
                                   release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                  "release-group-title":release["release-group"]["title"],
                                                  "release-group-type":release["release-group"]["primary-type"]}
                                   break
                              elif(release["release-group"]["title"]==album_name):
                                   result_found=True
                                   release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                  "release-group-title":release["release-group"]["title"],
                                                  "release-group-type":release["release-group"]["primary-type"]}
                                   break
                    else:
                         release_details={"id":result["release-list"][0]["id"],"release-group-id":result["release-list"][0]["release-group"]["id"],
                                                  "release-group-title":result["release-list"][0]["release-group"]["title"],
                                                  "release-group-type":result["release-list"][0]["release-group"]["primary-type"]}
                         result_found=True
               
               if result_found==True:
                         break
     
     if result_found!=True:
          del query_dict["type"]
          results=mbz.search_recordings(**query_dict)["recording-list"]
          for result in results:
               if result["title"] in query or query in result["title"]:
                    if album_name!=None:
                         for release in result["release-list"]:
                              if(release["title"]==album_name and release["status"]!="Cancelled" and release["release-group"]["title"]==album_name):
                                   result_found=True
                                   release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                  "release-group-title":release["release-group"]["title"],
                                                  "release-group-type":release["release-group"]["primary-type"]}
                                   break
                              elif(release["release-group"]["title"]==album_name):
                                   result_found=True
                                   release_details={"id":release["id"],"release-group-id":release["release-group"]["id"],
                                                  "release-group-title":release["release-group"]["title"],
                                                  "release-group-type":release["release-group"]["primary-type"]}
                                   break
                    else:
                         release_details={"id":result["release-list"][0]["id"],"release-group-id":result["release-list"][0]["release-group"]["id"],
                                                  "release-group-title":result["release-list"][0]["release-group"]["title"],
                                                  "release-group-type":result["release-list"][0]["release-group"]["primary-type"]}
                         result_found=True
               
               if result_found==True:
                         break
          
     
     formatted_results={}
     if  result_found==True:
          formatted_results=gettrackdetailsfromrecordingidrefined(result["id"])
          formatted_results["release_details"]= release_details
     else:
          formatted_results["Error"]="Result not found"
     
     return formatted_results

# outdated function to get basic details of a music entity
def oldsearchdetails(query,entity_type,artist_name=None,track_name=None,country=None):
    query_dict={"query":query,"strict":True,"limit":1000}
    
    if country!= None:
        query_dict["country"]=country

    if entity_type=="artist":
        results=mbz.search_artists(**query_dict)["artist-list"]
        for result in results:
            if result["name"]==query:
                break
        keys = ['id', 'name', 'type', 'country']
        formatted_results= {x:result[x] for x in keys}
    else:
            if entity_type=="album": 
                if artist_name!= None:
                    query_dict["artist"]=artist_name
                if track_name!= None:
                    #track name can be searched using recording field
                    query_dict["release"]=track_name
                
                #search releases
                query_dict["type"]="Album"
                results=mbz.search_releases(**query_dict)["release-list"]
                result_found=False
                for result in results:
                    if result["title"]==query:
                        result_found=True
                        break
                
                # #search recordings
                # if result_found!=True:
                #     if track_name!= None:
                #     #track name can be searched using recording field
                #         query_dict["recording"]=track_name
                    
                #     results=mbz.search_recordings(**query_dict)["recording-list"]
                #     for result in results:
                #         if result["title"]==query:
                #             result_found=True
                #             break
                

                if  result_found==True:
                    keys = ['id', 'title', 'length']
                    formatted_results= {x:result[x] for x in keys if x in result}
                    formatted_results["artists"]= result["artist-credit-phrase"]
                    formatted_results["tracks"]=gettracksfromreleaseid( formatted_results["id"])
                else:
                    formatted_results["Error"]="Result not found"
            
            elif entity_type=="track":
                if artist_name!= None:
                    query_dict["artist"]=artist_name
                
                result_found=False
                query_dict["type"]="Soundtrack"
                results=mbz.search_recordings(**query_dict)["recording-list"]
                for result in results:
                    if result["title"]==query:
                        result_found=True
                        break
                
                if result_found!=True:
                    query_dict["type"]="Single"
                    
                    results=mbz.search_recordings(**query_dict)["recording-list"]
                    for result in results:
                        if result["title"]==query:
                            result_found=True
                            break

                if  result_found==True:
                    keys = ['id', 'title', 'length']
                    formatted_results= {x:result[x] for x in keys if x in result}
                    formatted_results["artists"]= result["artist-credit-phrase"]
                    formatted_results["release-id"]= result["release-list"][0]["id"]
                    formatted_results["release-group-id"]=result["release-list"][0]["release-group"]["id"]
                    formatted_results["release-group-title"]=result["release-list"][0]["release-group"]["title"]
                    formatted_results["release-group-type"]=result["release-list"][0]["release-group"]["primary-type"]
                else:
                    formatted_results["Error"]="Result not found"
                     
    return formatted_results

# function to get basic details of a music entity
def searchdetails(query:str,entity_type:str,artist_name:str=None,track_name:str=None,country:str=None,album_name:str=None):
    """Gets basic details of a music entity based on Musicbrainz data
    
    Args:
          query: Name of entity.
          entity_type: Type of entity. Must be one of ['artist', 'track', 'album'].
          artist_name: Name of an artist. Defaults to None.
          track_name: Name of any track in an album. Defaults to None.
          country: Alpha-2 country code. Defaults to None.
          album_name:  Name of an album. Defaults to None.

    Returns:
          dict: a dictionary conatining details about the music entity.
    """

    query_dict={"query":query,"strict":True,"limit":1000}

    if entity_type=="artist":
        query_dict["country"]=country
        formatted_results= getartistdetails(**query_dict)
    else:
            if entity_type=="album": 
                query_dict["artist_name"]=artist_name
                query_dict["track_name"]=track_name
                formatted_results=getalbumdetails(**query_dict)
   
            elif entity_type=="track":
                query_dict["country"]=country
                query_dict["artist_name"]=artist_name
                query_dict["album_name"]=album_name
                formatted_results=gettrackdetails(**query_dict)
    return formatted_results

# updated function to get basic details of a music entity (only used for hard questions)
def searchdetailsrefined(query:str,entity_type:str,artist_name:str=None,track_name:str=None,country:str=None,album_name:str=None):
    """Gets basic details of a music entity based on Musicbrainz data
    
    Args:
          query: Name of entity.
          entity_type: Type of entity. Must be one of ['artist', 'track', 'album'].
          artist_name: Name of an artist. Defaults to None.
          track_name: Name of any track in an album. Defaults to None.
          country: Alpha-2 country code. Defaults to None.
          album_name:  Name of an album. Defaults to None.

    Returns:
          dict: a dictionary conatining details about the music entity.
    """

    query_dict={"query":query,"strict":True,"limit":1000}

    if entity_type=="artist":
        query_dict["country"]=country
        formatted_results= getartistdetails(**query_dict)
    else:
            if entity_type=="album": 
                query_dict["artist_name"]=artist_name
                query_dict["track_name"]=track_name
                formatted_results=getalbumdetails(**query_dict)
   
            elif entity_type=="track":
                query_dict["country"]=country
                query_dict["artist_name"]=artist_name
                query_dict["album_name"]=album_name
                formatted_results=gettrackdetailsrefined(**query_dict)
    return formatted_results