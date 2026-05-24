import redis
import time

print("Operator Notification Worker elindult, varakozas az uzenetekre...", flush=True, password=None)

# Kapcsolódás a Kubernetes-en belüli Redis szervizhez
r = redis.Redis(host='manual-redis-service-service', port=6379, decode_responses=True)
pubsub = r.pubsub()
pubsub.subscribe('operator_notifications')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"[UZEMELTETOI ERTESITES]: {message['data']}", flush=True)