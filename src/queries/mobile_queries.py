#!/usr/bin/env python3
"""
📱 MOBILE ANALYTICS QUERIES - Python
Crash analytics and performance monitoring
"""

import pymongo
from pprint import pprint

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
db = client['kafka_events_db']

print("=" * 70)
print("📱 MOBILE APP ANALYTICS")
print("=" * 70)

# Query 1: Crash summary
print("\n🚨 Query 1: Crash Summary by Reason")
pipeline = [
    { "$match": { "event_type": "crash" } },
    { "$group": { 
        "_id": "$crash_reason", 
        "count": { "$sum": 1 },
        "affected_users": { "$addToSet": "$user_id" },
        "devices": { "$addToSet": "$device_model" }
    }},
    { "$project": {
        "crash_reason": "$_id",
        "crash_count": "$count",
        "unique_users": { "$size": "$affected_users" },
        "unique_devices": { "$size": "$devices" }
    }},
    { "$sort": { "crash_count": -1 } }
]
result = db.mobile_events.aggregate(pipeline)
for doc in result:
    print(f"  {doc['crash_reason']}: {doc['crash_count']} crashes | {doc['unique_users']} users | {doc['unique_devices']} devices")

# Query 2: Overall crash rate
print("\n📊 Query 2: Overall Crash Rate")
pipeline = [
    { "$group": {
        "_id": None,
        "total_events": { "$sum": 1 },
        "crashes": { "$sum": { "$cond": [{ "$eq": ["$event_type", "crash"] }, 1, 0] } }
    }},
    { "$project": {
        "total_events": 1,
        "crashes": 1,
        "crash_rate": {
            "$cond": [
                { "$gt": ["$total_events", 0] },
                { "$multiply": [{ "$divide": ["$crashes", "$total_events"] }, 100] },
                0
            ]
        }
    }}
]
result = list(db.mobile_events.aggregate(pipeline))
if result:
    doc = result[0]
    print(f"  Total Events: {doc['total_events']}")
    print(f"  Crashes: {doc['crashes']}")
    print(f"  Crash Rate: {doc['crash_rate']:.2f}%")
else:
    print("  No data available")

# Query 3: Crash rate by app version
print("\n📱 Query 3: Crash Rate by App Version")
pipeline = [
    { "$group": { 
        "_id": { "version": "$app_version", "event_type": "$event_type" },
        "count": { "$sum": 1 }
    }},
    { "$group": {
        "_id": "$_id.version",
        "total_events": { "$sum": "$count" },
        "crashes": { 
            "$sum": { "$cond": [{ "$eq": ["$_id.event_type", "crash"] }, "$count", 0] }
        }
    }},
    { "$project": {
        "version": "$_id",
        "total_events": 1,
        "crashes": 1,
        "crash_rate": {
            "$cond": [
                { "$gt": ["$total_events", 0] },
                { "$multiply": [{ "$divide": ["$crashes", "$total_events"] }, 100] },
                0
            ]
        },
        "stability_score": {
            "$subtract": [100, {
                "$cond": [
                    { "$gt": ["$total_events", 0] },
                    { "$multiply": [{ "$divide": ["$crashes", "$total_events"] }, 100] },
                    0
                ]
            }]
        }
    }},
    { "$sort": { "crash_rate": -1 } }
]
result = db.mobile_events.aggregate(pipeline)
for doc in result:
    print(f"  Version {doc['version']}: {doc['crashes']} crashes / {doc['total_events']} events = {doc['crash_rate']:.2f}% | Stability: {doc['stability_score']:.1f}%")

# Query 4: Crash rate by platform
print("\n📊 Query 4: Crash Rate by Platform (iOS vs Android)")
pipeline = [
    { "$group": { 
        "_id": { "platform": "$platform", "event_type": "$event_type" },
        "count": { "$sum": 1 }
    }},
    { "$group": {
        "_id": "$_id.platform",
        "total_events": { "$sum": "$count" },
        "crashes": { 
            "$sum": { "$cond": [{ "$eq": ["$_id.event_type", "crash"] }, "$count", 0] }
        }
    }},
    { "$project": {
        "platform": "$_id",
        "total_events": 1,
        "crashes": 1,
        "crash_rate": {
            "$cond": [
                { "$gt": ["$total_events", 0] },
                { "$multiply": [{ "$divide": ["$crashes", "$total_events"] }, 100] },
                0
            ]
        }
    }},
    { "$sort": { "crash_rate": -1 } }
]
result = db.mobile_events.aggregate(pipeline)
for doc in result:
    print(f"  {doc['platform']}: {doc['crashes']} crashes / {doc['total_events']} events = {doc['crash_rate']:.2f}%")

# Query 5: Average session duration
print("\n⏱️ Query 5: Average Session Duration")
pipeline = [
    { "$match": { "event_type": "session_end" } },
    { "$group": { 
        "_id": None, 
        "avg_duration": { "$avg": "$session_duration_sec" },
        "min_duration": { "$min": "$session_duration_sec" },
        "max_duration": { "$max": "$session_duration_sec" },
        "total_sessions": { "$sum": 1 }
    }}
]
result = list(db.mobile_events.aggregate(pipeline))
if result:
    doc = result[0]
    print(f"  Average: {doc['avg_duration']/60:.2f} minutes")
    print(f"  Min: {doc['min_duration']} seconds")
    print(f"  Max: {doc['max_duration']/60:.2f} minutes")
    print(f"  Total Sessions: {doc['total_sessions']}")
else:
    print("  No session data")

# Query 6: Session duration by platform
print("\n📱 Query 6: Session Duration by Platform")
pipeline = [
    { "$match": { "event_type": "session_end" } },
    { "$group": { 
        "_id": "$platform", 
        "avg_duration": { "$avg": "$session_duration_sec" },
        "session_count": { "$sum": 1 }
    }},
    { "$sort": { "avg_duration": -1 } }
]
result = db.mobile_events.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}: {doc['avg_duration']/60:.2f} min avg | {doc['session_count']} sessions")

# Query 7: Performance - Average load time by platform
print("\n⚡ Query 7: Performance by Platform")
pipeline = [
    { "$match": { "event_type": "performance" } },
    { "$group": { 
        "_id": "$platform", 
        "avg_load_time": { "$avg": "$load_time_ms" },
        "avg_memory": { "$avg": "$memory_mb" },
        "sample_count": { "$sum": 1 }
    }},
    { "$sort": { "avg_load_time": 1 } }  # Lower is better
]
result = db.mobile_events.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}:")
    print(f"    Avg Load Time: {doc['avg_load_time']:.0f}ms")
    print(f"    Avg Memory: {doc['avg_memory']:.0f}MB")
    print(f"    Samples: {doc['sample_count']}")

# Query 8: Most active users
print("\n👥 Query 8: Most Active Users (by session count)")
pipeline = [
    { "$match": { "event_type": "session_start" } },
    { "$group": {
        "_id": "$user_id",
        "session_count": { "$sum": 1 },
        "platforms": { "$addToSet": "$platform" }
    }},
    { "$sort": { "session_count": -1 } },
    { "$limit": 10 }
]
result = db.mobile_events.aggregate(pipeline)
for i, doc in enumerate(result, 1):
    print(f"  {i}. User {doc['_id']}: {doc['session_count']} sessions | Platforms: {', '.join(doc['platforms'])}")

# Query 9: Device distribution
print("\n📲 Query 9: Device Distribution")
pipeline = [
    { "$group": {
        "_id": {
            "platform": "$platform",
            "device_model": "$device_model"
        },
        "users": { "$addToSet": "$user_id" },
        "event_count": { "$sum": 1 }
    }},
    { "$project": {
        "platform": "$_id.platform",
        "device_model": "$_id.device_model",
        "unique_users": { "$size": "$users" },
        "event_count": 1
    }},
    { "$sort": { "unique_users": -1 } },
    { "$limit": 10 }
]
result = db.mobile_events.aggregate(pipeline)
for doc in result:
    print(f"  {doc['platform']} - {doc['device_model']}: {doc['unique_users']} users | {doc['event_count']} events")

# Query 10: App version adoption
print("\n📊 Query 10: App Version Adoption")
pipeline = [
    { "$group": {
        "_id": "$app_version",
        "users": { "$addToSet": "$user_id" },
        "events": { "$sum": 1 }
    }},
    { "$project": {
        "version": "$_id",
        "unique_users": { "$size": "$users" },
        "event_count": "$events"
    }},
    { "$sort": { "unique_users": -1 } }
]
result = db.mobile_events.aggregate(pipeline)
for doc in result:
    print(f"  Version {doc['version']}: {doc['unique_users']} users | {doc['event_count']} events")

print("\n" + "=" * 70)
print("✅ Mobile analytics queries completed!")
print("=" * 70)

client.close()

