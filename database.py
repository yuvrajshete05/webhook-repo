import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote_plus

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = 'github_events_db'
COLLECTION_NAME = 'events'


class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Verify connection
            self.client.admin.command('ping')
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]
            print("✓ Connected to MongoDB successfully")
            return True
        except ServerSelectionTimeoutError:
            print("✗ Failed to connect to MongoDB. Make sure MongoDB is running.")
            return False
        except Exception as e:
            print(f"✗ Error connecting to MongoDB: {str(e)}")
            return False
    
    def init_db(self):
        """Initialize database and create indexes"""
        if not self.connect():
            return False
        
        try:
            # Create indexes for better query performance
            self.collection.create_index('request_id', unique=True)
            self.collection.create_index('timestamp', background=True)
            print("✓ Database indexes created")
            return True
        except Exception as e:
            print(f"✗ Error initializing database: {str(e)}")
            return False
    
    def save_event(self, event):
        """Save an event to MongoDB"""
        try:
            # Add created_at timestamp
            event['created_at'] = datetime.utcnow()
            
            # Insert or update based on request_id
            result = self.collection.insert_one(event)
            print(f"✓ Event saved: {result.inserted_id}")
            return True
        except Exception as e:
            print(f"✗ Error saving event: {str(e)}")
            return False
    
    def get_events(self, limit=50):
        """Retrieve all events from MongoDB, sorted by most recent first"""
        try:
            # Query without excluding _id first, then process
            events = []
            cursor = self.collection.find({}).sort('timestamp', -1).limit(limit)
            
            for doc in cursor:
                # Remove _id field for JSON serialization
                doc.pop('_id', None)
                
                # Convert datetime objects to ISO format strings
                if isinstance(doc.get('created_at'), datetime):
                    doc['created_at'] = doc['created_at'].isoformat() + 'Z'
                
                events.append(doc)
            
            print(f"[DEBUG] Retrieved {len(events)} events from MongoDB")
            return events
        except Exception as e:
            print(f"✗ Error fetching events: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_event_count(self):
        """Get total number of events"""
        try:
            return self.collection.count_documents({})
        except Exception as e:
            print(f"✗ Error counting events: {str(e)}")
            return 0
    
    def clear_all_events(self):
        """Clear all events (for testing purposes)"""
        try:
            result = self.collection.delete_many({})
            print(f"✓ Deleted {result.deleted_count} events")
            return True
        except Exception as e:
            print(f"✗ Error clearing events: {str(e)}")
            return False


# Create global database instance
db = Database()


# Convenience functions
def save_event(event):
    """Save event to database"""
    return db.save_event(event)


def get_events(limit=50):
    """Get events from database"""
    return db.get_events(limit)
