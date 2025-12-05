#!/usr/bin/env python3
"""
📤 EXPORT E-COMMERCE DATA TO CSV
Extract data from MongoDB and export to CSV for further analysis
"""

import pymongo
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Export ecommerce events from MongoDB to CSV"""
    logger.info("🚀 Starting MongoDB → CSV Export")
    
    # Connect to MongoDB
    client = pymongo.MongoClient('mongodb://admin:mongopass@localhost:27017/')
    db = client['kafka_events_db']
    
    # Query all e-commerce events
    logger.info("📥 Fetching data from MongoDB...")
    events = list(db.ecommerce.find())
    
    if not events:
        logger.warning("⚠️ No events found in ecommerce collection")
        return
    
    logger.info(f"✅ Retrieved {len(events)} events")
    
    # Convert to DataFrame
    df = pd.DataFrame(events)
    
    # Remove MongoDB _id column (not useful in CSV)
    if '_id' in df.columns:
        df = df.drop('_id', axis=1)
    
    # Generate filename with timestamp
    filename = f"../data/exports/ecommerce_events_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Save to CSV
    df.to_csv(filename, index=False)
    
    logger.info(f"✅ Exported {len(df)} events to {filename}")
    logger.info(f"📊 Columns: {list(df.columns)}")
    
    # Summary statistics
    if 'event_type' in df.columns:
        event_counts = df['event_type'].value_counts().to_dict()
        logger.info(f"📈 Event types distribution:")
        for event_type, count in event_counts.items():
            logger.info(f"   - {event_type}: {count}")
    
    # Revenue summary if purchases exist
    if 'amount' in df.columns and 'event_type' in df.columns:
        purchases = df[df['event_type'] == 'purchase']
        if not purchases.empty:
            total_revenue = purchases['amount'].sum()
            avg_order = purchases['amount'].mean()
            logger.info(f"💰 Revenue summary:")
            logger.info(f"   - Total revenue: ${total_revenue:.2f}")
            logger.info(f"   - Average order value: ${avg_order:.2f}")
            logger.info(f"   - Number of purchases: {len(purchases)}")
    
    logger.info(f"\n📁 File saved: {filename}")
    client.close()


if __name__ == "__main__":
    import os
    
    # Create exports directory if it doesn't exist
    os.makedirs("../data/exports", exist_ok=True)
    
    main()

