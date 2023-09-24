from main import Updater, VideoAPIFetch
import logging
from streamlive import Live
from streamupcoming import Upcoming
from streamarchiver import Archive

logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)

liveData = Live()
upcomingData = Upcoming()
archiveData = Archive()
updater_adapter = Updater(liveData, upcomingData, archiveData)
fetcher = VideoAPIFetch(liveData, upcomingData, archiveData)
# updater_adapter.scheduler()
fetcher.refresh_videos()
updater_adapter.refresh_data()
