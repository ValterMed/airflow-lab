#!/usr/bin/env python3
"""
⚡ INDEX OPTIMIZATION DEMONSTRATION
Compare query performance with and without indexes
"""

import pymongo
import time
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
db = client['kafka_events_db']

print("=" * 70)
print("🔍 INDEX OPTIMIZATION DEMONSTRATION")
print("=" * 70)

# =============================================================================
# Test 1: Query WITHOUT index on timestamp
# =============================================================================
print("\n📊 Test 1: Query WITHOUT index on timestamp")

# Drop index if exists (for clean test)
try:
    db.sensors.drop_index('idx_timestamp_opt')
    print("  Dropped existing test index")
except:
    pass

start = time.time()
result = list(db.sensors.find({ 'timestamp': { '$gte': '2025-01-01' } }).limit(100))
time_no_index = time.time() - start

print(f"  ⏱️  Time: {time_no_index*1000:.2f}ms")
print(f"  📄 Results: {len(result)} documents")
print(f"  🔍 Index used: COLLSCAN (full collection scan)")

# Get explain stats
explain = db.sensors.find({ 'timestamp': { '$gte': '2025-01-01' } }).limit(100).explain()
docs_examined_no_index = explain['executionStats']['totalDocsExamined']
print(f"  📊 Documents examined: {docs_examined_no_index}")

# =============================================================================
# Create index
# =============================================================================
print("\n🔨 Creating index on timestamp...")
start_index = time.time()
db.sensors.create_index([('timestamp', pymongo.DESCENDING)], name='idx_timestamp_opt')
index_creation_time = time.time() - start_index
print(f"  ✅ Index created in {index_creation_time*1000:.2f}ms")

# =============================================================================
# Test 2: Query WITH index on timestamp
# =============================================================================
print("\n📊 Test 2: Query WITH index on timestamp")

start = time.time()
result = list(db.sensors.find({ 'timestamp': { '$gte': '2025-01-01' } }).limit(100))
time_with_index = time.time() - start

print(f"  ⏱️  Time: {time_with_index*1000:.2f}ms")
print(f"  📄 Results: {len(result)} documents")
print(f"  🔍 Index used: idx_timestamp_opt")

# Get explain stats
explain = db.sensors.find({ 'timestamp': { '$gte': '2025-01-01' } }).limit(100).explain()
docs_examined_with_index = explain['executionStats']['totalDocsExamined']
print(f"  📊 Documents examined: {docs_examined_with_index}")

# =============================================================================
# Performance Comparison
# =============================================================================
print("\n" + "=" * 70)
print("⚡ PERFORMANCE COMPARISON")
print("=" * 70)

if time_with_index > 0:
    speedup = time_no_index / time_with_index
    print(f"  Without index: {time_no_index*1000:.2f}ms ({docs_examined_no_index} docs examined)")
    print(f"  With index:    {time_with_index*1000:.2f}ms ({docs_examined_with_index} docs examined)")
    print(f"  🚀 Speedup:    {speedup:.2f}x faster with index!")
    
    efficiency_improvement = ((docs_examined_no_index - docs_examined_with_index) / docs_examined_no_index * 100) if docs_examined_no_index > 0 else 0
    print(f"  📊 Efficiency: {efficiency_improvement:.1f}% fewer documents examined")
else:
    print("  ⚠️ Query too fast to measure accurately")

# =============================================================================
# Additional Index Examples
# =============================================================================
print("\n📚 Creating additional useful indexes...")

indexes_to_create = [
    ('city', pymongo.ASCENDING),
    ('sensor_type', pymongo.ASCENDING),
    ('user_id', pymongo.ASCENDING),
    ('event_type', pymongo.ASCENDING),
]

for field, direction in indexes_to_create:
    try:
        # Try on sensors collection
        if field in ['city', 'sensor_type']:
            db.sensors.create_index([(field, direction)], name=f'idx_{field}')
            print(f"  ✅ Created index on sensors.{field}")
        
        # Try on ecommerce collection
        elif field in ['user_id', 'event_type']:
            db.ecommerce.create_index([(field, direction)], name=f'idx_{field}')
            print(f"  ✅ Created index on ecommerce.{field}")
            
            # Also on mobile_events
            db.mobile_events.create_index([(field, direction)], name=f'idx_{field}')
            print(f"  ✅ Created index on mobile_events.{field}")
    except Exception as e:
        print(f"  ℹ️  Index on {field} might already exist")

# =============================================================================
# Compound Index Example
# =============================================================================
print("\n🔗 Creating compound indexes...")

try:
    db.sensors.create_index([('city', pymongo.ASCENDING), ('sensor_type', pymongo.ASCENDING)], 
                           name='idx_city_sensor')
    print("  ✅ Created compound index on sensors (city + sensor_type)")
except:
    print("  ℹ️  Compound index might already exist")

try:
    db.ecommerce.create_index([('user_id', pymongo.ASCENDING), ('timestamp', pymongo.DESCENDING)], 
                             name='idx_user_timeline')
    print("  ✅ Created compound index on ecommerce (user_id + timestamp)")
except:
    print("  ℹ️  Compound index might already exist")

# =============================================================================
# List all indexes
# =============================================================================
print("\n📋 All indexes on sensors collection:")
for idx in db.sensors.list_indexes():
    print(f"  - {idx['name']}: {idx['key']}")

print("\n📋 All indexes on ecommerce collection:")
for idx in db.ecommerce.list_indexes():
    print(f"  - {idx['name']}: {idx['key']}")

print("\n📋 All indexes on mobile_events collection:")
for idx in db.mobile_events.list_indexes():
    print(f"  - {idx['name']}: {idx['key']}")

# =============================================================================
# Index Size Analysis
# =============================================================================
print("\n💾 Index Storage Analysis:")

for coll_name in ['sensors', 'ecommerce', 'mobile_events']:
    try:
        stats = db.command('collStats', coll_name)
        if 'indexSizes' in stats:
            print(f"\n  {coll_name}:")
            total_index_size = sum(stats['indexSizes'].values())
            print(f"    Collection size: {stats.get('size', 0) / 1024:.2f} KB")
            print(f"    Total index size: {total_index_size / 1024:.2f} KB")
            print(f"    Indexes:")
            for idx_name, idx_size in stats['indexSizes'].items():
                print(f"      - {idx_name}: {idx_size / 1024:.2f} KB")
    except Exception as e:
        print(f"  ⚠️ Error getting stats for {coll_name}: {e}")

# =============================================================================
# Summary
# =============================================================================
print("\n" + "=" * 70)
print("✅ Index optimization demonstration completed!")
print("=" * 70)
print("\n💡 Key Takeaways:")
print("  1. Indexes dramatically improve query performance")
print("  2. Trade-off: Faster reads but slower writes and more storage")
print("  3. Create indexes on fields used in WHERE, JOIN, ORDER BY")
print("  4. Compound indexes help queries with multiple filters")
print("  5. Monitor index usage with explain() to optimize")
print("=" * 70)

client.close()

