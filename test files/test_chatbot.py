from hotel_search_service import HotelSearchService

def test_hotel_search_service():
    """Test the hotel search service functionality"""
    
    print("🧪 Testing Hotel Search Service...")
    print("=" * 50)
    
    service = HotelSearchService()
    
    if not service.connect():
        print("❌ Failed to connect to database!")
        return
    
    try:
        # Test 1: Search hotels by city
        print("\n1. Testing search by city (New York):")
        hotels = service.search_hotels_by_city("New York")
        if hotels:
            for hotel in hotels:
                print(f"   🏨 {hotel['name']} - Rating: {hotel['rating']}/5.0")
        else:
            print("   No hotels found")
        
        # Test 2: Search hotels by rating
        print("\n2. Testing search by rating (4.5+):")
        hotels = service.search_hotels_by_rating(4.5)
        if hotels:
            for hotel in hotels[:3]:  # Show first 3
                print(f"   🏨 {hotel['name']} ({hotel['city']}) - Rating: {hotel['rating']}/5.0")
        else:
            print("   No hotels found")
        
        # Test 3: Get available rooms
        print("\n3. Testing available rooms (first 5):")
        rooms = service.get_available_rooms()
        if rooms:
            for room in rooms[:5]:  # Show first 5
                print(f"   🏠 {room['hotel_name']} - Room {room['room_number']} ({room['room_type']}) - ${room['price_per_night']:.2f}/night")
        else:
            print("   No rooms found")
        
        # Test 4: Search by price range
        print("\n4. Testing search by price range ($150-$300):")
        hotels = service.search_hotels_by_price_range(150, 300)
        if hotels:
            for hotel in hotels[:3]:  # Show first 3
                print(f"   🏨 {hotel['name']} ({hotel['city']}) - ${hotel['min_room_price']:.2f}-${hotel['max_room_price']:.2f}")
        else:
            print("   No hotels found")
        
        # Test 5: Get hotel details
        print("\n5. Testing hotel details (Grand Palace Hotel):")
        hotel = service.get_hotel_details("Grand Palace Hotel")
        if hotel:
            print(f"   🏨 {hotel['name']}")
            print(f"   📍 {hotel['address']}, {hotel['city']}")
            print(f"   ⭐ Rating: {hotel['rating']}/5.0")
            print(f"   🏠 Total Rooms: {hotel['total_rooms']}")
            print(f"   💰 Price Range: ${hotel['min_price']:.2f} - ${hotel['max_price']:.2f}")
        else:
            print("   Hotel not found")
        
        # Test 6: Get city summary
        print("\n6. Testing city summary (Miami):")
        summary = service.get_city_summary("Miami")
        if summary:
            print(f"   🌆 {summary['city']}")
            print(f"   🏨 Hotels: {summary['hotel_count']}")
            print(f"   🏠 Total Rooms: {summary['total_rooms']}")
            print(f"   ✅ Available: {summary['available_rooms']}")
            print(f"   ⭐ Avg Rating: {summary['avg_rating']:.1f}/5.0")
        else:
            print("   City not found")
        
        print("\n✅ All tests completed successfully!")
        
    finally:
        service.disconnect()

def test_search_queries():
    """Test various search scenarios"""
    
    print("\n🔍 Testing Search Scenarios...")
    print("=" * 50)
    
    service = HotelSearchService()
    
    if not service.connect():
        print("❌ Failed to connect to database!")
        return
    
    try:
        # Scenario 1: Looking for budget hotels
        print("\n💰 Scenario 1: Budget hotels under $200/night")
        rooms = service.get_available_rooms(max_price=200)
        print(f"   Found {len(rooms)} budget rooms")
        
        # Scenario 2: Luxury hotels
        print("\n✨ Scenario 2: Luxury hotels (4.5+ rating)")
        hotels = service.search_hotels_by_rating(4.5)
        print(f"   Found {len(hotels)} luxury hotels")
        
        # Scenario 3: Specific room type
        print("\n🛏️ Scenario 3: Suite rooms available")
        rooms = service.get_available_rooms(room_type="Suite")
        print(f"   Found {len(rooms)} suite rooms")
        
        # Scenario 4: City with most hotels
        cities = ["New York", "Miami", "Los Angeles", "Chicago", "Boston"]
        print("\n🏙️ Scenario 4: Hotel count by city")
        for city in cities:
            summary = service.get_city_summary(city)
            if summary:
                print(f"   {city}: {summary['hotel_count']} hotels")
        
        print("\n✅ Search scenarios completed!")
        
    finally:
        service.disconnect()

if __name__ == "__main__":
    test_hotel_search_service()
    test_search_queries()
