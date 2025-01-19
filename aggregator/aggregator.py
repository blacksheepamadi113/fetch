import os
import json
import time
import redis
from kafka import KafkaConsumer

BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
PROCESSED_TOPIC = os.getenv("PROCESSED_TOPIC", "user-login-processed")
GROUP_ID = os.getenv("GROUP_ID", "aggregator-group")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Basic Kafka consumer to read from user-login-processed
consumer = KafkaConsumer(
    PROCESSED_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id=GROUP_ID,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

# Connect to Redis for storing aggregator counts
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def increment_count(device_type):
    key_name = f"{device_type.lower()}_count"
    return r.incr(key_name)

def get_counts():
    android_str = r.get("android_count")
    ios_str = r.get("ios_count")
    android_count = int(android_str) if android_str else 0
    ios_count = int(ios_str) if ios_str else 0
    return android_count, ios_count

def main():
    print(f"Aggregator started. Reading from {PROCESSED_TOPIC}...")
    last_print_time = time.time()
    try:
        while True:
            records = consumer.poll(timeout_ms=500)
            for _, batch in records.items():
                for record in batch:
                    data = record.value
                    device_type = data.get("device_type", "").lower()
                    if "android" in device_type:
                        increment_count("android")
                    elif "ios" in device_type:
                        increment_count("ios")

            # print updated counts every 5 seconds
            now = time.time()
            if now - last_print_time >= 5:
                android_count, ios_count = get_counts()
                print(f"Android: {android_count}, iOS: {ios_count}")
                last_print_time = now
    except KeyboardInterrupt:
        print("Aggregator shutting down...")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()