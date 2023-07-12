import json
from datetime import datetime

class Archive():
    
    def __init__(self) -> None:
        self.list = []
        self.new_data = []
        self.load_data()
    
    def load_data(self):
        with open('./currentarchive.json', 'r') as file:
            loader = json.load(file)
            self.list = loader["archive"]
        
        self.idlist = []
        for i in self.list:
            self.idlist.append(i['id'])
    
    def add(self, item):
        if item['id'] in self.idlist:
            return
        self.new_data.append(item)
        self.idlist.append(item['id'])
                
    def write_to_file(self):
        self.list += self.new_data
        
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        
        archive = sorted(
            self.list,
            key=lambda x: datetime.strptime(x["actualEndTime"], date_format),
            reverse=True,
        )
        
        res = {"last_archive" : archive[len(self.new_data)]['id'] ,"archive" : archive}
        with open('./currentarchive.json', 'w') as file:
            jsonobj = json.dumps(res,indent=4)
            file.write(jsonobj)