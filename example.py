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


def idRemake(id):
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


def makenew():
    lst = []

    with open("./currentarchive.json", "r") as file:
        loader = json.load(file)
        for i in loader["archive"]:
            lst.append(idRemake(i["id"]))

    with open("./currentarchive.json", "w") as file:
        res = {"archive": lst}
        jsonobj = json.dumps(res, indent=4)
        file.write(jsonobj)


def writeToDB():
    IdData = supabase.table("StreamData").select("id").execute()
    IdData = [i["id"] for i in IdData.data]

    with open("./newarchive.json", "r") as file:
        loader = json.load(file)
        for i in loader["archive"]:
            if i == None:
                continue

            if i["id"] in IdData:
                data = (
                    supabase.table("StreamData").update(i).eq("id", i["id"]).execute()
                )
                assert len(data.data) > 0

            else:
                data = supabase.table("StreamData").insert(i).execute()
                assert len(data.data) > 0
                IdData.append(i["id"])


makenew()
writeToDB()
