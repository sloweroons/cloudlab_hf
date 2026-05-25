import redis
import time

# A tájékoztató szöveg maradjon tiszta
print("Operator Notification Worker elindult, varakozas az uzenetekre...", flush=True)

# A jelszót kizárólag a redis.Redis-nek adjuk át!
r = redis.Redis(host='manual-redis-service', port=6379, decode_responses=True, password='adminpass')
pubsub = r.pubsub()
pubsub.subscribe('operator_notifications')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"[WORKER NOTIFICATION]: {message['data']}", flush=True)