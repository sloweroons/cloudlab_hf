import redis
import time
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-> {current_time} - Worker thread initializing", flush=True)

r = redis.Redis(host='manual-redis-service', port=6379, decode_responses=True, password='adminpass')

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-> {current_time} - Attempting connection with in-memory Redis database", flush=True)
while True:
    try:
        if r.ping():
            break
    except redis.exceptions.ConnectionError:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"-- # {current_time} - Redis offline, waiting... ", flush=True)
        time.sleep(2)

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-- # {current_time} Redis online", flush=True)
print(f"-> {current_time} - Fetching Redis in-memory database", flush=True)
try:
    all_keys = r.keys('*')
    if not all_keys:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"-- # {current_time} - No previous uploads found", flush=True)
    else:
        for filename in all_keys:
            description_and_text = r.get(filename)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"-- # {current_time} - {filename};{description_and_text}")
except Exception as e:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"-- # {current_time} -  Error fetching data: {e}", flush=True)

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-> {current_time} - enabling notifications", flush=True)

pubsub = r.pubsub()
pubsub.subscribe('operator_notifications')

for message in pubsub.listen():
    if message['type'] == 'message':
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"-- # {current_time} - received new OCR data: {message['data']}", flush=True)