import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from . import spotify_client_id,spotify_client_secret

# Initialize API
client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id,
                                                      client_secret=spotify_client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#function to get track details from release id of an album
def gettracksfromreleaseid(id):
    tracks_details=[]
    for track in sp.album_tracks(id)["items"]:
        tract_detail={"id":track["id"],"name":track["name"],"track_number":track["track_number"],"length":track["duration_ms"]}
        tracks_details.append(tract_detail)
    return tracks_details

#function to get artist details from artist id
def getartistdetailsfromartistid(id):
    keys = ['id', 'name', 'genres']
    result = sp.artist(id)
    formatted_results= {x:result[x] for x in keys}
    return formatted_results

#function to get album details from release group id
def getalbumdetailsfromreleasegroupid(id):
    keys = ['id', 'name',"release_date","genres"]
    #get the first release
    result=sp.album(id)
    #get all tracks' detail
    formatted_results= {x:result[x] for x in keys if x in result}
    formatted_results["artists"]=  [artist["name"] for artist in result["artists"]]
    return formatted_results

#function to get album details
def getalbumdetailsfromspotify(query:str,artist_name:str=None,track_name:str=None,limit=50):
    """Gets basic details based on Spotify data of an album, which includes the release date, artists and tracks part of the album. For each track the duration and its number is also returned. 

     Args:
          query: Name of the album.
          artist_name: Name of an artist who contributed to the album. Defaults to None.
          track_name:  Name of a track part of the album. Defaults to None.

     Returns:
          dict: a dictionary containing details about an album which includes the release date,
            artists and tracks part of the album. For each track the duration and its number is 
            also returned. 
    """

    album_name=query
    if artist_name!= None:
        query=query+' artist:' + artist_name
    

    query_dict={"q":query,"limit":limit,"type":"album","offset":0,"market":None}
    results=sp.search(**query_dict)["albums"]
    result_found=False
    for result in results["items"]:
        if result["name"]==album_name or album_name in result["name"]:
            if track_name!= None:       
                tracks=[trackdetails['name'] for trackdetails in gettracksfromreleaseid(result["id"])]
                if track_name in tracks:
                    result_found=True
                if result_found==True:
                    break

            else:
                result_found=True
                break
            
        if result_found==True:
            break

    formatted_results={}
    if  result_found==True:
        formatted_results=getalbumdetailsfromreleasegroupid(result["id"])
        formatted_results["tracks"]=gettracksfromreleaseid(result["id"])
        formatted_results["release_id"]=result["id"]
    else:
        formatted_results["Error"]="Result not found"
    return formatted_results

#function to get artist details
def getartistdetailsfromspotify(query:str,limit=50):
    """Gets basic details based on Spotify data of an artist, which includes the name and genres of an artist.

     Args:
          query: Name of artist.

     Returns:
          dict: a dictionary containing the name and genres of an artist.
    """

    artist_name=query
    query_dict={"q":query,"limit":50,"type":"artist","offset":0,"market":None}
    results=sp.search(**query_dict)["artists"]
    result_found=False
    for result in results["items"]:
        if result["name"]==artist_name:
            result_found=True
            break

    formatted_results={}
    if  result_found==True:
        formatted_results= getartistdetailsfromartistid(result["id"])
    else:
        formatted_results["Error"]="Result not found"
   
    return formatted_results

#function to get track details
def gettrackdetailsfromspotify(query:str,artist_name:str=None,limit=50, album_name:str=None):
    """Gets basic details based on Spotify data of a track, which includes the duration, explicity, artists and the album of a track. 

        Args:
            query: Name of track.
            artist_name: Name of a artist who contributed to the track. Defaults to None.
            album_name:  Name of the album the track is part of. Defaults to None.

        Returns:
            dict: a dictionary containing details about a track which includes the duration, explicity,
            artists and the album of a track.
    """
    
    track_name=query
    if artist_name!= None:
        query=query+' artist:' + artist_name
    if album_name!= None:
        query=query+' album:' + album_name

    query_dict={"q":query,"limit":limit,"type":"track","offset":0,"market":None}
    results=sp.search(**query_dict)["tracks"]

    result_found=False
    for result in results["items"]:
        if result["name"]==track_name:
            #iterate over all releases if album name is specified
            if album_name!=None:
                if (result["album"]["name"]==album_name):
                    result_found=True
                    release_details={"release-group-id":result["album"]["id"],
                                    "release-group-title":result["album"]["name"],
                                    "release-group-type":result["album"]["album_type"]}
                    break
            else:
                result_found=True
                release_details={"release-group-id":result["album"]["id"],
                                "release-group-title":result["album"]["name"],
                                "release-group-type":result["album"]["album_type"]}
                break
        
        if result_found==True:
            break

    formatted_results={}
    if  result_found==True:
            keys = ['id', 'name', 'duration_ms',"explicit"]
            formatted_results= {x:result[x] for x in keys if x in result}
            formatted_results["artists"]= [artist["name"] for artist in result["artists"]]
            formatted_results["release_details"]= release_details
    else:
        formatted_results["Error"]="Result not found"
    return formatted_results

#function to get basic details of a music entity
def searchdetailsfromspotify(query:str,entity_type:str,artist_name:str=None,track_name:str=None,album_name:str=None):
    """Gets basic details of a music entity based on Spotify data. Based on entity type, the details returned change.
    For an artist: the name and genre of the artist are included.
    For an album: the release date, artists and tracks part of the album are included. For each track the duration and its number is also returned. 
    For a track: the duration, explicity, artists and the album of a track are included.

    Args:
          query: Name of entity.
          entity_type: Type of entity. Must be one of ['artist', 'track', 'album'].
          artist_name: Name of an artist. Defaults to None.
          track_name: Name of any track in an album. Defaults to None.
          album_name:  Name of an album. Defaults to None.

    Returns:
          dict: a dictionary conatining details about the music entity.
    """

    query_dict={"query":query,"limit":50}

    if entity_type=="artist":
        formatted_results=getartistdetailsfromspotify(**query_dict)
    else:
            if entity_type=="album": 
                query_dict["artist_name"]=artist_name
                query_dict["track_name"]=track_name
                formatted_results=getalbumdetailsfromspotify(**query_dict)
   
            elif entity_type=="track":
                query_dict["artist_name"]=artist_name
                query_dict["album_name"]=album_name
                formatted_results=gettrackdetailsfromspotify(**query_dict)
    return formatted_results

#function to get track recommendations
def getrecommendationsfromspotify(artist_name:str=None,track_name:str=None, genre:str=None,limit:int=5):
    """Gets track recommendations based on the specified filters. For each recommended track its duration, explicity, artists and the album of the track is retured. Note: Atleast one of the filters must be specified.

    Args:
        artist_name: Name of an artist. Defaults to None 
        track_name: Name of a track. Defaults to None 
        genre: Name of a genre. Defaults to None 
        limit: No of recommedations.

    Returns:
        dict: dictionary containing details about the recommended tracks which include the duration, explicity,
            artists and the album of the tracks.
    """
    formatted_results={}
    if artist_name==None and track_name==None and genre==None:
       formatted_results["Error"]="Either one of the artist_name, track_name or genre has to be specified" 
    
    query_dict={}
    query_dict["limit"]=limit
    if artist_name!=None:
        query_dict["seed_artists"]=[getartistdetailsfromspotify(query=artist_name)["id"]]
    if track_name!=None:
        query_dict["seed_tracks"]=[gettrackdetailsfromspotify(query=track_name)["id"]]
    if genre!=None:
        if genre in sp.recommendation_genre_seeds()["genres"]:
            query_dict["seed_genres"]=[genre]
        else:
            formatted_results["Error"]="Cannot get recommendation for the specified genre"
    
    formatted_results["tracks"]=[]
    for track in sp.recommendations(**query_dict)["tracks"]:
        track_details=gettrackdetailsfromspotify(query=track["name"],album_name=track["album"]["name"],artist_name=track["artists"][0]["name"])
        formatted_results["tracks"].append(track_details)
    return formatted_results
