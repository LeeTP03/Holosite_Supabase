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


api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyDmDbzEfrKCfE0aYVsoxIDuzd_MwXijOP4"

youtube = build(api_service_name, api_version, developerKey=api_key)

u = Upcoming()
live = Live()
archiver = Archive()

def getChannel(id):
    req = youtube.channels().list(
        part="contentDetails,id,snippet,statistics, status", id=id
    )
    response = req.execute()
    ch_name = urls.name[urls.url.index(id)]

    with open(f"./channels/{ch_name}vid.json", "w") as file:
        jsonobj = json.dumps(response, indent=4)
        file.write(jsonobj)


def getChannelActivities(id):
    req = youtube.activities().list(part="contentDetails,id,snippet", channelId=id)
    response = req.execute()
    ch_name = urls.name[urls.url.index(id)]

    with open(f"./activities/{ch_name}vid.json", "w") as file:
        jsonobj = json.dumps(response, indent=4)
        file.write(jsonobj)


def checkActivities(ch_name):
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
        info = getVideoInfo(i)
        lst2.append(info)

    livestreams = {"livestreams": lst2}

    with open(f"./livestreams/{ch_name}lives.json", "w") as file:
        jsonobj = json.dumps(livestreams, indent=4)
        file.write(jsonobj)


def getVideoInfo(id):
    req = youtube.videos().list(
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
            }
            lst = live_vid_json

        elif "actualEndTime" in items[0]["liveStreamingDetails"]:
            ended_vid_json = {
                "id": id,
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
            }
            lst = ended_vid_json

        elif "actualStartTime" not in items[0]["liveStreamingDetails"]:
            ended_vid_json = {
                "id": id,
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
            }
            lst = ended_vid_json

    with open(f"./video/{ch_name}vid.json", "w") as file:
        jsonobj = json.dumps(response, indent=4)
        file.write(jsonobj)

    return lst


def refresh_videos():
    for i in range(len(urls.url)):
        getChannelActivities(urls.url[i])
        checkActivities(urls.name[i])
        
    for i in urls.name:
        if i == "rushia":
            continue
        with open(f"./livestreams/{i}lives.json", "r") as file:
            loader = json.load(file)
            for j in loader["livestreams"]:
                if j != None:
                    if "concurrentViewers" in j:
                        live.add(j)
                    elif "actualEndTime" not in j:
                        u.add(j)


# def refresh_data():
#     update_live = u.checkLive()

#     for i in update_live:
#         live.add(i)

#     archives = live.check_live()

#     for i in archives:
#         archiver.add(i)

#     live.write_to_file()
#     u.write_to_file()
#     archiver.write_to_file()
    
#     uID = u.idlist
#     lID = live.idlist
    
#     updateDatabase(uID, lID)
#     # updateSiteData()


def updateSiteData():
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
        

    
if __name__ == "__main__":
    refresh_videos()
    # refresh_data()
    # updateDatabase(u.idlist, live.idlist)
