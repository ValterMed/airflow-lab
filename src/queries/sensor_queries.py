#!/usr/bin/env python3
"""
🌆 SMART CITY SENSOR QUERIES - Python
Run analytical queries on sensor data in MongoDB
"""

import pymongo
from pprint import pprint

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
db = client['kafka_events_db']

print("=" * 70)
print("🌆 SMART CITY SENSOR ANALYTICS")
print("=" * 70)

# Query 1: Count all sensor documents
print("\n📊 Query 1: Total Sensor Documents")
count = db.sensors.count_documents({})
print(f"  Total sensors: {count}")

# Query 2: Find all sensors from a specific city
print("\n🏙️ Query 2: Sensors in Ciudad de México")
sensors = db.sensors.find({ "city": "Ciudad de México" }).limit(5)
for sensor in sensors:
    print(f"  {sensor['sensor_id']} | {sensor['sensor_type']} | Value: {sensor.get('value', 'N/A')}")

# Query 3: Find temperature sensors with value > 25°C
print("\n🌡️ Query 3: Hot Temperature Readings (> 25°C)")
hot_temps = db.sensors.find({
    "sensor_type": "temperature",
    "value": { "$gt": 25 }
}).limit(10)
for temp in hot_temps:
    print(f"  {temp['city']} | {temp['value']}°C | {temp['timestamp']}")

# Query 4: Count sensors by type
print("\n📈 Query 4: Sensor Count by Type")
pipeline = [
    { "$group": { "_id": "$sensor_type", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } }
]
result = db.sensors.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}: {doc['count']} sensors")

# Query 5: Count sensors by city
print("\n🌍 Query 5: Sensor Count by City")
pipeline = [
    { "$group": { "_id": "$city", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } }
]
result = db.sensors.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}: {doc['count']} sensors")

# Query 6: Average air quality by city
print("\n💨 Query 6: Average Air Quality by City")
pipeline = [
    { "$match": { "sensor_type": "air_quality" } },
    { "$group": { 
        "_id": "$city", 
        "avg_aqi": { "$avg": "$value" },
        "min_aqi": { "$min": "$value" },
        "max_aqi": { "$max": "$value" },
        "count": { "$sum": 1 }
    }},
    { "$sort": { "avg_aqi": -1 } }
]
result = db.sensors.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}:")
    print(f"    Avg: {doc['avg_aqi']:.1f} | Min: {doc['min_aqi']} | Max: {doc['max_aqi']} | Readings: {doc['count']}")

# Query 7: Most recent 10 sensor readings
print("\n🕐 Query 7: Most Recent Sensor Readings")
recent = db.sensors.find().sort("timestamp", -1).limit(10)
for sensor in recent:
    print(f"  {sensor['timestamp']} | {sensor['city']} | {sensor['sensor_type']}: {sensor.get('value', 'N/A')}")

# Query 8: Temperature statistics across all cities
print("\n📊 Query 8: Temperature Statistics")
pipeline = [
    { "$match": { "sensor_type": "temperature" } },
    { "$group": {
        "_id": None,
        "avg_temp": { "$avg": "$value" },
        "min_temp": { "$min": "$value" },
        "max_temp": { "$max": "$value" },
        "count": { "$sum": 1 }
    }}
]
result = list(db.sensors.aggregate(pipeline))
if result:
    doc = result[0]
    print(f"  Average: {doc['avg_temp']:.2f}°C")
    print(f"  Min: {doc['min_temp']:.2f}°C")
    print(f"  Max: {doc['max_temp']:.2f}°C")
    print(f"  Total readings: {doc['count']}")

# Query 9: Cities with air quality issues (AQI > 100)
print("\n⚠️ Query 9: Cities with Poor Air Quality (AQI > 100)")
pipeline = [
    { "$match": { 
        "sensor_type": "air_quality",
        "value": { "$gt": 100 }
    }},
    { "$group": {
        "_id": "$city",
        "dangerous_readings": { "$sum": 1 },
        "max_aqi": { "$max": "$value" }
    }},
    { "$sort": { "dangerous_readings": -1 } }
]
result = db.sensors.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}: {doc['dangerous_readings']} dangerous readings | Max AQI: {doc['max_aqi']}")

# Query 10: Data quality check
print("\n✅ Query 10: Data Quality Check")
total = db.sensors.count_documents({})
missing_value = db.sensors.count_documents({ "value": { "$exists": False } })
with_location = db.sensors.count_documents({ "location": { "$exists": True } })

print(f"  Total documents: {total}")
print(f"  Missing value: {missing_value} ({missing_value/total*100:.1f}%)" if total > 0 else "  No documents")
print(f"  With geolocation: {with_location} ({with_location/total*100:.1f}%)" if total > 0 else "  No documents")

print("\n" + "=" * 70)
print("✅ Sensor queries completed!")
print("=" * 70)

client.close()

