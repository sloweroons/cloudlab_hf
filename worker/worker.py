import redis
import time
from datetime import datetime

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-> worker thread initializing - {current_time}", flush=True)

r = redis.Redis(host='manual-redis-service', port=6379, decode_responses=True, password='adminpass')

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-> Attempting connection with in-memory Redis database - {current_time}", flush=True)
while True:
    try:
        if r.ping():
            break
    except redis.exceptions.ConnectionError:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"-- # Redis offline, waiting... - {current_time}", flush=True)
        time.sleep(2)

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-- # Redis online - {current_time}", flush=True)
print(f"-> Fetching Redis in-memory database - {current_time}", flush=True)
try:
    all_keys = r.keys('*')
    if not all_keys:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"-- # No previous uploads found - {current_time}", flush=True)
    else:
        for filename in all_keys:
            description_and_text = r.get(filename)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"-- #{filename};{description_and_text}")
except Exception as e:
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"-- # Error fetching data: {e} - {current_time}", flush=True)

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f"-> enabling notifications - {current_time}")

pubsub = r.pubsub()
pubsub.subscribe('operator_notifications')

for message in pubsub.listen():
    if message['type'] == 'message':
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"-- # received new OCR data: {message['data']} - {current_time}", flush=True)