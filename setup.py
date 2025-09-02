#!/usr/bin/env python
"""
Setup script for Hospitality Booking System.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_python():
    """Check Python version."""
    print("Checking Python version...")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("❌ Python 3.10+ required")
        return False
    
    print("✅ Python version OK")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Try running: pip install -r requirements.txt")
        return False

def check_firebase_config():
    """Check Firebase configuration."""
    print("\nChecking Firebase configuration...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Run: cp .env.example .env")
        return False
    
    # Check service account file
    from dotenv import load_dotenv
    load_dotenv()
    
    service_account = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not service_account:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set in .env")
        return False
    
    service_account_path = Path(service_account)
    if not service_account_path.exists():
        print(f"❌ Service account file not found: {service_account}")
        return False
    
    project_id = os.getenv("FIRESTORE_PROJECT_ID")
    if not project_id:
        print("❌ FIRESTORE_PROJECT_ID not set in .env")
        return False
    
    print(f"✅ Firebase configured for project: {project_id}")
    return True

def create_test_data():
    """Create sample data in Firestore."""
    print("\nWould you like to create sample data? (y/n): ", end="")
    response = input().strip().lower()
    
    if response != 'y':
        return
    
    try:
        import firebase_admin
        from firebase_admin import firestore, credentials
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Initialize Firebase
        cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        db = firestore.client()
        
        print("Creating sample properties...")
        
        # Sample properties
        properties = [
            {
                "property_id": "villa_miami_beach_001",
                "name": "Luxury Beach Villa Miami",
                "description": "Stunning beachfront villa with panoramic ocean views",
                "status": "active",
                "location": {
                    "address": "123 Ocean Drive",
                    "city": "Miami",
                    "country": "USA",
                    "lat": 25.7617,
                    "lng": -80.1918
                },
                "minimum_price": 450.0,
                "property_type": "villa",
                "guest_space": 8,
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "prices": {"weekday": 450, "weekend": 550},
                "amenities": ["pool", "beach_access", "wifi", "parking", "kitchen", "air_conditioning"],
                "images": ["villa1.jpg", "villa2.jpg"],
                "user_id": "host_001"
            },
            {
                "property_id": "apt_miami_downtown_002",
                "name": "Downtown Miami Luxury Apartment",
                "description": "Modern apartment in the heart of Miami",
                "status": "active",
                "location": {
                    "address": "456 Biscayne Blvd",
                    "city": "Miami",
                    "country": "USA",
                    "lat": 25.7749,
                    "lng": -80.1937
                },
                "minimum_price": 250.0,
                "property_type": "apartment",
                "guest_space": 4,
                "check_in_time": "15:00",
                "check_out_time": "11:00",
                "prices": {"weekday": 250, "weekend": 300},
                "amenities": ["wifi", "parking", "gym", "pool", "concierge"],
                "images": ["apt1.jpg", "apt2.jpg"],
                "user_id": "host_002"
            }
        ]
        
        for prop in properties:
            doc_ref = db.collection('properties').document(prop['property_id'])
            doc_ref.set(prop)
            print(f"  ✅ Created: {prop['name']}")
        
        # Sample user
        user = {
            "uid": "guest_001",
            "name": "John Doe",
            "email": "john@example.com",
            "role": "guest",
            "preferences": {},
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        user_ref = db.collection('users').document(user['uid'])
        user_ref.set(user)
        print(f"  ✅ Created test user: {user['name']}")
        
        print("\n✅ Sample data created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return False

def main():
    """Run setup process."""
    print("="*50)
    print("HOSPITALITY BOOKING SYSTEM - SETUP")
    print("="*50)
    
    # Check Python
    if not check_python():
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Check Firebase
    if check_firebase_config():
        create_test_data()
    else:
        print("\n⚠️  Please configure Firebase in .env file")
    
    print("\n" + "="*50)
    print("Setup complete! You can now run:")
    print("  python example_usage.py")
    print("="*50)

if __name__ == "__main__":
    main()