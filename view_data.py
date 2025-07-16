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
               COUNT(r.id) as room_count,
               COUNT(b.id) as booking_count
        FROM hotels h
        LEFT JOIN rooms r ON h.id = r.hotel_id
        LEFT JOIN bookings b ON r.id = b.room_id
        GROUP BY h.id, h.name, h.address, h.city, h.country, h.rating, h.created_at
        ORDER BY h.name;
    """)
    
    if hotels:
        for hotel in hotels:
            print(f"\n🏨 {hotel['name']}")
            print(f"   📍 {hotel['address']}, {hotel['city']}, {hotel['country']}")
            print(f"   ⭐ Rating: {hotel['rating']}/5.0")
            print(f"   🏠 Rooms: {hotel['room_count']} | 📅 Bookings: {hotel['booking_count']}")
    
    # Display room statistics
    print("\n\n🏠 ROOM STATISTICS:")
    room_stats = db.execute_query("""
        SELECT 
            room_type,
            COUNT(*) as count,
            AVG(price_per_night) as avg_price,
            MIN(price_per_night) as min_price,
            MAX(price_per_night) as max_price
        FROM rooms
        GROUP BY room_type
        ORDER BY avg_price DESC;
    """)
    
    if room_stats:
        for stat in room_stats:
            print(f"  {stat['room_type']}: {stat['count']} rooms | Avg: ${stat['avg_price']:.2f} | Range: ${stat['min_price']:.2f} - ${stat['max_price']:.2f}")
    
    # Display booking statistics
    print("\n\n📅 BOOKING STATISTICS:")
    booking_stats = db.execute_query("""
        SELECT 
            COUNT(*) as total_bookings,
            AVG(total_amount) as avg_booking_value,
            SUM(total_amount) as total_revenue,
            MIN(check_in_date) as earliest_checkin,
            MAX(check_in_date) as latest_checkin
        FROM bookings;
    """)
    
    if booking_stats and booking_stats[0]['total_bookings']:
        stats = booking_stats[0]
        print(f"  Total Bookings: {stats['total_bookings']}")
        print(f"  Average Booking Value: ${stats['avg_booking_value']:.2f}")
        print(f"  Total Revenue: ${stats['total_revenue']:.2f}")
        print(f"  Booking Date Range: {stats['earliest_checkin']} to {stats['latest_checkin']}")
    
    # Display top hotels by bookings
    print("\n\n🏆 TOP HOTELS BY BOOKINGS:")
    top_hotels = db.execute_query("""
        SELECT 
            h.name,
            h.city,
            h.rating,
            COUNT(b.id) as booking_count,
            SUM(b.total_amount) as total_revenue
        FROM hotels h
        LEFT JOIN rooms r ON h.id = r.hotel_id
        LEFT JOIN bookings b ON r.id = b.room_id
        GROUP BY h.id, h.name, h.city, h.rating
        HAVING COUNT(b.id) > 0
        ORDER BY booking_count DESC
        LIMIT 5;
    """)
    
    if top_hotels:
        for i, hotel in enumerate(top_hotels, 1):
            print(f"  {i}. {hotel['name']} ({hotel['city']})")
            print(f"     ⭐ {hotel['rating']}/5.0 | 📅 {hotel['booking_count']} bookings | 💰 ${hotel['total_revenue']:.2f}")
    
    # Display recent bookings
    print("\n\n📋 RECENT BOOKINGS:")
    recent_bookings = db.execute_query("""
        SELECT 
            b.guest_name,
            b.guest_email,
            h.name as hotel_name,
            r.room_number,
            r.room_type,
            b.check_in_date,
            b.check_out_date,
            b.total_amount,
            b.created_at
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN hotels h ON r.hotel_id = h.id
        ORDER BY b.created_at DESC
        LIMIT 10;
    """)
    
    if recent_bookings:
        for booking in recent_bookings:
            nights = (booking['check_out_date'] - booking['check_in_date']).days
            print(f"  👤 {booking['guest_name']}")
            print(f"     🏨 {booking['hotel_name']} - Room {booking['room_number']} ({booking['room_type']})")
            print(f"     📅 {booking['check_in_date']} to {booking['check_out_date']} ({nights} nights)")
            print(f"     💰 ${booking['total_amount']:.2f}")
            print()
    
    # Display city statistics
    print("\n\n🌆 CITY STATISTICS:")
    city_stats = db.execute_query("""
        SELECT 
            h.city,
            COUNT(DISTINCT h.id) as hotel_count,
            COUNT(r.id) as room_count,
            COUNT(b.id) as booking_count,
            AVG(h.rating) as avg_rating,
            SUM(b.total_amount) as total_revenue
        FROM hotels h
        LEFT JOIN rooms r ON h.id = r.hotel_id
        LEFT JOIN bookings b ON r.id = b.room_id
        GROUP BY h.city
        ORDER BY booking_count DESC;
    """)
    
    if city_stats:
        for city in city_stats:
            print(f"  🌆 {city['city']}")
            print(f"     🏨 {city['hotel_count']} hotels | 🏠 {city['room_count']} rooms | 📅 {city['booking_count']} bookings")
            print(f"     ⭐ Avg Rating: {city['avg_rating']:.1f}/5.0 | 💰 Revenue: ${city['total_revenue'] or 0:.2f}")
    
    db.disconnect()
    print("\n" + "=" * 50)
    print("Database display completed!")

if __name__ == "__main__":
    display_database_contents()
