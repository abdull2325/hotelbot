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
            # Create ENUM for room type
            create_room_type_enum = """
            DO $$ BEGIN
                CREATE TYPE room_type_enum AS ENUM ('single', 'double', 'suite', 'deluxe', 'presidential');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
            """
            
            # Hotels table
            create_hotels_table = """
            CREATE TABLE IF NOT EXISTS hotels (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                city VARCHAR(100) NOT NULL,
                address TEXT,
                stars INTEGER CHECK (stars >= 1 AND stars <= 5) NOT NULL,
                description TEXT,
                phone_number VARCHAR(20),
                email VARCHAR(255),
                latitude DECIMAL(10,8),
                longitude DECIMAL(11,8),
                amenities TEXT[],
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                -- CONSTRAINTS
                CONSTRAINT valid_email CHECK (email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
                CONSTRAINT valid_phone CHECK (phone_number ~ '^\+?[0-9\s\-()]{7,20}$')
            );
            """
            
            # Rooms table
            create_rooms_table = """
            CREATE TABLE IF NOT EXISTS hotel_rooms (
                id SERIAL PRIMARY KEY,
                hotel_id INTEGER NOT NULL REFERENCES hotels(id) ON DELETE CASCADE,
                room_number VARCHAR(10) NOT NULL,
                capacity INTEGER NOT NULL CHECK (capacity > 0 AND capacity <= 10),
                price_per_night DECIMAL(10,2) NOT NULL CHECK (price_per_night > 0),
                room_type room_type_enum NOT NULL DEFAULT 'single',
                is_available BOOLEAN DEFAULT TRUE,
                image_urls TEXT[],
                amenities TEXT[],
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(hotel_id, room_number)
            );
            """
            
            # Bookings table
            create_bookings_table = """
            CREATE TABLE IF NOT EXISTS bookings (
                id SERIAL PRIMARY KEY,
                room_id INTEGER NOT NULL REFERENCES hotel_rooms(id) ON DELETE CASCADE,
                guest_name VARCHAR(255) NOT NULL,
                guest_email VARCHAR(255),
                guest_phone VARCHAR(20),
                check_in DATE NOT NULL,
                check_out DATE NOT NULL,
                total_amount DECIMAL(10,2),
                status VARCHAR(20) DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled', 'completed')),
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT valid_dates CHECK (check_out > check_in),
                CONSTRAINT valid_guest_email CHECK (guest_email ~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
                CONSTRAINT valid_guest_phone CHECK (guest_phone ~ '^\+?[0-9\s\-()]{7,20}$')
            );
            """
            
            # Create indexes
            create_indexes = """
            CREATE INDEX IF NOT EXISTS idx_hotels_city ON hotels(city);
            CREATE INDEX IF NOT EXISTS idx_hotels_stars ON hotels(stars);
            CREATE INDEX IF NOT EXISTS idx_hotels_active ON hotels(is_active);
            CREATE INDEX IF NOT EXISTS idx_hotel_rooms_hotel_id ON hotel_rooms(hotel_id);
            CREATE INDEX IF NOT EXISTS idx_hotel_rooms_available ON hotel_rooms(is_available);
            CREATE INDEX IF NOT EXISTS idx_hotel_rooms_price ON hotel_rooms(price_per_night);
            CREATE INDEX IF NOT EXISTS idx_hotel_rooms_type ON hotel_rooms(room_type);
            CREATE INDEX IF NOT EXISTS idx_bookings_room_id ON bookings(room_id);
            CREATE INDEX IF NOT EXISTS idx_bookings_dates ON bookings(check_in, check_out);
            CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings(status);
            """
            
            # Create trigger function
            create_trigger_function = """
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
            """
            
            # Create triggers
            create_triggers = """
            DROP TRIGGER IF EXISTS update_hotels_updated_at ON hotels;
            CREATE TRIGGER update_hotels_updated_at BEFORE UPDATE ON hotels
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_hotel_rooms_updated_at ON hotel_rooms;
            CREATE TRIGGER update_hotel_rooms_updated_at BEFORE UPDATE ON hotel_rooms
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
                
            DROP TRIGGER IF EXISTS update_bookings_updated_at ON bookings;
            CREATE TRIGGER update_bookings_updated_at BEFORE UPDATE ON bookings
                FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
            """
            
            # Execute table creation queries
            self.execute_update(create_room_type_enum)
            self.execute_update(create_hotels_table)
            self.execute_update(create_rooms_table)
            self.execute_update(create_bookings_table)
            self.execute_update(create_indexes)
            self.execute_update(create_trigger_function)
            self.execute_update(create_triggers)
            
            print("Tables created successfully!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
