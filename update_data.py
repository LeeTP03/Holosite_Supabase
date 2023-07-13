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


class Updater:
    def __init__(self) -> None:
        self.upcoming = Upcoming()
        self.live = Live()
        self.archive = Archive()
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

        self.upcoming = Upcoming()
        self.live = Live()
        self.archive = Archive()

        self.newupdateDatabase()
        
        now = datetime.now()

        current_time = now.strftime("%H:%M:%S")
        print("Last updated at", current_time)

    def scheduler(self):
        self.refresh_data()
        schedule.every(10).minutes.do(self.refresh_data)

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


if __name__ == "__main__":
    update_adapter = Updater()
    update_adapter.scheduler()
    # update_adapter.refresh_data()
