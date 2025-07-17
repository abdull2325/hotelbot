from database import DatabaseConnection
from typing import List, Dict, Optional
from datetime import datetime, date

class HotelSearchService:
    def __init__(self):
        self.db = DatabaseConnection()
    
    def connect(self):
        """Connect to the database"""
        return self.db.connect()
    
    def disconnect(self):
        """Disconnect from the database"""
        self.db.disconnect()
    
    def search_hotels_by_city(self, city: str) -> List[Dict]:
        """Search hotels in a specific city"""
        query = """
        SELECT h.*, 
               COUNT(hr.id) as total_rooms,
               COUNT(CASE WHEN hr.is_available = true THEN 1 END) as available_rooms
        FROM hotels h
        LEFT JOIN hotel_rooms hr ON h.id = hr.hotel_id
        WHERE LOWER(h.city) LIKE LOWER(%s) AND h.is_active = true
        GROUP BY h.id, h.name, h.address, h.city, h.stars, h.description, h.phone_number, h.email, h.latitude, h.longitude, h.amenities, h.is_active, h.created_at, h.updated_at
        ORDER BY h.stars DESC, h.name;
        """
        return self.db.execute_query(query, (f"%{city}%",))
    
    def search_hotels_by_rating(self, min_rating: float) -> List[Dict]:
        """Search hotels with minimum rating (now using stars)"""
        query = """
        SELECT h.*, 
               COUNT(hr.id) as total_rooms,
               COUNT(CASE WHEN hr.is_available = true THEN 1 END) as available_rooms
        FROM hotels h
        LEFT JOIN hotel_rooms hr ON h.id = hr.hotel_id
        WHERE h.stars >= %s AND h.is_active = true
        GROUP BY h.id, h.name, h.address, h.city, h.stars, h.description, h.phone_number, h.email, h.latitude, h.longitude, h.amenities, h.is_active, h.created_at, h.updated_at
        ORDER BY h.stars DESC, h.name;
        """
        return self.db.execute_query(query, (min_rating,))
    
    def get_available_rooms(self, hotel_id: int = None, room_type: str = None, max_price: float = None) -> List[Dict]:
        """Get available rooms with optional filters"""
        query = """
        SELECT hr.*, h.name as hotel_name, h.city, h.address
        FROM hotel_rooms hr
        JOIN hotels h ON hr.hotel_id = h.id
        WHERE hr.is_available = true AND h.is_active = true
        """
        params = []
        
        if hotel_id:
            query += " AND hr.hotel_id = %s"
            params.append(hotel_id)
        
        if room_type:
            query += " AND LOWER(hr.room_type::text) LIKE LOWER(%s)"
            params.append(f"%{room_type}%")
        
        if max_price:
            query += " AND hr.price_per_night <= %s"
            params.append(max_price)
        
        query += " ORDER BY hr.price_per_night ASC;"
        
        return self.db.execute_query(query, params if params else None)
    
    def get_room_types_and_prices(self, hotel_id: int = None) -> List[Dict]:
        """Get room types and their price ranges"""
        query = """
        SELECT 
            hr.room_type,
            COUNT(*) as available_count,
            MIN(hr.price_per_night) as min_price,
            MAX(hr.price_per_night) as max_price,
            AVG(hr.price_per_night) as avg_price,
            h.name as hotel_name,
            h.city
        FROM hotel_rooms hr
        JOIN hotels h ON hr.hotel_id = h.id
        WHERE hr.is_available = true AND h.is_active = true
        """
        params = []
        
        if hotel_id:
            query += " AND hr.hotel_id = %s"
            params.append(hotel_id)
        
        query += """
        GROUP BY hr.room_type, h.name, h.city
        ORDER BY avg_price ASC;
        """
        
        return self.db.execute_query(query, params if params else None)
    
    def search_hotels_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """Search hotels with rooms in a specific price range"""
        query = """
        SELECT DISTINCT h.*, 
               MIN(hr.price_per_night) as min_room_price,
               MAX(hr.price_per_night) as max_room_price,
               COUNT(hr.id) as total_rooms
        FROM hotels h
        JOIN hotel_rooms hr ON h.id = hr.hotel_id
        WHERE hr.price_per_night BETWEEN %s AND %s
        AND hr.is_available = true AND h.is_active = true
        GROUP BY h.id, h.name, h.address, h.city, h.stars, h.description, h.phone_number, h.email, h.latitude, h.longitude, h.amenities, h.is_active, h.created_at, h.updated_at
        ORDER BY h.stars DESC, h.name;
        """
        return self.db.execute_query(query, (min_price, max_price))
    
    def get_hotel_details(self, hotel_name: str) -> Dict:
        """Get detailed information about a specific hotel"""
        query = """
        SELECT h.*, 
               COUNT(hr.id) as total_rooms,
               COUNT(CASE WHEN hr.is_available = true THEN 1 END) as available_rooms,
               MIN(hr.price_per_night) as min_price,
               MAX(hr.price_per_night) as max_price,
               COUNT(b.id) as total_bookings
        FROM hotels h
        LEFT JOIN hotel_rooms hr ON h.id = hr.hotel_id
        LEFT JOIN bookings b ON hr.id = b.room_id
        WHERE LOWER(h.name) LIKE LOWER(%s) AND h.is_active = true
        GROUP BY h.id, h.name, h.address, h.city, h.stars, h.description, h.phone_number, h.email, h.latitude, h.longitude, h.amenities, h.is_active, h.created_at, h.updated_at;
        """
        results = self.db.execute_query(query, (f"%{hotel_name}%",))
        return results[0] if results else None
    
    def get_city_summary(self, city: str) -> Dict:
        """Get summary of hotels and rooms in a city"""
        query = """
        SELECT 
            h.city,
            COUNT(DISTINCT h.id) as hotel_count,
            COUNT(hr.id) as total_rooms,
            COUNT(CASE WHEN hr.is_available = true THEN 1 END) as available_rooms,
            AVG(h.stars) as avg_rating,
            MIN(hr.price_per_night) as min_price,
            MAX(hr.price_per_night) as max_price
        FROM hotels h
        LEFT JOIN hotel_rooms hr ON h.id = hr.hotel_id
        WHERE LOWER(h.city) LIKE LOWER(%s) AND h.is_active = true
        GROUP BY h.city;
        """
        results = self.db.execute_query(query, (f"%{city}%",))
        return results[0] if results else None
    
    def get_recent_bookings(self, limit: int = 10) -> List[Dict]:
        """Get recent bookings for context"""
        query = """
        SELECT 
            b.guest_name,
            h.name as hotel_name,
            h.city,
            hr.room_number,
            hr.room_type,
            b.check_in,
            b.check_out,
            b.total_amount,
            b.status
        FROM bookings b
        JOIN hotel_rooms hr ON b.room_id = hr.id
        JOIN hotels h ON hr.hotel_id = h.id
        WHERE h.is_active = true
        ORDER BY b.created_at DESC
        LIMIT %s;
        """
        return self.db.execute_query(query, (limit,))
    
    def check_room_availability(self, hotel_name: str, room_type: str = None) -> List[Dict]:
        """Check availability of rooms in a specific hotel"""
        query = """
        SELECT hr.*, h.name as hotel_name, h.city
        FROM hotel_rooms hr
        JOIN hotels h ON hr.hotel_id = h.id
        WHERE LOWER(h.name) LIKE LOWER(%s)
        AND hr.is_available = true AND h.is_active = true
        """
        params = [f"%{hotel_name}%"]
        
        if room_type:
            query += " AND LOWER(hr.room_type::text) LIKE LOWER(%s)"
            params.append(f"%{room_type}%")
        
        query += " ORDER BY hr.price_per_night ASC;"
        
        return self.db.execute_query(query, params)
