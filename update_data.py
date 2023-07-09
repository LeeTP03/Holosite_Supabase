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

class Updater():
    
    def __init__(self) -> None:
        self.upcoming = Upcoming()
        self.live = Live()
        self.archive = Archive()
        self.update_counter = 0
    
    def refresh_data(self):
        update_live = self.upcoming.checkLive()

        for i in update_live:
            self.live.add(i)

        archives = self.live.check_live()

        for i in archives:
            self.archive.add(i)

        self.live.write_to_file()
        self.upcoming.write_to_file()
        self.archive.write_to_file()
        
        uID = self.upcoming.idlist
        lID = self.live.idlist
    
        self.updateDatabase(uID, lID)

    def updateDatabase(self, upcomingId = None, liveId = None):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        supabase = create_client(url, key)
        
        liveRes = supabase.table('Live').select('*').execute()
        liveIdRes = [i['id'] for i in liveRes.data]
        
        with open('./currentlive.json', 'r') as file:
            loader = json.load(file)
            
            for i in loader['live']:
                if i['id'] in liveIdRes:
                    data = supabase.table("Live").update(i).eq("id", i['id'] ).execute()
                    assert len(data.data) > 0
                    
                else:
                    data = supabase.table("Live").insert(i).execute()
                    assert len(data.data) > 0
                    
        liveRes = supabase.table('Live').select('*').execute()
        liveIdRes = [i['id'] for i in liveRes.data]
        deleteLiveId = [i for i in liveIdRes if i not in liveId]
        
        for i in deleteLiveId:
            data = supabase.table("Live").delete().eq("id", i).execute()
            
        with open('./currentarchive.json', 'r') as file:
            loader = json.load(file)
            
            archiveIdRes = supabase.table('Archive').select('id').execute()
            archiveIdRes = [i['id'] for i in archiveIdRes.data]
                            
            for i in loader['archive']:
                if i['id'] in archiveIdRes:
                    break
                else:
                    data = supabase.table("Archive").insert(i).execute()
                    assert len(data.data) > 0
                    
        upcomingRes = supabase.table('Upcoming').select('id').execute()
        upcomingIdRes = [i['id'] for i in upcomingRes.data]
        
        with open('./currentupcoming.json', 'r') as file:
            loader = json.load(file)
            
            for i in loader['upcoming']:
                if i['id'] in upcomingIdRes:
                    continue
                else:
                    data = supabase.table("Upcoming").insert(i).execute()
                    assert len(data.data) > 0
                    
        upcomingRes = supabase.table('Upcoming').select('id').execute()
        upcomingIdRes = [i['id'] for i in upcomingRes.data]
        deleteUpcomingId = [i for i in upcomingIdRes if i not in upcomingId]
        
        for i in deleteUpcomingId:
            data = supabase.table("Upcoming").delete().eq("id", i).execute()
            
        self.update_counter += 1
        
        print(f'updated {self.update_counter} times')
            
    def scheduler(self):
        schedule.every(10).minutes.do(self.refresh_data)
    
        while True:
            schedule.run_pending()
            time.sleep(1)
            
            
            

if __name__ == "__main__":
    update_adapter = Updater() 
    update_adapter.scheduler()
    # update_adapter.refresh_data()
#     schedule.every(10).minutes.do(update_adapter.refresh_data())
    
#     while True:
#         schedule.run_pending()
#         time.sleep(1)