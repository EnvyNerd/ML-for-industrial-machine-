import pandas as pd 
import numpy as np 
from datetime import datetime, timedelta
import random 

# Setting
num_machine = 20
num_records_per_machine = 100 # per machine
start_time = datetime.now()
time_interval = timedelta(minutes=5)

# Sensor Simulation ranges
def simulate_sensor_data():
    return {
        "temperature": round(np.random.normal(75, 5), 3), #Fahrenheit 
        "pressure": round(np.random.normal(30, 2), 2), #PSI
        "vibration": round(np.random.normal(0.5, 0.1), 3), #mm/s
        "rpm": random.randint(1000, 3000) #RPM
    }

# Generate data 
data = []

for machine_id in range(1, num_machine + 1):
    timestamp = start_time
    for _ in range(num_records_per_machine):
        sensor = simulate_sensor_data()
        data.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "machine_id": f"MCH-{machine_id:03}",
            "temperature": sensor["temperature"],
            "pressure": sensor["pressure"],
            "vibration": sensor["vibration"],
            "rpm": sensor["rpm"]
        })
        timestamp += timedelta(seconds=10)

# Save to Csv
df = pd.DataFrame(data)
df.to_csv("Machine_sensor_data.csv", index=False)

print("Sensor data for 20 minutes saved to 'Machine_sensor_data.csv'")