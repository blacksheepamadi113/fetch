import os
import json
import time
import ipaddress
from kafka import KafkaConsumer, KafkaProducer

BOOTSTRAP_SERVERS = os.getenv("BOOTSTRAP_SERVERS", "kafka:9092")
INPUT_TOPIC = os.getenv("INPUT_TOPIC", "user-login")
PROCESSED_TOPIC = os.getenv("PROCESSED_TOPIC", "user-login-processed")
ERROR_TOPIC = os.getenv("ERROR_TOPIC", "user-login-errors")

consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVERS,
    group_id="my-consumer-group",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode("utf-8"))
)

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVERS,
    value_serializer=lambda m: json.dumps(m).encode("utf-8")
)

def validate_and_transform(message):
    """
    Checks for mandatory fields (app_version, device_type, ip).
    Validates IP, then adds a processed_timestamp.
    Returns (is_valid, data).
    """
    if not message.get("app_version"):
        return False, {"reason": "missing_app_version", "original": message}
    if not message.get("device_type"):
        return False, {"reason": "missing_device_type", "original": message}
    if not message.get("ip"):
        return False, {"reason": "missing_ip", "original": message}

    # Validate IP
    try:
        ipaddress.ip_address(message["ip"])
    except ValueError:
        return False, {"reason": "invalid_ip", "original": message}

    message["processed_timestamp"] = int(time.time())
    return True, message

def main():
    print("Consumer started, waiting for messages...")
    try:
        while True:
            records = consumer.poll(timeout_ms=500)
            for _, batch in records.items():
                for record in batch:
                    data = record.value
                    is_valid, transformed = validate_and_transform(data)
                    if is_valid:
                        producer.send(PROCESSED_TOPIC, value=transformed)
                    else:
                        producer.send(ERROR_TOPIC, value=transformed)
    except KeyboardInterrupt:
        print("Consumer shutting down...")
    finally:
        consumer.close()
        producer.close()

if __name__ == "__main__":
    main()