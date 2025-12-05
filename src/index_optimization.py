# Copy to: src/index_optimization.py
import pymongo
import time

client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
db = client['kafka_events_db']

print("🔍 INDEX OPTIMIZATION DEMONSTRATION\n")

# Query WITHOUT index
print("Test 1: Query WITHOUT index on timestamp")
start = time.time()
result = list(db.sensors.find({ 'timestamp': { '$gte': '2025-01-01' } }).limit(100))
time_no_index = time.time() - start
print(f"  Time: {time_no_index*1000:.2f}ms | Results: {len(result)}")

# Drop old index if exists to avoid conflict
print("\nPreparing index creation...")
try:
    db.sensors.drop_index('idx_timestamp_desc')
    print("  🗑️ Dropped old index: idx_timestamp_desc")
except:
    print("  ℹ️ No old index to drop")

# Create index
print("\nCreating index on timestamp...")
try:
    db.sensors.create_index([('timestamp', pymongo.DESCENDING)], name='idx_timestamp_opt')
    print("  ✅ Index created: idx_timestamp_opt")
except Exception as e:
    if "already exists" in str(e):
        print("  ⚠️ Index already exists (using existing one)")
    else:
        raise

# Query WITH index
print("\nTest 2: Query WITH index on timestamp")
start = time.time()
result = list(db.sensors.find({ 'timestamp': { '$gte': '2025-01-01' } }).limit(100))
time_with_index = time.time() - start
print(f"  Time: {time_with_index*1000:.2f}ms | Results: {len(result)}")

# Speedup
speedup = time_no_index / time_with_index if time_with_index > 0 else 0
print(f"\n⚡ Speedup: {speedup:.2f}x faster with index!")

# Show all indexes
print("\n📊 All indexes on sensors collection:")
for idx in db.sensors.list_indexes():
    print(f"  - {idx['name']}: {idx['key']}")

client.close()