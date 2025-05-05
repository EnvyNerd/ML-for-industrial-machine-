# mqtt_simulator.py
import paho.mqtt.client as mqtt
import json
import time
import random

client = mqtt.Client()
client.connect("test.mosquitto.org", 1883, 60)

while True:
    payload = {
        "machine_id": f"M{random.randint(1, 20)}",
        "temperature": round(random.uniform(70, 100), 2),
        "pressure": round(random.uniform(30, 60), 2),
        "vibration": round(random.uniform(0.1, 1.0), 2)
    }
    client.publish("factory/machine", json.dumps(payload))
    time.sleep(2)
