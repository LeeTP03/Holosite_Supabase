from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv()

import json
from datetime import datetime
import urls
import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyDmDbzEfrKCfE0aYVsoxIDuzd_MwXijOP4"

class Live():
    
    def __init__(self) -> None:
        self.list = []
        self.new_data = []
        self.idlist = []
        self.load_data()
        self.youtube = build(api_service_name, api_version, developerKey=api_key)
    
    def load_data(self):
        with open('./currentlive.json', 'r') as file:
            loader = json.load(file)
            self.list = loader["live"]
            
        for i in self.list:
            self.idlist.append(i['id'])
    
    def add(self, item):
        if item['id'] in self.idlist:
            return

        if 'actualEndTIme' in item:
            return item
        
        self.new_data.append(item)
        self.idlist.append(item['id'])
        
    def check_live(self):
        archivelist = []
        
        for i in self.list:
            id = i['id']
            response = self.getVideoInfo(id)
        
            if response is None:
                continue
            
            elif response['type'] == 'Live':
                self.list[self.list.index(i)] = response
            
            elif response['type'] == 'Archive':
                self.list.remove(i)
                self.idlist.remove(id)
                archivelist.append(response)

        return archivelist
    
    def getVideoInfo(self, id):
        req = self.youtube.videos().list(
            part="liveStreamingDetails,contentDetails, id, snippet, statistics, status",
            id=id,
        )

        response = req.execute()
        items = response["items"]

        if len(items) == 0:
            return None

        ch_id = items[0]["snippet"]["channelId"]
        ch_name = urls.name[urls.url.index(ch_id)]

        lst = {}

        if "liveStreamingDetails" not in items[0]:
            return None

        with open(f"./channels/{ch_name}vid.json", "r") as file:
            loader = json.load(file)

            link = "https://www.youtube.com/watch?v=" + id
            if "concurrentViewers" in items[0]["liveStreamingDetails"]:
                live_vid_json = {
                    "id": id,
                    "type": "Live",
                    "title": items[0]["snippet"]["title"],
                    "channelTitle": items[0]["snippet"]["channelTitle"],
                    "channelThumbnail": loader["items"][0]["snippet"]["thumbnails"][
                        "default"
                    ]["url"],
                    "thumbnail": items[0]["snippet"]["thumbnails"]["medium"]["url"],
                    "duration": items[0]["contentDetails"]["duration"],
                    "concurrentViewers": items[0]["liveStreamingDetails"][
                        "concurrentViewers"
                    ],
                    "actualStartTime": items[0]["liveStreamingDetails"]["actualStartTime"],
                    "scheduledStartTime": items[0]["liveStreamingDetails"][
                        "scheduledStartTime"
                    ],
                    "videolink": link,
                    "channelId": loader["items"][0]["id"],
                }
                lst = live_vid_json

            elif "actualEndTime" in items[0]["liveStreamingDetails"]:
                ended_vid_json = {
                    "id": id,
                    "type": "Archive",
                    "title": items[0]["snippet"]["title"],
                    "channelTitle": items[0]["snippet"]["channelTitle"],
                    "channelThumbnail": loader["items"][0]["snippet"]["thumbnails"][
                        "default"
                    ]["url"],
                    "thumbnail": items[0]["snippet"]["thumbnails"]["medium"]["url"],
                    "duration": items[0]["contentDetails"]["duration"],
                    "scheduledStartTime": items[0]["liveStreamingDetails"][
                        "scheduledStartTime"
                    ],
                    "actualStartTime": items[0]["liveStreamingDetails"]["actualStartTime"],
                    "actualEndTime": items[0]["liveStreamingDetails"]["actualEndTime"],
                    "videolink": link,
                    "channelId": loader["items"][0]["id"],
                }
                lst = ended_vid_json

            elif "actualStartTime" not in items[0]["liveStreamingDetails"]:
                ended_vid_json = {
                    "id": id,
                    "type": "Upcoming",
                    "title": items[0]["snippet"]["title"],
                    "channelTitle": items[0]["snippet"]["channelTitle"],
                    "channelThumbnail": loader["items"][0]["snippet"]["thumbnails"][
                        "default"
                    ]["url"],
                    "thumbnail": items[0]["snippet"]["thumbnails"]["medium"]["url"],
                    "duration": items[0]["contentDetails"]["duration"],
                    "scheduledStartTime": items[0]["liveStreamingDetails"][
                        "scheduledStartTime"
                    ],
                    "videolink": link,
                    "channelId": loader["items"][0]["id"],
                }
                lst = ended_vid_json

        return lst
    
        
    def write_to_file(self):
        self.list += self.new_data
        
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        livelist = sorted(
            self.list, key=lambda x: datetime.strptime(x["actualStartTime"], date_format)
        )
        
        res = {"live" : livelist}
        
        with open('./currentlive.json', 'w') as file:
            jsonobj = json.dumps(res ,indent=4)
            file.write(jsonobj)