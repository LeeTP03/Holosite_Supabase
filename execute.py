from main import Updater
import logging
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

updater_adapter = Updater()
updater_adapter.scheduler()