import json
from datetime import datetime


class Upcoming():
    
    def __init__(self) -> None:
        self.list = []
        self.newlist = []
        self.idlist = []
        self.load_data()
    
    def load_data(self):
        with open('./currentupcoming.json', 'r') as file:
            loader = json.load(file)
            self.list = loader["upcoming"]
    
        for i in self.list:
            self.idlist.append(i['id'])
            
    def checkLive(self):
        from main import getVideoInfo
        live = []
        
        for i in self.list:
            id = i['id']
            response = getVideoInfo(id)
            
            if response is None:
                continue
            
            if 'actualStartTime' in response:
                self.list.remove(i)
                live.append(response)
        
        return live
            
        
    def add(self, item):
        if item['id'] not in self.idlist:
            self.newlist.append(item)
            self.idlist.append(item['id'])
        
    def write_to_file(self):
        
        self.list += self.newlist
        
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        upcominglist = sorted(
            self.list,
            key=lambda x: datetime.strptime(x["scheduledStartTime"], date_format),
        )
        
        res = {'upcoming' : upcominglist}
        with open('./currentupcoming.json', 'w') as file:
            jsonobj = json.dumps(res, indent=4)
            file.write(jsonobj)


