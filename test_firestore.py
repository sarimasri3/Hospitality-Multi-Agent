#!/usr/bin/env python
"""
Test Firestore connection and basic operations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def test_firestore_connection():
    """Test connection to Firestore."""
    print("="*50)
    print("TESTING FIRESTORE CONNECTION")
    print("="*50)
    
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get configuration
        project_id = os.getenv('FIRESTORE_PROJECT_ID')
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        print(f"\n1. Configuration:")
        print(f"   Project ID: {project_id}")
        print(f"   Credentials: {cred_path}")
        
        # Check if credentials file exists
        if not Path(cred_path).exists():
            print(f"   ❌ Credentials file not found: {cred_path}")
            return False
        
        print("   ✅ Credentials file found")
        
        # Initialize Firebase
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        print("\n2. Initializing Firebase...")
        
        # Check if already initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            print("   ✅ Firebase initialized")
        else:
            print("   ℹ️  Firebase already initialized")
        
        # Get Firestore client
        db = firestore.client()
        print("   ✅ Firestore client created")
        
        # Test write operation
        print("\n3. Testing write operation...")
        test_doc = {
            "test_field": "Hello from Hospitality Booking System",
            "timestamp": datetime.now().isoformat(),
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        doc_ref = db.collection('test_collection').document('test_doc')
        doc_ref.set(test_doc)
        print("   ✅ Test document written")
        
        # Test read operation
        print("\n4. Testing read operation...")
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            print(f"   ✅ Document read: {data['test_field']}")
        else:
            print("   ❌ Document not found")
        
        # List collections
        print("\n5. Checking collections...")
        collections = db.collections()
        collection_names = [c.id for c in collections]
        print(f"   Found {len(collection_names)} collections:")
        for name in collection_names[:5]:  # Show first 5
            print(f"   - {name}")
        
        # Check for hospitality collections
        print("\n6. Checking hospitality collections...")
        expected = ['users', 'properties', 'bookings']
        for collection in expected:
            try:
                # Try to get first document
                docs = db.collection(collection).limit(1).get()
                if docs:
                    print(f"   ✅ {collection}: {len(list(docs))} document(s)")
                else:
                    print(f"   ⚠️  {collection}: empty")
            except Exception as e:
                print(f"   ⚠️  {collection}: not found")
        
        # Clean up test document
        print("\n7. Cleaning up...")
        doc_ref.delete()
        print("   ✅ Test document deleted")
        
        print("\n" + "="*50)
        print("✅ FIRESTORE CONNECTION SUCCESSFUL")
        print("="*50)
        return True
        
    except ImportError as e:
        print(f"\n❌ Missing dependency: {e}")
        print("Run: pip install firebase-admin python-dotenv")
        return False
        
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check that service-account.json exists")
        print("2. Verify FIRESTORE_PROJECT_ID matches your Firebase project")
        print("3. Ensure service account has Firestore permissions")
        return False


def create_sample_data():
    """Create sample data for testing."""
    print("\n" + "="*50)
    print("CREATING SAMPLE DATA")
    print("="*50)
    
    try:
        from dotenv import load_dotenv
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        load_dotenv()
        
        # Initialize if needed
        if not firebase_admin._apps:
            cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        
        # Create sample properties
        print("\n1. Creating properties...")
        properties = [
            {
                "property_id": "villa_miami_001",
                "name": "Oceanfront Villa Miami Beach",
                "description": "Luxurious 5-bedroom villa with private beach access",
                "status": "active",
                "location": {
                    "address": "1234 Ocean Drive",
                    "city": "Miami",
                    "country": "USA",
                    "lat": 25.7617,
                    "lng": -80.1918
                },
                "minimum_price": 500.0,
                "property_type": "villa",
                "guest_space": 10,
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "prices": {"weekday": 500, "weekend": 650},
                "amenities": [
                    "pool", "beach_access", "wifi", "parking", 
                    "kitchen", "air_conditioning", "hot_tub", "bbq"
                ],
                "images": [],
                "user_id": "host_001",
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
            },
            {
                "property_id": "apt_miami_002",
                "name": "Brickell City Centre Apartment",
                "description": "Modern 2-bedroom apartment with city views",
                "status": "active",
                "location": {
                    "address": "88 SW 7th Street",
                    "city": "Miami",
                    "country": "USA",
                    "lat": 25.7669,
                    "lng": -80.1932
                },
                "minimum_price": 200.0,
                "property_type": "apartment",
                "guest_space": 4,
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "prices": {"weekday": 200, "weekend": 250},
                "amenities": [
                    "wifi", "parking", "gym", "pool", 
                    "concierge", "air_conditioning"
                ],
                "images": [],
                "user_id": "host_002",
                "created_at": firestore.SERVER_TIMESTAMP,
                "updated_at": firestore.SERVER_TIMESTAMP
            }
        ]
        
        for prop in properties:
            db.collection('properties').document(prop['property_id']).set(prop)
            print(f"   ✅ Created: {prop['name']}")
        
        # Create sample users
        print("\n2. Creating users...")
        users = [
            {
                "uid": "guest_001",
                "name": "Sarah Johnson",
                "email": "sarah@example.com",
                "role": "guest",
                "phone": "+1234567890",
                "preferences": {
                    "preferred_cities": ["Miami"],
                    "favorite_amenities": ["pool", "wifi"]
                },
                "created_at": firestore.SERVER_TIMESTAMP
            },
            {
                "uid": "host_001",
                "name": "Property Manager LLC",
                "email": "host@example.com",
                "role": "host",
                "created_at": firestore.SERVER_TIMESTAMP
            }
        ]
        
        for user in users:
            db.collection('users').document(user['uid']).set(user)
            print(f"   ✅ Created: {user['name']} ({user['role']})")
        
        print("\n" + "="*50)
        print("✅ SAMPLE DATA CREATED")
        print("="*50)
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to create data: {e}")
        return False


def main():
    """Run Firestore tests."""
    # Test connection
    if test_firestore_connection():
        # Ask about sample data
        print("\nWould you like to create sample data? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y':
            create_sample_data()
        
        print("\n✅ Firestore is ready for use!")
        print("\nNext steps:")
        print("1. Run: python example_usage.py")
        print("2. Or start the orchestrator")
    else:
        print("\n❌ Please fix the connection issues above")


if __name__ == "__main__":
    main()