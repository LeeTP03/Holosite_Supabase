from dotenv import load_dotenv

load_dotenv()

from googleapiclient.discovery import build
import urls
from streamupcoming import Upcoming
from streamlive import Live
from datetime import datetime
from streamarchiver import Archive

import os
from supabase import create_client
import json

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

api_service_name = os.environ.get("SERVICE_NAME")
api_version = os.environ.get("SERVICE_VER")
api_key = os.environ.get("SERVICE_KEY")

youtube = build(api_service_name, api_version, developerKey=api_key)

def getChannel(id):
    req = youtube.channels().list(
        part="contentDetails,id,snippet,statistics, status, brandingSettings", id=id
    )
    response = req.execute()
    ch_name = urls.name[urls.url.index(id)]

    with open(f"./channels/{ch_name}vid.json", "w") as file:
        jsonobj = json.dumps(response, indent=4)
        file.write(jsonobj)
        

def getData():
    lst = []
    
    for i in urls.url:
        ch_name = urls.name[urls.url.index(i)]
        print(ch_name)
        
        if ch_name == 'rushia':
            continue
        
        with open(f"./channels/{ch_name}vid.json", "r") as file:
            loader = json.load(file)
            item = loader['items'][0]
            ch_data = {
                "id" : item['id'],
                "title" : item['snippet']['title'],
                "description" : item['snippet']['description'],
                "customUrl" : item['snippet']['customUrl'],
                "thumbnail" : item['snippet']['thumbnails']['default']['url'],
                "viewCount" : item['statistics']['viewCount'],
                "subscriberCount" : item['statistics']['subscriberCount'],
                "videoCount" : item['statistics']['videoCount'],
                "channelThumbnail" : item['brandingSettings']['image']['bannerExternalUrl'] if 'image' in item['brandingSettings'] else "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAASwAAACoCAMAAABt9SM9AAAAA1BMVEWpqamhHEfZAAAAR0lEQVR4nO3BAQEAAACCIP+vbkhAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAO8GxYgAAb0jQ/cAAAAASUVORK5CYII=",
            }
        lst.append(ch_data)
        
    with open('./channelDetails', 'w') as file:
        res = {"channels" : lst}
        jsonobj = json.dumps(res, indent=4)
        file.write(jsonobj)

def writeChannelData():
    
    allIDs = supabase.table('Channels').select('id').execute()
    allIDs = [i['id'] for i in allIDs.data]
        
    with open('./channelDetails.json', 'r') as file:
        loader = json.load(file)
        
        for i in loader['channels']:
            if i['id'] in allIDs:
                data = supabase.table("Channels").update(i).eq("id", i['id'] ).execute()
                assert len(data.data) > 0
                    
            else:
                data = supabase.table("Channels").insert(i).execute()
                allIDs.append(i['id'])
                assert len(data.data) > 0  

writeChannelData()
