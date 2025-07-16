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
               COUNT(r.id) as total_rooms,
               COUNT(CASE WHEN r.is_available = true THEN 1 END) as available_rooms
        FROM hotels h
        LEFT JOIN rooms r ON h.id = r.hotel_id
        WHERE LOWER(h.city) LIKE LOWER(%s)
        GROUP BY h.id, h.name, h.address, h.city, h.country, h.rating, h.created_at
        ORDER BY h.rating DESC;
        """
        return self.db.execute_query(query, (f"%{city}%",))
    
    def search_hotels_by_rating(self, min_rating: float) -> List[Dict]:
        """Search hotels with minimum rating"""
        query = """
        SELECT h.*, 
               COUNT(r.id) as total_rooms,
               COUNT(CASE WHEN r.is_available = true THEN 1 END) as available_rooms
        FROM hotels h
        LEFT JOIN rooms r ON h.id = r.hotel_id
        WHERE h.rating >= %s
        GROUP BY h.id, h.name, h.address, h.city, h.country, h.rating, h.created_at
        ORDER BY h.rating DESC;
        """
        return self.db.execute_query(query, (min_rating,))
    
    def get_available_rooms(self, hotel_id: int = None, room_type: str = None, max_price: float = None) -> List[Dict]:
        """Get available rooms with optional filters"""
        query = """
        SELECT r.*, h.name as hotel_name, h.city, h.address
        FROM rooms r
        JOIN hotels h ON r.hotel_id = h.id
        WHERE r.is_available = true
        """
        params = []
        
        if hotel_id:
            query += " AND r.hotel_id = %s"
            params.append(hotel_id)
        
        if room_type:
            query += " AND LOWER(r.room_type) LIKE LOWER(%s)"
            params.append(f"%{room_type}%")
        
        if max_price:
            query += " AND r.price_per_night <= %s"
            params.append(max_price)
        
        query += " ORDER BY r.price_per_night ASC;"
        
        return self.db.execute_query(query, params if params else None)
    
    def get_room_types_and_prices(self, hotel_id: int = None) -> List[Dict]:
        """Get room types and their price ranges"""
        query = """
        SELECT 
            r.room_type,
            COUNT(*) as available_count,
            MIN(r.price_per_night) as min_price,
            MAX(r.price_per_night) as max_price,
            AVG(r.price_per_night) as avg_price,
            h.name as hotel_name,
            h.city
        FROM rooms r
        JOIN hotels h ON r.hotel_id = h.id
        WHERE r.is_available = true
        """
        params = []
        
        if hotel_id:
            query += " AND r.hotel_id = %s"
            params.append(hotel_id)
        
        query += """
        GROUP BY r.room_type, h.name, h.city
        ORDER BY avg_price ASC;
        """
        
        return self.db.execute_query(query, params if params else None)
    
    def search_hotels_by_price_range(self, min_price: float, max_price: float) -> List[Dict]:
        """Search hotels with rooms in a specific price range"""
        query = """
        SELECT DISTINCT h.*, 
               MIN(r.price_per_night) as min_room_price,
               MAX(r.price_per_night) as max_room_price,
               COUNT(r.id) as total_rooms
        FROM hotels h
        JOIN rooms r ON h.id = r.hotel_id
        WHERE r.price_per_night BETWEEN %s AND %s
        AND r.is_available = true
        GROUP BY h.id, h.name, h.address, h.city, h.country, h.rating, h.created_at
        ORDER BY h.rating DESC;
        """
        return self.db.execute_query(query, (min_price, max_price))
    
    def get_hotel_details(self, hotel_name: str) -> Dict:
        """Get detailed information about a specific hotel"""
        query = """
        SELECT h.*, 
               COUNT(r.id) as total_rooms,
               COUNT(CASE WHEN r.is_available = true THEN 1 END) as available_rooms,
               MIN(r.price_per_night) as min_price,
               MAX(r.price_per_night) as max_price,
               COUNT(b.id) as total_bookings
        FROM hotels h
        LEFT JOIN rooms r ON h.id = r.hotel_id
        LEFT JOIN bookings b ON r.id = b.room_id
        WHERE LOWER(h.name) LIKE LOWER(%s)
        GROUP BY h.id, h.name, h.address, h.city, h.country, h.rating, h.created_at;
        """
        results = self.db.execute_query(query, (f"%{hotel_name}%",))
        return results[0] if results else None
    
    def get_city_summary(self, city: str) -> Dict:
        """Get summary of hotels and rooms in a city"""
        query = """
        SELECT 
            h.city,
            COUNT(DISTINCT h.id) as hotel_count,
            COUNT(r.id) as total_rooms,
            COUNT(CASE WHEN r.is_available = true THEN 1 END) as available_rooms,
            AVG(h.rating) as avg_rating,
            MIN(r.price_per_night) as min_price,
            MAX(r.price_per_night) as max_price
        FROM hotels h
        LEFT JOIN rooms r ON h.id = r.hotel_id
        WHERE LOWER(h.city) LIKE LOWER(%s)
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
            r.room_number,
            r.room_type,
            b.check_in_date,
            b.check_out_date,
            b.total_amount
        FROM bookings b
        JOIN rooms r ON b.room_id = r.id
        JOIN hotels h ON r.hotel_id = h.id
        ORDER BY b.created_at DESC
        LIMIT %s;
        """
        return self.db.execute_query(query, (limit,))
    
    def check_room_availability(self, hotel_name: str, room_type: str = None) -> List[Dict]:
        """Check availability of rooms in a specific hotel"""
        query = """
        SELECT r.*, h.name as hotel_name, h.city
        FROM rooms r
        JOIN hotels h ON r.hotel_id = h.id
        WHERE LOWER(h.name) LIKE LOWER(%s)
        AND r.is_available = true
        """
        params = [f"%{hotel_name}%"]
        
        if room_type:
            query += " AND LOWER(r.room_type) LIKE LOWER(%s)"
            params.append(f"%{room_type}%")
        
        query += " ORDER BY r.price_per_night ASC;"
        
        return self.db.execute_query(query, params)
