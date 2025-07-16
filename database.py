import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables with override
load_dotenv(override=True)

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            # Debug: Print connection parameters
            print("Attempting connection with:")
            print(f"  Host: {os.getenv('DB_HOST')}")
            print(f"  Port: {os.getenv('DB_PORT')}")
            print(f"  Database: {os.getenv('DB_NAME')}")
            print(f"  User: {os.getenv('DB_USER')}")
            print(f"  Password: {'Set' if os.getenv('DB_PASSWORD') else 'Empty'}")
            
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD') or None
            )
            self.cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            print("Database connection established successfully!")
            return True
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("Database connection closed.")
    
    def execute_query(self, query, params=None):
        """Execute a SELECT query"""
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
            return None
    
    def execute_update(self, query, params=None):
        """Execute an INSERT, UPDATE, or DELETE query"""
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return self.cursor.rowcount
        except Exception as e:
            print(f"Error executing update: {e}")
            self.connection.rollback()
            return 0
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        try:
            # Hotels table
            create_hotels_table = """
            CREATE TABLE IF NOT EXISTS hotels (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                address TEXT,
                city VARCHAR(100),
                country VARCHAR(100),
                rating DECIMAL(2,1),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Rooms table
            create_rooms_table = """
            CREATE TABLE IF NOT EXISTS rooms (
                id SERIAL PRIMARY KEY,
                hotel_id INTEGER REFERENCES hotels(id) ON DELETE CASCADE,
                room_number VARCHAR(10) NOT NULL,
                room_type VARCHAR(50),
                price_per_night DECIMAL(10,2),
                is_available BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Bookings table
            create_bookings_table = """
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                room_id INTEGER REFERENCES rooms(id) ON DELETE CASCADE,
                guest_name VARCHAR(255) NOT NULL,
                guest_email VARCHAR(255),
                check_in_date DATE,
                check_out_date DATE,
                total_amount DECIMAL(10,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            
            # Execute table creation queries
            self.execute_update(create_hotels_table)
            self.execute_update(create_rooms_table)
            self.execute_update(create_bookings_table)
            
            print("Tables created successfully!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
