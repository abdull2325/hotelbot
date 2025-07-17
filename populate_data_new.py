from database import DatabaseConnection
import random
from datetime import datetime, timedelta

def populate_dummy_data():
    """Populate the database with dummy data for hotels, rooms, and bookings"""
    
    db = DatabaseConnection()
    
    if not db.connect():
        print("Failed to connect to database!")
        return
    
    print("Connected to database successfully!")
    
    # Create tables first
    print("Creating tables...")
    db.create_tables()
    
    # Clear existing data
    print("Clearing existing data...")
    db.execute_update("DELETE FROM bookings;")
    db.execute_update("DELETE FROM hotel_rooms;")
    db.execute_update("DELETE FROM hotels;")
    
    # Hotel data (updated for new schema)
    hotels_data = [
        ("Grand Palace Hotel", "New York", "123 Main Street", 5, "Luxury hotel in Manhattan", "+1-212-555-0123", "info@grandpalace.com", 40.7589, -73.9851, ["WiFi", "Spa", "Pool", "Gym"]),
        ("Ocean View Resort", "Miami", "456 Beach Avenue", 4, "Beautiful beachfront resort", "+1-305-555-0456", "reservations@oceanview.com", 25.7617, -80.1918, ["WiFi", "Beach Access", "Pool", "Restaurant"]),
        ("Mountain Lodge", "Denver", "789 Alpine Drive", 4, "Cozy mountain retreat", "+1-303-555-0789", "stay@mountainlodge.com", 39.7392, -104.9903, ["WiFi", "Fireplace", "Ski Access"]),
        ("City Center Inn", "Chicago", "321 Downtown Blvd", 3, "Convenient downtown location", "+1-312-555-0321", "bookings@citycenter.com", 41.8781, -87.6298, ["WiFi", "Business Center"]),
        ("Luxury Suites", "Los Angeles", "654 Elite Street", 5, "Premium luxury accommodations", "+1-310-555-0654", "concierge@luxurysuites.com", 34.0522, -118.2437, ["WiFi", "Spa", "Pool", "Valet"]),
        ("Historic Hotel", "Boston", "987 Heritage Lane", 4, "Charming historic property", "+1-617-555-0987", "heritage@historichotel.com", 42.3601, -71.0589, ["WiFi", "Historic Tours"]),
        ("Boutique Hotel", "San Francisco", "147 Trendy Ave", 4, "Stylish boutique experience", "+1-415-555-0147", "stay@boutique.com", 37.7749, -122.4194, ["WiFi", "Rooftop Bar", "Art Gallery"]),
        ("Business Hotel", "Seattle", "258 Corporate Plaza", 3, "Modern business accommodations", "+1-206-555-0258", "business@corporatehotel.com", 47.6062, -122.3321, ["WiFi", "Conference Rooms", "Business Center"]),
        ("Seaside Resort", "San Diego", "369 Coastal Highway", 4, "Relaxing coastal getaway", "+1-619-555-0369", "info@seasideresort.com", 32.7157, -117.1611, ["WiFi", "Beach Access", "Pool", "Spa"]),
        ("Urban Retreat", "Las Vegas", "741 Metropolitan Way", 4, "Modern urban hotel", "+1-702-555-0741", "retreat@urbanhotel.com", 36.1699, -115.1398, ["WiFi", "Casino", "Pool", "Shows"])
    ]
    
    # Insert hotels and store their IDs
    print("Inserting hotels...")
    hotel_ids = []
    for hotel_data in hotels_data:
        query = """
        INSERT INTO hotels (name, city, address, stars, description, phone_number, email, latitude, longitude, amenities)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = db.execute_query(query, hotel_data)
        if result:
            hotel_ids.append(result[0]['id'])
            print(f"  ✓ Inserted hotel: {hotel_data[0]}")
    
    print(f"Inserted {len(hotel_ids)} hotels")
    
    # Room types based on new enum
    room_types = ['single', 'double', 'suite', 'deluxe', 'presidential']
    
    # Insert rooms for each hotel
    print("Inserting rooms...")
    room_ids = []
    for hotel_id in hotel_ids:
        # Generate 8-15 rooms per hotel
        num_rooms = random.randint(8, 15)
        
        for room_num in range(1, num_rooms + 1):
            room_type = random.choice(room_types)
            capacity = random.randint(1, 6)
            
            # Price varies by room type
            if room_type == 'presidential':
                base_price = random.randint(500, 1000)
            elif room_type == 'suite':
                base_price = random.randint(300, 600)
            elif room_type == 'deluxe':
                base_price = random.randint(200, 400)
            elif room_type == 'double':
                base_price = random.randint(150, 300)
            else:  # single
                base_price = random.randint(80, 200)
            
            price_per_night = base_price + random.randint(-30, 50)
            is_available = random.choice([True, True, True, False])  # 75% available
            
            room_number = f"{room_num:03d}"
            
            image_urls = [f"https://example.com/hotel{hotel_id}/room{room_number}.jpg"]
            amenities = ["WiFi", "TV", "Air Conditioning"]
            
            if room_type in ['suite', 'deluxe', 'presidential']:
                amenities.extend(["Mini Bar", "Room Service"])
            if room_type == 'presidential':
                amenities.extend(["Butler Service", "Jacuzzi", "Balcony"])
            
            room_data = (
                hotel_id,
                room_number,
                capacity,
                price_per_night,
                room_type,
                is_available,
                image_urls,
                amenities
            )
            
            query = """
            INSERT INTO hotel_rooms (hotel_id, room_number, capacity, price_per_night, room_type, is_available, image_urls, amenities)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            result = db.execute_query(query, room_data)
            if result:
                room_ids.append(result[0]['id'])
    
    print(f"Inserted {len(room_ids)} rooms")
    
    # Insert bookings for some rooms
    print("Inserting bookings...")
    booking_count = 0
    guest_names = [
        "John Smith", "Jane Doe", "Mike Johnson", "Sarah Wilson", "David Brown",
        "Emily Davis", "Chris Anderson", "Lisa Taylor", "Robert Miller", "Amanda Garcia",
        "Kevin Martinez", "Rachel Rodriguez", "Brian Lee", "Nicole White", "Steven Harris"
    ]
    
    statuses = ['confirmed', 'completed', 'cancelled']
    
    # Create bookings for about 30% of rooms
    available_rooms = [room_id for room_id in room_ids if random.random() < 0.3]
    
    for room_id in available_rooms:
        # Get room details to calculate price
        room_query = "SELECT price_per_night FROM hotel_rooms WHERE id = %s"
        room_result = db.execute_query(room_query, (room_id,))
        
        if room_result:
            room_price = room_result[0]['price_per_night']
            
            guest_name = random.choice(guest_names)
            guest_email = f"{guest_name.lower().replace(' ', '.')}@example.com"
            guest_phone = f"+1-{random.randint(200, 999)}-555-{random.randint(1000, 9999)}"
            
            # Random dates
            start_date = datetime.now().date() + timedelta(days=random.randint(-30, 30))
            end_date = start_date + timedelta(days=random.randint(1, 7))
            
            nights = (end_date - start_date).days
            total_amount = float(room_price) * nights
            
            status = random.choice(statuses)
            
            booking_data = (
                room_id,
                guest_name,
                guest_email,
                guest_phone,
                start_date,
                end_date,
                total_amount,
                status
            )
            
            query = """
            INSERT INTO bookings (room_id, guest_name, guest_email, guest_phone, check_in, check_out, total_amount, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
            """
            
            result = db.execute_query(query, booking_data)
            if result:
                booking_count += 1
                
                # If booking is confirmed and overlaps with current date, mark room as unavailable
                if status == 'confirmed' and start_date <= datetime.now().date() <= end_date:
                    update_query = "UPDATE hotel_rooms SET is_available = FALSE WHERE id = %s"
                    db.execute_update(update_query, (room_id,))
    
    print(f"Inserted {booking_count} bookings")
    
    # Display summary
    print("\n=== DATABASE POPULATION SUMMARY ===")
    print(f"✓ Hotels: {len(hotel_ids)}")
    print(f"✓ Rooms: {len(room_ids)}")
    print(f"✓ Bookings: {booking_count}")
    
    # Display sample data
    print("\n=== SAMPLE DATA ===")
    sample_hotels = db.execute_query("SELECT name, city, stars FROM hotels LIMIT 3")
    if sample_hotels:
        print("Sample Hotels:")
        for hotel in sample_hotels:
            print(f"  - {hotel['name']} ({hotel['city']}) - {hotel['stars']} stars")
    
    sample_rooms = db.execute_query("""
        SELECT hr.room_number, hr.room_type, hr.price_per_night, h.name as hotel_name
        FROM hotel_rooms hr
        JOIN hotels h ON hr.hotel_id = h.id
        LIMIT 5
    """)
    if sample_rooms:
        print("\nSample Rooms:")
        for room in sample_rooms:
            print(f"  - Room {room['room_number']} ({room['room_type']}) at {room['hotel_name']} - ${room['price_per_night']}/night")
    
    db.disconnect()
    print("\nDatabase population completed successfully!")

if __name__ == "__main__":
    populate_dummy_data()
