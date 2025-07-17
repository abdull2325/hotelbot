from database import DatabaseConnection

def display_database_contents():
    """Display the contents of the database in a formatted way"""
    
    db = DatabaseConnection()
    
    if not db.connect():
        print("Failed to connect to database!")
        return
    
    print("🏨 HOTEL DATABASE CONTENTS 🏨")
    print("=" * 50)
    
    # Display all hotels
    print("\n📍 HOTELS:")
    hotels = db.execute_query("""
        SELECT h.*, 
               COUNT(hr.id) as room_count,
               COUNT(b.id) as booking_count
        FROM hotels h
        LEFT JOIN hotel_rooms hr ON h.id = hr.hotel_id
        LEFT JOIN bookings b ON hr.id = b.room_id
        WHERE h.is_active = true
        GROUP BY h.id, h.name, h.address, h.city, h.stars, h.description, h.phone_number, h.email, h.latitude, h.longitude, h.amenities, h.is_active, h.created_at, h.updated_at
        ORDER BY h.name;
    """)
    
    if hotels:
        for hotel in hotels:
            print(f"\n🏨 {hotel['name']}")
            print(f"   📍 {hotel['address']}, {hotel['city']}")
            print(f"   ⭐ Stars: {hotel['stars']}/5")
            if hotel.get('description'):
                print(f"   📝 {hotel['description']}")
            if hotel.get('phone_number'):
                print(f"   📞 {hotel['phone_number']}")
            if hotel.get('email'):
                print(f"   📧 {hotel['email']}")
            if hotel.get('amenities'):
                print(f"   🎯 Amenities: {', '.join(hotel['amenities'])}")
            print(f"   🏠 Rooms: {hotel['room_count']} | 📅 Bookings: {hotel['booking_count']}")
    
    # Display room statistics
    print("\n\n🏠 ROOM STATISTICS:")
    room_stats = db.execute_query("""
        SELECT 
            room_type,
            COUNT(*) as count,
            AVG(price_per_night) as avg_price,
            MIN(price_per_night) as min_price,
            MAX(price_per_night) as max_price,
            AVG(capacity) as avg_capacity
        FROM hotel_rooms
        GROUP BY room_type
        ORDER BY avg_price DESC;
    """)
    
    if room_stats:
        for stat in room_stats:
            print(f"\n🏠 {stat['room_type'].upper()}")
            print(f"   📊 Count: {stat['count']}")
            print(f"   💰 Price Range: ${stat['min_price']:.2f} - ${stat['max_price']:.2f}")
            print(f"   📈 Average Price: ${stat['avg_price']:.2f}")
            print(f"   👥 Average Capacity: {stat['avg_capacity']:.1f} guests")
    
    # Display availability statistics
    print("\n\n✅ AVAILABILITY STATISTICS:")
    availability_stats = db.execute_query("""
        SELECT 
            COUNT(*) as total_rooms,
            COUNT(CASE WHEN is_available = true THEN 1 END) as available_rooms,
            COUNT(CASE WHEN is_available = false THEN 1 END) as occupied_rooms,
            ROUND(COUNT(CASE WHEN is_available = true THEN 1 END) * 100.0 / COUNT(*), 1) as availability_percentage
        FROM hotel_rooms;
    """)
    
    if availability_stats:
        stats = availability_stats[0]
        print(f"   📊 Total Rooms: {stats['total_rooms']}")
        print(f"   ✅ Available: {stats['available_rooms']}")
        print(f"   🔴 Occupied: {stats['occupied_rooms']}")
        print(f"   📈 Availability: {stats['availability_percentage']}%")
    
    # Display recent bookings
    print("\n\n📅 RECENT BOOKINGS:")
    recent_bookings = db.execute_query("""
        SELECT 
            b.guest_name,
            b.guest_email,
            b.check_in,
            b.check_out,
            b.total_amount,
            b.status,
            h.name as hotel_name,
            hr.room_number,
            hr.room_type
        FROM bookings b
        JOIN hotel_rooms hr ON b.room_id = hr.id
        JOIN hotels h ON hr.hotel_id = h.id
        ORDER BY b.created_at DESC
        LIMIT 5;
    """)
    
    if recent_bookings:
        for booking in recent_bookings:
            print(f"\n📅 {booking['guest_name']}")
            print(f"   🏨 {booking['hotel_name']} - Room {booking['room_number']} ({booking['room_type']})")
            print(f"   📧 {booking['guest_email']}")
            print(f"   📆 {booking['check_in']} to {booking['check_out']}")
            print(f"   💰 ${booking['total_amount']:.2f}")
            print(f"   📊 Status: {booking['status']}")
    
    # Display city statistics
    print("\n\n🌍 CITY STATISTICS:")
    city_stats = db.execute_query("""
        SELECT 
            city,
            COUNT(*) as hotel_count,
            AVG(stars) as avg_stars,
            COUNT(hr.id) as total_rooms,
            COUNT(CASE WHEN hr.is_available = true THEN 1 END) as available_rooms
        FROM hotels h
        LEFT JOIN hotel_rooms hr ON h.id = hr.hotel_id
        WHERE h.is_active = true
        GROUP BY city
        ORDER BY hotel_count DESC;
    """)
    
    if city_stats:
        for stat in city_stats:
            print(f"\n🌍 {stat['city']}")
            print(f"   🏨 Hotels: {stat['hotel_count']}")
            print(f"   ⭐ Average Stars: {stat['avg_stars']:.1f}")
            print(f"   🏠 Total Rooms: {stat['total_rooms']}")
            print(f"   ✅ Available: {stat['available_rooms']}")
    
    # Display booking status summary
    print("\n\n📊 BOOKING STATUS SUMMARY:")
    booking_stats = db.execute_query("""
        SELECT 
            status,
            COUNT(*) as count,
            SUM(total_amount) as total_revenue
        FROM bookings
        GROUP BY status
        ORDER BY count DESC;
    """)
    
    if booking_stats:
        for stat in booking_stats:
            print(f"   📊 {stat['status'].upper()}: {stat['count']} bookings, ${stat['total_revenue']:.2f} revenue")
    
    # Display overall statistics
    print("\n\n📈 OVERALL STATISTICS:")
    overall_stats = db.execute_query("""
        SELECT 
            (SELECT COUNT(*) FROM hotels WHERE is_active = true) as total_hotels,
            (SELECT COUNT(*) FROM hotel_rooms) as total_rooms,
            (SELECT COUNT(*) FROM bookings) as total_bookings,
            (SELECT SUM(total_amount) FROM bookings WHERE status = 'confirmed') as confirmed_revenue,
            (SELECT AVG(stars) FROM hotels WHERE is_active = true) as avg_hotel_stars,
            (SELECT AVG(price_per_night) FROM hotel_rooms) as avg_room_price;
    """)
    
    if overall_stats:
        stats = overall_stats[0]
        print(f"   🏨 Total Hotels: {stats['total_hotels']}")
        print(f"   🏠 Total Rooms: {stats['total_rooms']}")
        print(f"   📅 Total Bookings: {stats['total_bookings']}")
        print(f"   💰 Confirmed Revenue: ${stats['confirmed_revenue']:.2f}")
        print(f"   ⭐ Average Hotel Stars: {stats['avg_hotel_stars']:.1f}")
        print(f"   💵 Average Room Price: ${stats['avg_room_price']:.2f}")
    
    db.disconnect()
    print("\n" + "=" * 50)
    print("Database contents displayed successfully!")

def search_hotels_by_city(city_name):
    """Search and display hotels in a specific city"""
    
    db = DatabaseConnection()
    
    if not db.connect():
        print("Failed to connect to database!")
        return
    
    print(f"🔍 SEARCHING HOTELS IN {city_name.upper()}")
    print("=" * 50)
    
    hotels = db.execute_query("""
        SELECT h.*, 
               COUNT(hr.id) as room_count,
               COUNT(CASE WHEN hr.is_available = true THEN 1 END) as available_rooms
        FROM hotels h
        LEFT JOIN hotel_rooms hr ON h.id = hr.hotel_id
        WHERE LOWER(h.city) LIKE LOWER(%s) AND h.is_active = true
        GROUP BY h.id, h.name, h.address, h.city, h.stars, h.description, h.phone_number, h.email, h.latitude, h.longitude, h.amenities, h.is_active, h.created_at, h.updated_at
        ORDER BY h.stars DESC, h.name;
    """, (f"%{city_name}%",))
    
    if hotels:
        print(f"Found {len(hotels)} hotels in {city_name}:")
        for hotel in hotels:
            print(f"\n🏨 {hotel['name']}")
            print(f"   📍 {hotel['address']}, {hotel['city']}")
            print(f"   ⭐ Stars: {hotel['stars']}/5")
            if hotel.get('description'):
                print(f"   📝 {hotel['description']}")
            if hotel.get('phone_number'):
                print(f"   📞 {hotel['phone_number']}")
            if hotel.get('amenities'):
                print(f"   🎯 Amenities: {', '.join(hotel['amenities'])}")
            print(f"   🏠 Total Rooms: {hotel['room_count']} | ✅ Available: {hotel['available_rooms']}")
    else:
        print(f"No hotels found in {city_name}")
    
    db.disconnect()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        city_name = " ".join(sys.argv[1:])
        search_hotels_by_city(city_name)
    else:
        display_database_contents()
