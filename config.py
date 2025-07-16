"""
Configuration file for HotelBot
"""

# Chatbot Configuration
CHATBOT_CONFIG = {
    "temperature": 0.7,
    "model": "gpt-3.5-turbo",
    "memory_window": 10,  # Number of previous exchanges to remember
    "max_tokens": 1000,
    "verbose": True  # Set to False for production
}

# Database Configuration
DATABASE_CONFIG = {
    "connection_timeout": 30,
    "query_timeout": 60,
    "retry_attempts": 3
}

# Tool Configuration
TOOL_CONFIG = {
    "max_results_per_search": 10,
    "default_room_filters": {
        "available_only": True,
        "sort_by": "price_asc"
    }
}

# Response Templates
RESPONSE_TEMPLATES = {
    "greeting": "Hello! I'm HotelBot 🏨, your friendly hotel booking assistant. How can I help you find the perfect hotel today?",
    "goodbye": "Thank you for using HotelBot! Have a wonderful stay! 🌟",
    "no_results": "I couldn't find any hotels matching your criteria. Would you like to try different search parameters?",
    "error": "I apologize, but I encountered an issue. Please try again or rephrase your question.",
    "booking_info": "I can help you find hotels and rooms, but for actual booking, you'll need to contact the hotel directly or use their booking system."
}

# Available room types (for validation)
ROOM_TYPES = [
    "single",
    "double",
    "twin",
    "suite",
    "deluxe",
    "standard",
    "premium",
    "family",
    "executive"
]

# Supported cities (you can expand this based on your database)
SUPPORTED_CITIES = [
    "New York",
    "Los Angeles",
    "Chicago",
    "Houston",
    "Phoenix",
    "Philadelphia",
    "San Antonio",
    "San Diego",
    "Dallas",
    "San Jose"
]
