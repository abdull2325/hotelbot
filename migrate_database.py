#!/usr/bin/env python3
"""
Database Migration and Setup Script
This script migrates the database to the new schema and populates it with sample data.
"""

import os
import sys
from database import DatabaseConnection

def migrate_database():
    """Migrate database to new schema"""
    print("🔄 Starting database migration...")
    
    db = DatabaseConnection()
    if not db.connect():
        print("❌ Failed to connect to database!")
        return False
    
    print("✅ Connected to database successfully!")
    
    # Read and execute the migration script
    try:
        with open('schema_migration.sql', 'r') as f:
            migration_script = f.read()
        
        # Execute the migration in chunks
        statements = migration_script.split(';')
        for statement in statements:
            if statement.strip():
                try:
                    db.execute_update(statement + ';')
                    print(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    if "already exists" not in str(e) and "does not exist" not in str(e):
                        print(f"⚠️  Warning: {e}")
        
        # Fix trigger function
        print("🔧 Setting up trigger functions...")
        trigger_function = '''
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = CURRENT_TIMESTAMP;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        '''
        
        triggers = [
            'DROP TRIGGER IF EXISTS update_hotels_updated_at ON hotels;',
            'CREATE TRIGGER update_hotels_updated_at BEFORE UPDATE ON hotels FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            'DROP TRIGGER IF EXISTS update_hotel_rooms_updated_at ON hotel_rooms;',
            'CREATE TRIGGER update_hotel_rooms_updated_at BEFORE UPDATE ON hotel_rooms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            'DROP TRIGGER IF EXISTS update_bookings_updated_at ON bookings;',
            'CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();'
        ]
        
        db.execute_update(trigger_function)
        print("✅ Created trigger function")
        
        for trigger in triggers:
            db.execute_update(trigger)
            print(f"✅ Executed trigger: {trigger[:50]}...")
        
        print("✅ Database migration completed successfully!")
        
        # Check if data exists
        hotels = db.execute_query("SELECT COUNT(*) as count FROM hotels")
        hotel_count = hotels[0]['count'] if hotels else 0
        
        print(f"📊 Database contains {hotel_count} hotels")
        
        db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        db.disconnect()
        return False

def populate_additional_data():
    """Populate additional dummy data using the new script"""
    print("📊 Populating additional data...")
    
    try:
        from populate_data_new import populate_dummy_data
        populate_dummy_data()
        return True
    except Exception as e:
        print(f"❌ Failed to populate data: {e}")
        return False

def test_chatbot():
    """Test the chatbot with the new schema"""
    print("🤖 Testing chatbot with new schema...")
    
    try:
        from chatbot_langgraph import HotelBotLangGraph
        
        chatbot = HotelBotLangGraph()
        
        # Quick test
        response = chatbot.chat("Show me hotels in Lahore")
        if "Pearl Continental" in response:
            print("✅ Chatbot test passed!")
            return True
        else:
            print("❌ Chatbot test failed!")
            return False
            
    except Exception as e:
        print(f"❌ Chatbot test failed: {e}")
        return False

def main():
    """Main function to run the migration process"""
    print("🏨 HotelBot Database Migration Script")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage: python migrate_database.py [options]")
        print("Options:")
        print("  --help       Show this help message")
        print("  --migrate    Run database migration only")
        print("  --populate   Populate additional data only")
        print("  --test       Test chatbot only")
        print("  (no args)    Run full migration, population, and test")
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--migrate":
        migrate_database()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--populate":
        populate_additional_data()
        return
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_chatbot()
        return
    
    # Run full process
    print("🚀 Starting full migration process...")
    
    # Step 1: Migrate database
    if not migrate_database():
        print("❌ Migration failed. Stopping.")
        return
    
    # Step 2: Test chatbot
    if not test_chatbot():
        print("❌ Chatbot test failed. Please check the setup.")
        return
    
    print("\n🎉 SUCCESS!")
    print("✅ Database migration completed")
    print("✅ New schema is active")
    print("✅ Sample data is populated")
    print("✅ Chatbot is working with new schema")
    print("\nYou can now run the LangGraph chatbot with:")
    print("  python chatbot_langgraph.py")
    print("\nOr view the database contents with:")
    print("  python view_data_new.py")

if __name__ == "__main__":
    main()
