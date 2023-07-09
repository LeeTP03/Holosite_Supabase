from dotenv import load_dotenv
load_dotenv()

import os
from supabase import create_client
import json

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# data = supabase.table("Live").update({ "id" : "GgmXKfDcEgs",
#         "title" : "【超探偵事件簿 レインコード】ダンロン制作陣による新作ゲーム！待ってた～！！！＃1【ホロライブ/夜空メル】"  ,
#         "channelTitle" : "Mel Channel 夜空メルチャンネル",
#         "channelThumbnail" : "https://yt3.ggpht.com/I6f2LiL5tEL4ECQhPNJPvBkrf6WrKAS8nheCpTyyQSNKzCwBL2XJSGKxBMc6UNcUr1AR7hrjXw=s88-c-k-c0x00ffffff-no-rj",
#         "thumbnail" : "https://i.ytimg.com/vi/GgmXKfDcEgs/mqdefault_live.jpg",
#         "duration" : "P0D",
#         "concurrentViewers" : "99999",
#         "actualStartTime" : '2023-07-08T09:00:24Z',
#         "scheduledStartTime" : "2023-07-08T09:00:00Z",
#         "videolink" : 'https://www.youtube.com/watch?v=GgmXKfDcEgs'
#         }).eq("id", "GgmXKfDcEgs" ).execute()
# assert len(data.data) > 0

# with open('./live.json', 'r') as file:
#     loader = json.load(file)
#     for i in loader['archive']:
        # data = supabase.table("archiveTable").insert(i).execute()
        # assert len(data.data) > 0
    
# with open('./currentlive.json', 'r') as file:
#     loader = json.load(file)
#     for i in loader['live']:
        # data = supabase.table("liveTable").insert(i).execute()
        # assert len(data.data) > 0
        
# with open('./currentupcoming.json', 'r') as file:
#     loader = json.load(file)
#     for i in loader['upcoming']:
#         data = supabase.table("upcomingTable").insert(i).execute()
#         assert len(data.data) > 0

data = supabase.table('Live').select("id").execute()
# Assert we pulled real data.
assert len(data.data) > 0

print(data.data[0]['id'])

# print(data.data)


# data = supabase.table('Live').insert().execute