from googleapiclient.discovery import build
import json
import urls
from streamupcoming import Upcoming
from streamlive import Live
from datetime import datetime
from streamarchiver import Archive
from dotenv import load_dotenv
load_dotenv()
import os
from supabase import create_client
import time
import schedule

import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyDmDbzEfrKCfE0aYVsoxIDuzd_MwXijOP4"
youtube = build(api_service_name, api_version, developerKey=api_key)

class VideoAPIFetch():
    
    def __init__(self, live, upcoming, archive) -> None:
        self.u = upcoming
        self.live = live
        self.archiver = archive
        self.call_amount = 0

    def getChannel(self, id):
        req = youtube.channels().list(
            part="contentDetails,id,snippet,statistics, status", id=id
        )
        response = req.execute()
        ch_name = urls.name[urls.url.index(id)]

        with open(f"./channels/{ch_name}vid.json", "w") as file:
            jsonobj = json.dumps(response, indent=4)
            file.write(jsonobj)


    def getChannelActivities(self, id):
        req = youtube.activities().list(part="contentDetails,id,snippet", channelId=id)
        response = req.execute()
        self.call_amount += 1
        ch_name = urls.name[urls.url.index(id)]

        with open(f"./activities/{ch_name}vid.json", "w") as file:
            jsonobj = json.dumps(response, indent=4)
            file.write(jsonobj)


    def checkActivities(self, ch_name):
        lst = []
        with open(f"./activities/{ch_name}vid.json", "r") as file:
            loader = json.load(file)
            items = loader["items"]

            if loader["pageInfo"]["totalResults"] == 0:
                return

            for i in range(loader["pageInfo"]["resultsPerPage"]):
                if "upload" in items[i]["contentDetails"]:
                    lst.append(items[i]["contentDetails"]["upload"]["videoId"])

        lst2 = []
        for i in lst:
            info = self.getVideoInfo(i)
            lst2.append(info)
        
        livestreams = {"livestreams": lst2}

        with open(f"./livestreams/{ch_name}lives.json", "w") as file:
            jsonobj = json.dumps(livestreams, indent=4)
            file.write(jsonobj)


    def getVideoInfo(self, id):
        req = youtube.videos().list(
            part="liveStreamingDetails, contentDetails, id, snippet, statistics, status",
            id=id,
        )

        response = req.execute()
        self.call_amount += 1
        items = response["items"]

        
        if len(items) == 0:
            return None

        ch_id = items[0]["snippet"]["channelId"]
        ch_name = urls.name[urls.url.index(ch_id)]

        lst = {}
        
        if "liveStreamingDetails" not in items[0]:
            return None
        
        if "scheduledStartTime" not in items[0]["liveStreamingDetails"]:
            return None
        
        # if "actualStartTime" in items[0]["liveStreamingDetails"] and "actualEndTime" not in items[0]["liveStreamingDetails"] and "concurrentViewers" not in items[0]["liveStreamingDetails"]:
        #     return None

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
            else:
                return None

        return lst


    def refresh_videos(self):
        for i in range(len(urls.url)):
            self.getChannelActivities(urls.url[i])
            self.checkActivities(urls.name[i])
            
        for i in urls.name:
            if i == "rushia":
                continue
            with open(f"./livestreams/{i}lives.json", "r") as file:
                loader = json.load(file)
                for j in loader["livestreams"]:
                    if j != None:
                        if "concurrentViewers" in j:
                            self.live.add(j)
                        elif "actualEndTime" in j:
                            self.archiver.add(j)
                        else:
                            self.u.add(j)
                            
        self.live.write_to_file()
        self.u.write_to_file()
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("Videos last updated", current_time)


    def updateSiteData(self):
        with open("./livedata/streamLiveData.json", "r") as file:
            loader = json.load(file)
            livelist = loader["live"]

            date_format = "%Y-%m-%dT%H:%M:%SZ"
            livelist = sorted(
                livelist, key=lambda x: datetime.strptime(x["actualStartTime"], date_format)
            )

        with open("./livedata/streamUpcomingData.json", "r") as file:
            loader = json.load(file)
            upcominglist = loader["upcoming"]

            upcominglist = sorted(
                upcominglist,
                key=lambda x: datetime.strptime(x["scheduledStartTime"], date_format),
            )

        with open("./livedata/archive.json", "r") as file:
            loader = json.load(file)
            archive = loader["archive"]

            archive = sorted(
                archive,
                key=lambda x: datetime.strptime(x["actualEndTime"], date_format),
                reverse=True,
            )

        with open("../src/routes/livedata.js", "w") as file:
            livelist = json.dumps(livelist, indent=4)
            upcominglist = json.dumps(upcominglist, indent=4)
            string = (
                "let liveData ="
                + livelist
                + "\nlet upcomingData ="
                + upcominglist
                + "\nexport {liveData}\nexport {upcomingData}"
            )
            file.write(string)

        with open("../src/routes/archive/archive.js", "w") as file:
            archive = json.dumps(archive, indent=4)

            string = "let archive =" + archive + "\nexport {archive}"
            file.write(string)
        
class Updater:
    def __init__(self, live, upcoming, archive) -> None:
        self.upcoming = upcoming
        self.live = live
        self.archive = archive
        self.fetcher = VideoAPIFetch(live, upcoming, archive)
        self.update_counter = 0

    def refresh_data(self):
        update_live = self.upcoming.checkLive()
        archives = []

        for i in update_live:
            item = self.live.add(i)

            if item != None:
                archives.append(item)

        for i in archives:
            self.archive.add(i)

        archives = self.live.check_live()

        for i in archives:
            self.archive.add(i)

        self.live.write_to_file()
        self.upcoming.write_to_file()
        self.archive.write_to_file()

        # self.upcoming = Upcoming()
        # self.live = Live()
        # self.archive = Archive()

        self.newupdateDatabase()
        
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Last updated at", current_time)
        print("Activity reset call amount", self.fetcher.call_amount)
        print("Live call amount", self.live.call_amount)
        print("upcoming call amount", self.upcoming.call_amount)
        
        
    def scheduler(self):
        self.fetcher.refresh_videos()
        self.refresh_data()
        schedule.every(2).minutes.do(self.refresh_data)
        schedule.every(4).minutes.do(self.fetcher.refresh_videos)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def newupdateDatabase(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        supabase = create_client(url, key)

        allIDs = supabase.table("StreamData").select("id").execute()
        allIDs = [i["id"] for i in allIDs.data]

        with open("./currentupcoming.json", "r") as file:
            loader = json.load(file)

            for i in loader["upcoming"]:
                if i["id"] in allIDs:
                    data = (
                        supabase.table("StreamData")
                        .update(i)
                        .eq("id", i["id"])
                        .execute()
                    )
                    assert len(data.data) > 0

                else:
                    data = supabase.table("StreamData").insert(i).execute()
                    allIDs.append(i["id"])
                    assert len(data.data) > 0

        with open("./currentlive.json", "r") as file:
            loader = json.load(file)

            for i in loader["live"]:
                if i["id"] in allIDs:
                    data = ( 
                        supabase.table("StreamData")
                        .update(i)
                        .eq("id", i["id"])
                        .execute()
                    )
                    assert len(data.data) > 0

                else:
                    data = supabase.table("StreamData").insert(i).execute()
                    allIDs.append(i["id"])
                    assert len(data.data) > 0

        with open("./currentarchive.json", "r") as file:
            loader = json.load(file)

            for i in loader["archive"]:
                # if i['id'] == loader['last_archive']:
                #     break

                if i["id"] in allIDs:
                    data = (
                        supabase.table("StreamData")
                        .update(i)
                        .eq("id", i["id"])
                        .execute()
                    )
                    assert len(data.data) > 0

                else:
                    data = supabase.table("StreamData").insert(i).execute()
                    allIDs.append(i["id"])
                    assert len(data.data) > 0
    

