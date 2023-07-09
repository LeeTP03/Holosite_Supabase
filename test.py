import schedule
import time
  
def func():
    print("Geeksforgeeks")
  
schedule.every(3).seconds.do(func)
  
while True:
    schedule.run_pending()
    time.sleep(1)