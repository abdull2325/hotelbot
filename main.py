from database import DatabaseConnection
from chatbot import OptimizedHotelChatBot
import os

def test_database_connection():
    """Test the database connection and show sample data"""
    db = DatabaseConnection()
    
    # Connect to database
    if db.connect():
        print("✅ Connected to PostgreSQL database!")
        
        # Create tables
        print("Creating tables...")
        db.create_tables()
        
        # Example: Insert a hotel
        insert_hotel_query = """
        INSERT INTO hotels (name, address, city, country, rating)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        
        hotel_data = ("Grand Hotel", "123 Main St", "New York", "USA", 4.5)
        result = db.execute_query(insert_hotel_query, hotel_data)
        
        if result:
            hotel_id = result[0]['id']
            print(f"Hotel inserted with ID: {hotel_id}")
            
            # Example: Insert a room
            insert_room_query = """
            INSERT INTO rooms (hotel_id, room_number, room_type, price_per_night)
            VALUES (%s, %s, %s, %s);
            """
            
            room_data = (hotel_id, "101", "Standard", 150.00)
            rows_affected = db.execute_update(insert_room_query, room_data)
            
            if rows_affected:
                print(f"Room inserted successfully!")
        
        # Example: Query hotels
        hotels = db.execute_query("SELECT * FROM hotels;")
        print("\nHotels in database:")
        for hotel in hotels:
            print(f"- {hotel['name']} in {hotel['city']}, Rating: {hotel['rating']}")
        
        # Close connection
        db.disconnect()
    else:
        print("❌ Failed to connect to database!")

def main():
    """Main function with menu options"""
    print("🏨 Welcome to HotelBot System! 🏨")
    print("=" * 50)
    
    while True:
        print("\nChoose an option:")
        print("1. 🤖 Start Interactive ChatBot (LangChain)")
        print("2. � Start Interactive ChatBot (LangGraph)")
        print("3. �🔍 View Database Contents")
        print("4. 📊 Test Database Connection")
        print("5. 🆚 Compare Both Chatbots")
        print("6. 🚪 Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            print("\n🤖 Starting LangChain ChatBot...")
            print("Make sure you have set your OpenAI API key in the .env file!")
            
            if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
                print("⚠️  Please set your OpenAI API key in the .env file first.")
                print("Add: OPENAI_API_KEY=your_actual_api_key")
                continue
            
            # Import and run original chatbot
            from chatbot import main as chatbot_main
            chatbot_main()
            
        elif choice == "2":
            print("\n� Starting LangGraph ChatBot...")
            print("Make sure you have set your OpenAI API key in the .env file!")
            
            if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
                print("⚠️  Please set your OpenAI API key in the .env file first.")
                print("Add: OPENAI_API_KEY=your_actual_api_key")
                continue
            
            # Import and run LangGraph chatbot
            from chatbot_langgraph import main as langgraph_main
            langgraph_main()
            
        elif choice == "3":
            print("\n�🔍 Loading Database Contents...")
            from view_data import display_database_contents
            display_database_contents()
            
        elif choice == "4":
            print("\n📊 Testing Database Connection...")
            test_database_connection()
            
        elif choice == "5":
            print("\n🆚 Starting Chatbot Comparison...")
            if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
                print("⚠️  Please set your OpenAI API key in the .env file first.")
                print("Add: OPENAI_API_KEY=your_actual_api_key")
                continue
            
            from test_langgraph_chatbot import interactive_comparison
            interactive_comparison()
            
        elif choice == "6":
            print("\n👋 Thank you for using HotelBot System!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-6.")

if __name__ == "__main__":
    main()
