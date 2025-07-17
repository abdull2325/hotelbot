# HotelBot - Hotel Search and Booking Chatbot

A sophisticated hotel search and booking chatbot built with LangGraph, PostgreSQL, and OpenAI's GPT models. The chatbot can help users find hotels, check room availability, and get pricing information.

## 🌟 Features

- **Hotel Search**: Find hotels by city, star rating, price range, or name
- **Room Availability**: Check available rooms with filters for type, capacity, and price
- **Detailed Information**: Get comprehensive hotel details including amenities, contact info, and descriptions
- **Conversational Interface**: Natural language processing for intuitive interactions
- **Memory Management**: Maintains conversation context across multiple queries
- **Parallel Processing**: LangGraph-based architecture for efficient tool execution

## 🏗️ Architecture

### Database Schema (Updated)

The application uses a modern PostgreSQL schema with the following tables:

#### Hotels Table
```sql
CREATE TABLE hotels (
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
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### Hotel Rooms Table
```sql
CREATE TABLE hotel_rooms (
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
```

#### Bookings Table
```sql
CREATE TABLE bookings (
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
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
```

#### Room Types
- `single`: Standard single occupancy room
- `double`: Standard double occupancy room
- `suite`: Premium suite with additional amenities
- `deluxe`: Deluxe room with enhanced features
- `presidential`: Top-tier presidential suite

### LangGraph Architecture

The chatbot uses a sophisticated LangGraph architecture with:

- **State Management**: Maintains conversation context and user information
- **Parallel Tool Execution**: Multiple hotel search operations can run simultaneously
- **Memory Persistence**: Conversation history is preserved across sessions
- **Error Handling**: Robust error handling with graceful degradation

## 🚀 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hotelbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=hotelbot_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   ```

4. **Set up PostgreSQL database**
   ```bash
   createdb hotelbot_db
   ```

5. **Run database migration**
   ```bash
   python migrate_database.py
   ```

## 📊 Usage

### Running the Chatbot

```bash
python chatbot_langgraph.py
```

### Available Commands

- **Search by city**: "Show me hotels in Lahore"
- **Search by rating**: "Find 5-star hotels"
- **Check rooms**: "What rooms are available?"
- **Price range**: "Hotels between $100-200 per night"
- **Hotel details**: "Tell me about Pearl Continental"
- **Room types**: "What room types are available?"

### Administrative Tools

- **View database contents**: `python view_data_new.py`
- **Search specific city**: `python view_data_new.py Lahore`
- **Migrate database**: `python migrate_database.py --migrate`
- **Test chatbot**: `python migrate_database.py --test`

## 🔧 Configuration

### Database Configuration

The database connection is configured through environment variables:

```python
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hotelbot_db
DB_USER=your_username
DB_PASSWORD=your_password
```

### OpenAI Configuration

The chatbot uses OpenAI's GPT-3.5-turbo model. Configure your API key:

```python
OPENAI_API_KEY=your_api_key_here
```

## 🛠️ Development

### Project Structure

```
hotelbot/
├── chatbot_langgraph.py      # Main LangGraph chatbot implementation
├── database.py               # Database connection and operations
├── hotel_search_service.py   # Hotel search logic
├── config.py                 # Configuration management
├── migrate_database.py       # Database migration script
├── schema_migration.sql      # SQL migration script
├── populate_data_new.py      # Sample data population
├── view_data_new.py          # Database viewing utility
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

### Key Components

1. **HotelBotLangGraph**: Main chatbot class with LangGraph integration
2. **HotelBotTools**: Tool implementations for database operations
3. **HotelSearchService**: Business logic for hotel searches
4. **DatabaseConnection**: Database abstraction layer

### Adding New Features

1. **New Tools**: Add tools to the `HotelBotTools` class
2. **New Nodes**: Add processing nodes to the LangGraph workflow
3. **New Queries**: Extend `HotelSearchService` with new search methods

## 🧪 Testing

### Running Tests

```bash
# Test database migration
python migrate_database.py --test

# Test specific functionality
python -c "from chatbot_langgraph import HotelBotLangGraph; bot = HotelBotLangGraph(); print(bot.chat('Test message'))"
```

### Manual Testing

1. Run the chatbot: `python chatbot_langgraph.py`
2. Test various queries:
   - Hotel searches
   - Room availability
   - Price filtering
   - Hotel details

## 🔄 Migration from Old Schema

If you're migrating from the old schema, run:

```bash
python migrate_database.py
```

This will:
1. Drop old tables (`rooms`, `bookings`, `hotels`)
2. Create new tables with updated schema
3. Populate sample data
4. Set up triggers and indexes
5. Test the chatbot functionality

### Key Changes in New Schema

- **Hotels**: Added `stars` (instead of `rating`), `description`, `phone_number`, `email`, `latitude`, `longitude`, `amenities`, `is_active`
- **Rooms**: Renamed to `hotel_rooms`, added `capacity`, `image_urls`, `amenities`, enum `room_type`
- **Bookings**: Added `guest_phone`, `status`, changed date field names
- **Indexes**: Added performance indexes on frequently queried fields
- **Triggers**: Auto-update `updated_at` timestamps

## 📝 API Reference

### HotelBotLangGraph Methods

- `chat(message, thread_id)`: Process a user message
- `reset_memory(thread_id)`: Clear conversation history
- `get_conversation_history(thread_id)`: Get chat history
- `visualize_graph()`: Display graph structure

### Available Tools

- `search_hotels_by_city(city)`: Find hotels in a city
- `search_hotels_by_rating(min_rating)`: Find hotels by star rating
- `get_available_rooms(filters)`: Get available rooms with filters
- `get_room_types_and_prices(hotel_id)`: Get room types and pricing
- `search_hotels_by_price_range(min_price, max_price)`: Price-based search
- `get_hotel_details(hotel_id)`: Get detailed hotel information
- `search_hotel_by_name(hotel_name)`: Search by hotel name

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section below
2. Review the logs for error messages
3. Ensure all environment variables are set correctly
4. Verify database connectivity

### Troubleshooting

- **Database connection issues**: Check PostgreSQL service and credentials
- **OpenAI API errors**: Verify API key and quota
- **Tool execution failures**: Check database schema and data integrity
- **Memory issues**: Reset conversation memory or restart the application

---

Built with ❤️ using LangGraph, PostgreSQL, and OpenAI GPT models.
