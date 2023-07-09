from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client
import json
from datetime import datetime

# url = os.environ.get("SUPABASE_URL")
# key = os.environ.get("SUPABASE_KEY")

# supabase = create_client(url, key)

class Live():
    
    def __init__(self) -> None:
        self.list = []
        self.new_data = []
        self.load_data()
    
    def load_data(self):
        
        # self.list = supabase.table('liveTable').select("*").execute()
        # self.list = self.list.data
        with open('./currentlive.json', 'r') as file:
            loader = json.load(file)
            self.list = loader["live"]
            
        self.idlist = []
        for i in self.list:
            self.idlist.append(i['id'])
    
    def add(self, item):
        if item['id'] in self.idlist:
            return
        self.new_data.append(item)
        self.idlist.append(item['id'])
        
    def check_live(self):
        from main import getVideoInfo
        removed = []
        
        for i in self.list:
            id = i['id']
            response = getVideoInfo(id)
        
            if response is None:
                continue
            
            if 'actualEndTime' in response:
                self.list.remove(i)
                removed.append(response)

        return removed
        
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