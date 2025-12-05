# Copy this code to: src/advanced_queries.py
#!/usr/bin/env python3
"""
🔍 ADVANCED MONGODB QUERIES
Demonstrate aggregation pipeline and query optimization
"""

import pymongo
from pprint import pprint
from datetime import datetime, timedelta

# Connect
client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
db = client['kafka_events_db']

print("="*70)
print("🔍 ADVANCED MONGODB ANALYTICS")
print("="*70)

# =============================================================================
# Query 1: Time-series analysis - Events per minute
# =============================================================================
print("\n📊 Query 1: Events per Minute (Last Hour)")
pipeline = [
    {
        '$project': {
            'minute': {
                '$dateToString': {
                    'format': '%Y-%m-%d %H:%M',
                    'date': { '$dateFromString': { 'dateString': '$timestamp' } }
                }
            }
        }
    },
    {
        '$group': {
            '_id': '$minute',
            'event_count': { '$sum': 1 }
        }
    },
    { '$sort': { '_id': -1 } },
    { '$limit': 10 }
]

result = list(db.sensors.aggregate(pipeline))
for doc in result:
    print(f"  {doc['_id']}: {doc['event_count']} events")

# =============================================================================
# Query 2: Geospatial - Find sensors near a location
# =============================================================================
print("\n🗺️ Query 2: Sensors Near CDMX (within 50km)")
result = db.sensors.find({
    'location': {
        '$near': {
            '$geometry': {
                'type': 'Point',
                'coordinates': [-99.1332, 19.4326]  # CDMX center
            },
            '$maxDistance': 50000  # 50km in meters
        }
    }
}).limit(5)

for doc in result:
    print(f"  {doc['sensor_id']} | {doc['city']} | {doc['sensor_type']}")

# =============================================================================
# Query 3: Multi-collection join (using $lookup)
# =============================================================================
print("\n🔗 Query 3: User Activity Summary (Ecommerce + Mobile)")
# Note: This requires both collections to have user_id
pipeline = [
    {
        '$group': {
            '_id': '$user_id',
            'ecommerce_events': { '$sum': 1 },
            'purchases': {
                '$sum': { '$cond': [{ '$eq': ['$event_type', 'purchase'] }, 1, 0] }
            },
            'total_spent': {
                '$sum': { '$cond': [{ '$eq': ['$event_type', 'purchase'] }, '$amount', 0] }
            }
        }
    },
    { '$sort': { 'total_spent': -1 } },
    { '$limit': 10 }
]

result = list(db.ecommerce.aggregate(pipeline))
for doc in result:
    print(f"  User: {doc['_id']} | Events: {doc['ecommerce_events']} | Purchases: {doc['purchases']} | Spent: ${doc['total_spent']:.2f}")

# =============================================================================
# Query 4: Text search (requires text index)
# =============================================================================
print("\n🔍 Query 4: Creating Text Index and Searching")
try:
    db.ecommerce.create_index([('product_name', pymongo.TEXT)])
    print("  ✅ Text index created on product_name")
except:
    print("  ⚠️ Text index already exists")

# Search for products containing "laptop"
result = db.ecommerce.find(
    { '$text': { '$search': 'laptop' } },
    { 'score': { '$meta': 'textScore' } }
).sort([('score', {'$meta': 'textScore'})]).limit(5)

print("  Products matching 'laptop':")
for doc in result:
    print(f"    {doc.get('product_name', 'N/A')} | User: {doc['user_id']}")

# =============================================================================
# Query 5: Performance analysis with explain()
# =============================================================================
print("\n⚡ Query 5: Query Performance Analysis")

query = { 'city': 'Ciudad de México', 'sensor_type': 'temperature' }
explain = db.sensors.find(query).explain()

print(f"  Execution time: {explain['executionStats']['executionTimeMillis']}ms")
print(f"  Documents examined: {explain['executionStats']['totalDocsExamined']}")
print(f"  Documents returned: {explain['executionStats']['nReturned']}")
print(f"  Index used: {explain['executionStats'].get('indexUsed', 'No index')}")

# =============================================================================
# Query 6: Complex aggregation - Cohort analysis
# =============================================================================
print("\n👥 Query 6: User Cohort Analysis (First Purchase Date)")
pipeline = [
    { '$match': { 'event_type': 'purchase' } },
    {
        '$group': {
            '_id': '$user_id',
            'first_purchase': { '$min': '$timestamp' },
            'last_purchase': { '$max': '$timestamp' },
            'total_purchases': { '$sum': 1 },
            'lifetime_value': { '$sum': '$amount' }
        }
    },
    {
        '$project': {
            'user_id': '$_id',
            'first_purchase': 1,
            'total_purchases': 1,
            'lifetime_value': 1,
            'cohort_month': {
                '$dateToString': {
                    'format': '%Y-%m',
                    'date': { '$dateFromString': { 'dateString': '$first_purchase' } }
                }
            }
        }
    },
    { '$sort': { 'lifetime_value': -1 } },
    { '$limit': 5 }
]

result = list(db.ecommerce.aggregate(pipeline))
print("  Top 5 users by lifetime value:")
for doc in result:
    print(f"    User: {doc['user_id']} | LTV: ${doc['lifetime_value']:.2f} | Purchases: {doc['total_purchases']}")

# =============================================================================
# Query 7: Data quality check
# =============================================================================
print("\n✅ Query 7: Data Quality Report")

total_sensors = db.sensors.count_documents({})
sensors_with_location = db.sensors.count_documents({ 'location': { '$exists': True } })
sensors_missing_value = db.sensors.count_documents({ 'value': { '$exists': False } })

print(f"  Total sensor documents: {total_sensors}")
print(f"  With geolocation: {sensors_with_location} ({sensors_with_location/total_sensors*100:.1f}%)")
print(f"  Missing value field: {sensors_missing_value} ({sensors_missing_value/total_sensors*100:.1f}%)")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "="*70)
print("✅ Advanced queries completed!")
print("="*70)

client.close()