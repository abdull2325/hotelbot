# HotelBot - AI-Powered Hotel Booking System

A Python-based hotel booking system with PostgreSQL database integration and an AI-powered chatbot using LangChain.

## Features

- **Database Management**: PostgreSQL database connectivity with hotel, room, and booking management
- **AI Chatbot**: LangChain-powered chatbot for natural language hotel search and booking assistance
- **Hotel Search**: Search hotels by city, rating, price range, and availability
- **Room Management**: Check room availability, types, and pricing
- **Comprehensive Data**: Pre-populated with realistic hotel and booking data
- **Interactive Interface**: Command-line interface with menu options

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database server
- OpenAI API key (for chatbot functionality)
- pip (Python package manager)

## Installation

1. Clone or download this project
2. Navigate to the project directory
3. Create a virtual environment (already configured)
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Database Setup

1. Install PostgreSQL on your system
2. Create a new database for the project:
   ```sql
   CREATE DATABASE hotelbot_db;
   ```
3. Update the `.env` file with your database credentials:
   ```
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=hotelbot_db
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

### OpenAI API Setup (for Chatbot)

1. Get an OpenAI API key from [OpenAI Platform](https://platform.openai.com/)
2. Add it to your `.env` file:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Main Application

Run the main application with menu options:
```bash
python main.py
```

**Menu Options:**
1. **🤖 Start Interactive ChatBot** - Launch the AI-powered hotel search assistant
2. **🔍 View Database Contents** - Display formatted database contents
3. **📊 Test Database Connection** - Test database connectivity
4. **🚪 Exit** - Exit the application

### Populate Database with Sample Data

```bash
python populate_data.py
```

This will create:
- 10 hotels across major US cities
- 190+ rooms with various types and pricing
- 100+ realistic bookings

### View Database Contents

```bash
python view_data.py
```

### Test Chatbot Backend

```bash
python test_chatbot.py
```

## Chatbot Capabilities

The AI chatbot can help users with:

- **🏨 Hotel Search**: "Find hotels in New York"
- **⭐ Rating Filter**: "Show me hotels with 4+ star rating"
- **💰 Price Search**: "Find hotels under $200 per night"
- **🏠 Room Availability**: "What rooms are available at Grand Palace Hotel?"
- **🛏️ Room Types**: "Show me all suite rooms"
- **📍 City Information**: "Tell me about hotels in Miami"
- **🔍 Specific Hotels**: "Give me details about Boutique Hotel"

### Example Chatbot Conversations

```
You: Find hotels in San Francisco
🤖 HotelBot: Found 1 hotels in San Francisco:
🏨 Boutique Hotel
   📍 147 Trendy Ave
   ⭐ Rating: 4.6/5.0
   🏠 Total Rooms: 27
   ✅ Available Rooms: 27

You: What rooms are available under $200?
🤖 HotelBot: Found 59 available rooms under $200...
```

## Project Structure

```
hotelbot/
├── main.py                     # Main application with menu
├── chatbot.py                  # LangChain-powered chatbot
├── hotel_search_service.py     # Database search service
├── database.py                 # Database connection and operations
├── populate_data.py            # Database population script
├── view_data.py               # Database content viewer
├── test_chatbot.py            # Chatbot testing script
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables
├── .github/
│   └── copilot-instructions.md
└── README.md                  # This file
```

## Database Schema

### Hotels Table
- `id`: Primary key
- `name`: Hotel name
- `address`: Hotel address
- `city`: City location
- `country`: Country location
- `rating`: Hotel rating (0-5)
- `created_at`: Timestamp

### Rooms Table
- `id`: Primary key
- `hotel_id`: Foreign key to hotels table
- `room_number`: Room identifier
- `room_type`: Type of room (Standard, Deluxe, Suite, Executive, Penthouse)
- `price_per_night`: Room price
- `is_available`: Availability status
- `created_at`: Timestamp

### Bookings Table
- `id`: Primary key
- `room_id`: Foreign key to rooms table
- `guest_name`: Guest name
- `guest_email`: Guest email
- `check_in_date`: Check-in date
- `check_out_date`: Check-out date
- `total_amount`: Total booking amount
- `created_at`: Timestamp

## Technologies Used

- **Backend**: Python 3.8+
- **Database**: PostgreSQL with psycopg2
- **AI Framework**: LangChain
- **LLM**: OpenAI GPT-3.5-turbo
- **Environment**: python-dotenv
- **Data**: Realistic hotel and booking data

## API Capabilities

The chatbot uses these search functions:
- `search_hotels_by_city(city)` - Find hotels in specific cities
- `search_hotels_by_rating(min_rating)` - Find highly-rated hotels
- `search_hotels_by_price_range(min_price, max_price)` - Find hotels within budget
- `get_available_rooms(hotel_name, room_type, max_price)` - Check room availability
- `get_hotel_details(hotel_name)` - Get comprehensive hotel information
- `get_city_summary(city)` - Get city accommodation overview

## Next Steps

Extend the system by:
- **Web Interface**: Build a Flask/Django web application
- **Booking System**: Add actual booking functionality
- **Payment Integration**: Integrate payment processing
- **User Authentication**: Add user accounts and profiles
- **Email Notifications**: Send booking confirmations
- **Mobile App**: Create a mobile interface
- **Advanced Search**: Add more search filters and sorting
- **Reviews System**: Add guest reviews and ratings
- **Analytics Dashboard**: Create admin analytics

## Troubleshooting

### Database Connection Issues
1. Verify PostgreSQL is running: `brew services start postgresql`
2. Check database credentials in `.env`
3. Ensure the database exists: `createdb hotelbot_db`

### Chatbot Issues
1. Verify OpenAI API key is set in `.env`
2. Check API key validity and billing status
3. Ensure all LangChain packages are installed

### General Issues
1. Activate virtual environment: `source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (3.8+ required)

## License

This project is for educational and demonstration purposes.
