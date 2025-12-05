#!/usr/bin/env python3
"""
🔍 ADVANCED MONGODB QUERIES
Demonstrate aggregation pipeline and query optimization
"""

import pymongo
from pprint import pprint
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Connect
client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
db = client['kafka_events_db']

print("=" * 70)
print("🔍 ADVANCED MONGODB ANALYTICS")
print("=" * 70)

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

try:
    result = list(db.sensors.aggregate(pipeline))
    for doc in result:
        print(f"  {doc['_id']}: {doc['event_count']} events")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

# =============================================================================
# Query 2: Geospatial - Find sensors near a location
# =============================================================================
print("\n🗺️ Query 2: Sensors Near CDMX (within 50km)")
try:
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
except Exception as e:
    print(f"  ⚠️ Geospatial query requires 2dsphere index. Error: {e}")

# =============================================================================
# Query 3: User Activity Summary (Ecommerce)
# =============================================================================
print("\n🔗 Query 3: User Activity Summary (Top 10 by spending)")
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

try:
    result = list(db.ecommerce.aggregate(pipeline))
    for doc in result:
        print(f"  User: {doc['_id']} | Events: {doc['ecommerce_events']} | Purchases: {doc['purchases']} | Spent: ${doc['total_spent']:.2f}")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

# =============================================================================
# Query 4: Text search (requires text index)
# =============================================================================
print("\n🔍 Query 4: Text Search on Product Names")
try:
    # Create text index if doesn't exist
    db.ecommerce.create_index([('product_name', pymongo.TEXT)])
    print("  ✅ Text index created on product_name")
except Exception as e:
    print("  ⚠️ Text index already exists or error:", e)

# Search for products containing "laptop"
try:
    result = db.ecommerce.find(
        { '$text': { '$search': 'laptop' } },
        { 'score': { '$meta': 'textScore' } }
    ).sort([('score', {'$meta': 'textScore'})]).limit(5)

    print("  Products matching 'laptop':")
    for doc in result:
        print(f"    {doc.get('product_name', 'N/A')} | User: {doc['user_id']}")
except Exception as e:
    print(f"  ⚠️ No results or error: {e}")

# =============================================================================
# Query 5: Performance analysis with explain()
# =============================================================================
print("\n⚡ Query 5: Query Performance Analysis")

query = { 'city': 'Ciudad de México', 'sensor_type': 'temperature' }
try:
    explain = db.sensors.find(query).explain()

    print(f"  Execution time: {explain['executionStats']['executionTimeMillis']}ms")
    print(f"  Documents examined: {explain['executionStats']['totalDocsExamined']}")
    print(f"  Documents returned: {explain['executionStats']['nReturned']}")
    
    if 'indexName' in explain['executionStats'].get('executionStages', {}):
        print(f"  Index used: {explain['executionStats']['executionStages']['indexName']}")
    else:
        print(f"  Index used: COLLSCAN (no index)")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

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
            'cohort_week': {
                '$dateToString': {
                    'format': '%Y-W%U',
                    'date': { '$dateFromString': { 'dateString': '$first_purchase' } }
                }
            }
        }
    },
    {
        '$group': {
            '_id': '$cohort_week',
            'user_count': { '$sum': 1 },
            'avg_ltv': { '$avg': '$lifetime_value' }
        }
    },
    { '$sort': { '_id': -1 } },
    { '$limit': 5 }
]

try:
    result = list(db.ecommerce.aggregate(pipeline))
    print("  User cohorts by first purchase week:")
    for doc in result:
        print(f"    Week {doc['_id']}: {doc['user_count']} users | Avg LTV: ${doc['avg_ltv']:.2f}")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

# =============================================================================
# Query 7: Data quality check
# =============================================================================
print("\n✅ Query 7: Data Quality Report")

try:
    total_sensors = db.sensors.count_documents({})
    sensors_with_location = db.sensors.count_documents({ 'location': { '$exists': True } })
    sensors_missing_value = db.sensors.count_documents({ 'value': { '$exists': False } })

    print(f"  Total sensor documents: {total_sensors}")
    if total_sensors > 0:
        print(f"  With geolocation: {sensors_with_location} ({sensors_with_location/total_sensors*100:.1f}%)")
        print(f"  Missing value field: {sensors_missing_value} ({sensors_missing_value/total_sensors*100:.1f}%)")
    else:
        print(f"  ⚠️ No sensor documents found. Run producer first!")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

# =============================================================================
# Query 8: Mobile Crash Summary
# =============================================================================
print("\n📱 Query 8: Mobile Crash Summary")
pipeline = [
    { '$match': { 'event_type': 'crash' } },
    {
        '$group': {
            '_id': '$crash_reason',
            'count': { '$sum': 1 },
            'affected_users': { '$addToSet': '$user_id' }
        }
    },
    {
        '$project': {
            'crash_reason': '$_id',
            'crash_count': '$count',
            'unique_users': { '$size': '$affected_users' }
        }
    },
    { '$sort': { 'crash_count': -1 } },
    { '$limit': 5 }
]

try:
    result = list(db.mobile_events.aggregate(pipeline))
    if result:
        print("  Top crash reasons:")
        for doc in result:
            print(f"    {doc['crash_reason']}: {doc['crash_count']} crashes | {doc['unique_users']} users affected")
    else:
        print("  ℹ️ No crashes recorded yet")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

# =============================================================================
# Query 9: Collection Statistics
# =============================================================================
print("\n📊 Query 9: Collection Statistics")

collections = ['sensors', 'ecommerce', 'mobile_events']
for coll_name in collections:
    try:
        count = db[coll_name].count_documents({})
        print(f"  {coll_name}: {count} documents")
    except Exception as e:
        print(f"  {coll_name}: Error - {e}")

# =============================================================================
# Query 10: Conversion Funnel Analysis
# =============================================================================
print("\n🛒 Query 10: E-commerce Conversion Funnel")
pipeline = [
    {
        '$group': {
            '_id': None,
            'total_views': { '$sum': { '$cond': [{ '$eq': ['$event_type', 'product_view'] }, 1, 0] } },
            'cart_adds': { '$sum': { '$cond': [{ '$eq': ['$event_type', 'add_to_cart'] }, 1, 0] } },
            'purchases': { '$sum': { '$cond': [{ '$eq': ['$event_type', 'purchase'] }, 1, 0] } }
        }
    },
    {
        '$project': {
            'total_views': 1,
            'cart_adds': 1,
            'purchases': 1,
            'view_to_cart_rate': {
                '$cond': [
                    { '$gt': ['$total_views', 0] },
                    { '$multiply': [{ '$divide': ['$cart_adds', '$total_views'] }, 100] },
                    0
                ]
            },
            'cart_to_purchase_rate': {
                '$cond': [
                    { '$gt': ['$cart_adds', 0] },
                    { '$multiply': [{ '$divide': ['$purchases', '$cart_adds'] }, 100] },
                    0
                ]
            },
            'overall_conversion': {
                '$cond': [
                    { '$gt': ['$total_views', 0] },
                    { '$multiply': [{ '$divide': ['$purchases', '$total_views'] }, 100] },
                    0
                ]
            }
        }
    }
]

try:
    result = list(db.ecommerce.aggregate(pipeline))
    if result:
        doc = result[0]
        print(f"  Views: {doc['total_views']}")
        print(f"  Cart Adds: {doc['cart_adds']}")
        print(f"  Purchases: {doc['purchases']}")
        print(f"  View → Cart Rate: {doc['view_to_cart_rate']:.2f}%")
        print(f"  Cart → Purchase Rate: {doc['cart_to_purchase_rate']:.2f}%")
        print(f"  Overall Conversion: {doc['overall_conversion']:.2f}%")
    else:
        print("  ℹ️ No ecommerce events yet")
except Exception as e:
    print(f"  ⚠️ Error: {e}")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 70)
print("✅ Advanced queries completed!")
print("=" * 70)

client.close()

