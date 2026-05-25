import redis
import time

print("-> worker thread initializing", flush=True)

r = redis.Redis(host='manual-redis-service', port=6379, decode_responses=True, password='adminpass')

print("-> fetching Redis in-memory database", flush=True)
while True:
    try:
        if r.ping():
            break
    except redis.exceptions.ConnectionError:
        print("-- # Redis offline, waiting...", flush=True)
        time.sleep(2)
try:
    all_keys = r.keys('*')
    if not all_keys:
        print("-- # No previous uploads found.")
    else:
        for filename in all_keys:
            description_and_text = r.get(filename)
            print(f"-- #{filename};{description_and_text}")
except Exception as e:
    print(f"-- # Error fetching data: {e}")

print("-> enabling notifications")

pubsub = r.pubsub()
pubsub.subscribe('operator_notifications')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"-- # received new OCR data: {message['data']}")