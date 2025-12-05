#!/usr/bin/env python3
"""
🛒 E-COMMERCE EVENT QUERIES - Python
Analyze user behavior and conversion funnels
"""

import pymongo
from pprint import pprint

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
db = client['kafka_events_db']

print("=" * 70)
print("🛒 E-COMMERCE ANALYTICS")
print("=" * 70)

# Query 1: User purchase funnel
print("\n📊 Query 1: Purchase Funnel - Events by Type")
pipeline = [
    { "$group": { "_id": "$event_type", "count": { "$sum": 1 } } },
    { "$sort": { "count": -1 } }
]
result = db.ecommerce.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}: {doc['count']} events")

# Query 2: Total revenue
print("\n💰 Query 2: Revenue Summary")
pipeline = [
    { "$match": { "event_type": "purchase" } },
    { "$group": { 
        "_id": None, 
        "total_revenue": { "$sum": "$amount" },
        "purchase_count": { "$sum": 1 },
        "avg_purchase": { "$avg": "$amount" }
    }}
]
result = list(db.ecommerce.aggregate(pipeline))
if result:
    doc = result[0]
    print(f"  Total Revenue: ${doc['total_revenue']:.2f}")
    print(f"  Total Purchases: {doc['purchase_count']}")
    print(f"  Average Order Value: ${doc['avg_purchase']:.2f}")
else:
    print("  No purchases yet")

# Query 3: Conversion rate analysis
print("\n📈 Query 3: Conversion Rate Analysis")
pipeline = [
    { "$group": { 
        "_id": None, 
        "total_views": { "$sum": { "$cond": [{ "$eq": ["$event_type", "product_view"] }, 1, 0] } },
        "cart_adds": { "$sum": { "$cond": [{ "$eq": ["$event_type", "add_to_cart"] }, 1, 0] } },
        "purchases": { "$sum": { "$cond": [{ "$eq": ["$event_type", "purchase"] }, 1, 0] } }
    }},
    { "$project": {
        "total_views": 1,
        "cart_adds": 1,
        "purchases": 1,
        "view_to_cart_rate": {
            "$cond": [
                { "$gt": ["$total_views", 0] },
                { "$multiply": [{ "$divide": ["$cart_adds", "$total_views"] }, 100] },
                0
            ]
        },
        "cart_to_purchase_rate": {
            "$cond": [
                { "$gt": ["$cart_adds", 0] },
                { "$multiply": [{ "$divide": ["$purchases", "$cart_adds"] }, 100] },
                0
            ]
        },
        "overall_conversion": {
            "$cond": [
                { "$gt": ["$total_views", 0] },
                { "$multiply": [{ "$divide": ["$purchases", "$total_views"] }, 100] },
                0
            ]
        }
    }}
]
result = list(db.ecommerce.aggregate(pipeline))
if result:
    doc = result[0]
    print(f"  Product Views: {doc['total_views']}")
    print(f"  Cart Additions: {doc['cart_adds']}")
    print(f"  Purchases: {doc['purchases']}")
    print(f"  View → Cart Rate: {doc['view_to_cart_rate']:.2f}%")
    print(f"  Cart → Purchase Rate: {doc['cart_to_purchase_rate']:.2f}%")
    print(f"  Overall Conversion: {doc['overall_conversion']:.2f}%")
else:
    print("  No data available")

# Query 4: Top 10 most viewed products
print("\n👁️ Query 4: Top 10 Most Viewed Products")
pipeline = [
    { "$match": { "event_type": "product_view" } },
    { "$group": { 
        "_id": "$product_name", 
        "views": { "$sum": 1 } 
    }},
    { "$sort": { "views": -1 } },
    { "$limit": 10 }
]
result = db.ecommerce.aggregate(pipeline)
for i, doc in enumerate(result, 1):
    print(f"  {i}. {doc['_id']}: {doc['views']} views")

# Query 5: Best-selling products by revenue
print("\n🏆 Query 5: Top 10 Products by Revenue")
pipeline = [
    { "$match": { "event_type": "purchase" } },
    { "$group": { 
        "_id": "$product_name", 
        "total_sales": { "$sum": "$amount" },
        "units_sold": { "$sum": 1 }
    }},
    { "$sort": { "total_sales": -1 } },
    { "$limit": 10 }
]
result = db.ecommerce.aggregate(pipeline)
for i, doc in enumerate(result, 1):
    print(f"  {i}. {doc['_id']}: ${doc['total_sales']:.2f} ({doc['units_sold']} units)")

# Query 6: Revenue by city
print("\n🌍 Query 6: Revenue by City")
pipeline = [
    { "$match": { "event_type": "purchase" } },
    { "$group": { 
        "_id": "$city", 
        "total_revenue": { "$sum": "$amount" },
        "purchase_count": { "$sum": 1 },
        "avg_order_value": { "$avg": "$amount" }
    }},
    { "$sort": { "total_revenue": -1 } }
]
result = db.ecommerce.aggregate(pipeline)
for doc in result:
    print(f"  {doc['_id']}:")
    print(f"    Revenue: ${doc['total_revenue']:.2f} | Orders: {doc['purchase_count']} | AOV: ${doc['avg_order_value']:.2f}")

# Query 7: Events by device type
print("\n📱 Query 7: Performance by Device Type")
pipeline = [
    { "$group": { 
        "_id": "$device_type", 
        "event_count": { "$sum": 1 },
        "purchases": { "$sum": { "$cond": [{ "$eq": ["$event_type", "purchase"] }, 1, 0] } }
    }},
    { "$project": {
        "device_type": "$_id",
        "event_count": 1,
        "purchases": 1,
        "conversion_rate": {
            "$cond": [
                { "$gt": ["$event_count", 0] },
                { "$multiply": [{ "$divide": ["$purchases", "$event_count"] }, 100] },
                0
            ]
        }
    }},
    { "$sort": { "event_count": -1 } }
]
result = db.ecommerce.aggregate(pipeline)
for doc in result:
    print(f"  {doc['device_type']}: {doc['event_count']} events | {doc['purchases']} purchases | {doc['conversion_rate']:.2f}% conversion")

# Query 8: Cart abandonment analysis
print("\n🛒 Query 8: Cart Abandonment")
total_users = db.ecommerce.distinct("user_id")
users_with_cart = db.ecommerce.distinct("user_id", { "event_type": "add_to_cart" })
users_with_purchase = db.ecommerce.distinct("user_id", { "event_type": "purchase" })

abandoned_users = len([u for u in users_with_cart if u not in users_with_purchase])

print(f"  Total unique users: {len(total_users)}")
print(f"  Users who added to cart: {len(users_with_cart)}")
print(f"  Users who purchased: {len(users_with_purchase)}")
print(f"  Cart abandonment: {abandoned_users} users ({abandoned_users/len(users_with_cart)*100:.1f}%)" if len(users_with_cart) > 0 else "  No cart data")

# Query 9: User journey example
print("\n👤 Query 9: Sample User Journey (First User)")
sample_user = db.ecommerce.find_one({}, { "user_id": 1 })
if sample_user:
    user_id = sample_user['user_id']
    print(f"  User: {user_id}")
    events = db.ecommerce.find({ "user_id": user_id }).sort("timestamp", 1).limit(10)
    for event in events:
        print(f"    {event['timestamp']} | {event['event_type']} | {event.get('product_name', 'N/A')}")
else:
    print("  No events yet")

# Query 10: Hourly purchase pattern
print("\n🕐 Query 10: Hourly Purchase Distribution")
pipeline = [
    { "$match": { "event_type": "purchase" } },
    {
        "$project": {
            "hour": {
                "$dateToString": {
                    "format": "%H",
                    "date": { "$dateFromString": { "dateString": "$timestamp" } }
                }
            },
            "amount": 1
        }
    },
    {
        "$group": {
            "_id": "$hour",
            "purchase_count": { "$sum": 1 },
            "revenue": { "$sum": "$amount" }
        }
    },
    { "$sort": { "_id": 1 } }
]
result = db.ecommerce.aggregate(pipeline)
for doc in result:
    print(f"  Hour {doc['_id']}:00 - {doc['purchase_count']} purchases | ${doc['revenue']:.2f}")

print("\n" + "=" * 70)
print("✅ E-commerce queries completed!")
print("=" * 70)

client.close()

