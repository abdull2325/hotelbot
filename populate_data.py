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
    db.execute_update("DELETE FROM rooms;")
    db.execute_update("DELETE FROM hotels;")
    
    # Hotel data
    hotels_data = [
        ("Grand Palace Hotel", "123 Main Street", "New York", "USA", 4.8),
        ("Ocean View Resort", "456 Beach Avenue", "Miami", "USA", 4.5),
        ("Mountain Lodge", "789 Alpine Drive", "Denver", "USA", 4.2),
        ("City Center Inn", "321 Downtown Blvd", "Chicago", "USA", 4.0),
        ("Luxury Suites", "654 Elite Street", "Los Angeles", "USA", 4.7),
        ("Historic Hotel", "987 Heritage Lane", "Boston", "USA", 4.3),
        ("Boutique Hotel", "147 Trendy Ave", "San Francisco", "USA", 4.6),
        ("Business Hotel", "258 Corporate Plaza", "Seattle", "USA", 4.1),
        ("Seaside Resort", "369 Coastal Highway", "San Diego", "USA", 4.4),
        ("Urban Retreat", "741 Metropolitan Way", "Las Vegas", "USA", 4.5)
    ]
    
    # Insert hotels and store their IDs
    print("Inserting hotels...")
    hotel_ids = []
    for hotel_data in hotels_data:
        query = """
        INSERT INTO hotels (name, address, city, country, rating)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
        """
        result = db.execute_query(query, hotel_data)
        if result:
            hotel_ids.append(result[0]['id'])
            print(f"  - {hotel_data[0]} added with ID: {result[0]['id']}")
    
    print(f"Successfully inserted {len(hotel_ids)} hotels")
    
    # Room types and pricing
    room_types = [
        ("Standard", 120.00),
        ("Deluxe", 180.00),
        ("Suite", 250.00),
        ("Executive", 200.00),
        ("Penthouse", 400.00)
    ]
    
    # Insert rooms for each hotel
    print("\nInserting rooms...")
    room_ids = []
    for hotel_id in hotel_ids:
        # Each hotel gets 15-25 rooms
        num_rooms = random.randint(15, 25)
        for room_num in range(1, num_rooms + 1):
            room_type, base_price = random.choice(room_types)
            # Add some price variation
            price = base_price + random.uniform(-20, 50)
            room_number = f"{random.randint(1, 5)}{room_num:02d}"
            
            query = """
            INSERT INTO rooms (hotel_id, room_number, room_type, price_per_night, is_available)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
            """
            room_data = (hotel_id, room_number, room_type, round(price, 2), True)
            result = db.execute_query(query, room_data)
            if result:
                room_ids.append(result[0]['id'])
    
    print(f"Successfully inserted {len(room_ids)} rooms")
    
    # Guest names for bookings
    guest_names = [
        "John Smith", "Emma Johnson", "Michael Brown", "Sarah Davis",
        "David Wilson", "Lisa Anderson", "Robert Taylor", "Jennifer Thomas",
        "William Jackson", "Amanda White", "James Harris", "Jessica Martin",
        "Christopher Thompson", "Ashley Garcia", "Daniel Martinez",
        "Nicole Robinson", "Matthew Clark", "Michelle Rodriguez",
        "Anthony Lewis", "Elizabeth Lee", "Mark Walker", "Maria Hall",
        "Steven Allen", "Laura Young", "Paul Hernandez", "Karen King"
    ]
    
    # Insert bookings
    print("\nInserting bookings...")
    booking_count = 0
    for _ in range(100):  # Create 100 bookings
        room_id = random.choice(room_ids)
        guest_name = random.choice(guest_names)
        guest_email = f"{guest_name.lower().replace(' ', '.')}@email.com"
        
        # Generate random check-in date (past 3 months to future 6 months)
        start_date = datetime.now() - timedelta(days=90)
        random_days = random.randint(0, 270)  # 9 months range
        check_in_date = start_date + timedelta(days=random_days)
        
        # Stay duration between 1-7 nights
        stay_duration = random.randint(1, 7)
        check_out_date = check_in_date + timedelta(days=stay_duration)
        
        # Get room price for total calculation
        room_query = "SELECT price_per_night FROM rooms WHERE id = %s;"
        room_result = db.execute_query(room_query, (room_id,))
        if room_result:
            room_price = float(room_result[0]['price_per_night'])
            total_amount = room_price * stay_duration
            
            booking_query = """
            INSERT INTO bookings (room_id, guest_name, guest_email, check_in_date, check_out_date, total_amount)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            booking_data = (
                room_id, guest_name, guest_email,
                check_in_date.date(), check_out_date.date(), round(total_amount, 2)
            )
            
            rows_affected = db.execute_update(booking_query, booking_data)
            if rows_affected:
                booking_count += 1
    
    print(f"Successfully inserted {booking_count} bookings")
    
    # Display summary statistics
    print("\n=== Database Summary ===")
    
    # Hotel count by city
    hotels_by_city = db.execute_query("""
        SELECT city, COUNT(*) as hotel_count, AVG(rating) as avg_rating
        FROM hotels
        GROUP BY city
        ORDER BY hotel_count DESC;
    """)
    
    print("\nHotels by City:")
    for row in hotels_by_city:
        print(f"  {row['city']}: {row['hotel_count']} hotels (avg rating: {row['avg_rating']:.1f})")
    
    # Room type distribution
    room_types_count = db.execute_query("""
        SELECT room_type, COUNT(*) as count, AVG(price_per_night) as avg_price
        FROM rooms
        GROUP BY room_type
        ORDER BY count DESC;
    """)
    
    print("\nRoom Types:")
    for row in room_types_count:
        print(f"  {row['room_type']}: {row['count']} rooms (avg price: ${row['avg_price']:.2f})")
    
    # Recent bookings
    recent_bookings = db.execute_query("""
        SELECT b.guest_name, h.name as hotel_name, r.room_number, b.check_in_date, b.total_amount
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN hotels h ON r.hotel_id = h.id
        ORDER BY b.created_at DESC
        LIMIT 10;
    """)
    
    print("\nRecent Bookings:")
    for booking in recent_bookings:
        print(f"  {booking['guest_name']} - {booking['hotel_name']} Room {booking['room_number']} - Check-in: {booking['check_in_date']} - ${booking['total_amount']}")
    
    # Close connection
    db.disconnect()
    print("\nDatabase population completed successfully!")

if __name__ == "__main__":
    populate_dummy_data()
