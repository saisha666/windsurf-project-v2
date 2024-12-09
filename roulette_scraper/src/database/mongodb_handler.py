import motor.motor_asyncio
from typing import List, Dict
import logging
from datetime import datetime

class MongoDBHandler:
    def __init__(self, connection_string: str, database_name: str):
        self.logger = logging.getLogger(__name__)
        self.client = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
        self.db = self.client[database_name]
        
    async def insert_many(self, data: List[Dict]):
        """Insert multiple records into MongoDB"""
        try:
            # Add timestamp for when data was saved
            for record in data:
                record['saved_at'] = datetime.utcnow()
            
            # Insert into appropriate collection based on provider
            for provider in set(record['provider'] for record in data):
                provider_data = [r for r in data if r['provider'] == provider]
                collection = self.db[f"{provider}_data"]
                await collection.insert_many(provider_data)
                
        except Exception as e:
            self.logger.error(f"Error inserting data into MongoDB: {str(e)}")
            raise
    
    async def get_latest_numbers(self, provider: str, table_id: str, limit: int = 100) -> List[Dict]:
        """Get the latest numbers for a specific table"""
        try:
            collection = self.db[f"{provider}_data"]
            cursor = collection.find(
                {'table_id': table_id},
                {'number': 1, 'timestamp': 1, 'multiplier': 1, '_id': 0}
            ).sort('timestamp', -1).limit(limit)
            
            return await cursor.to_list(length=limit)
            
        except Exception as e:
            self.logger.error(f"Error retrieving data from MongoDB: {str(e)}")
            return []
    
    async def get_table_stats(self, provider: str, table_id: str) -> Dict:
        """Get statistics for a specific table"""
        try:
            collection = self.db[f"{provider}_data"]
            pipeline = [
                {'$match': {'table_id': table_id}},
                {'$group': {
                    '_id': None,
                    'total_spins': {'$sum': 1},
                    'unique_numbers': {'$addToSet': '$number'},
                    'avg_multiplier': {'$avg': '$multiplier'},
                    'last_spin': {'$last': '$timestamp'}
                }}
            ]
            
            result = await collection.aggregate(pipeline).to_list(length=1)
            return result[0] if result else {}
            
        except Exception as e:
            self.logger.error(f"Error getting table stats from MongoDB: {str(e)}")
            return {}
