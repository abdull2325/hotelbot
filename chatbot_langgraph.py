import os
import json
import re
from typing import List, Dict, Optional, Any, Annotated, TypedDict
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

from langchain_openai import ChatOpenAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableConfig

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send

from database import DatabaseConnection
from hotel_search_service import HotelSearchService

# Load environment variables
load_dotenv(override=True)

# Define the state of our graph
class State(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    user_info: Dict[str, Any]  # Store user preferences, last searched hotels, etc.

class HotelBotTools:
    """Tools for the hotel chatbot to interact with the database"""
    
    def __init__(self):
        self.search_service = HotelSearchService()
        self.search_service.connect()
    
    def __del__(self):
        """Cleanup database connections"""
        try:
            self.search_service.disconnect()
        except:
            pass

    @tool
    def search_hotels_by_city(city: str) -> str:
        """Search for hotels in a specific city. Use this when user asks about hotels in a particular location."""
        try:
            tools_instance = HotelBotTools()
            hotels = tools_instance.search_service.search_hotels_by_city(city)
            
            if not hotels:
                return f"No hotels found in {city}. Please try another city."
            
            result = f"Found {len(hotels)} hotels in {city}:\n\n"
            for hotel in hotels:
                result += f"🏨 **{hotel['name']}** (Hotel ID: {hotel['id']})\n"
                result += f"   📍 {hotel['address']}, {hotel['city']}\n"
                result += f"   ⭐ Stars: {hotel['stars']}/5\n"
                if hotel.get('description'):
                    result += f"   📝 {hotel['description']}\n"
                result += f"   🏠 Total Rooms: {hotel['total_rooms']}\n"
                result += f"   ✅ Available Rooms: {hotel['available_rooms']}\n"
                if hotel.get('amenities'):
                    result += f"   🎯 Amenities: {', '.join(hotel['amenities'])}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error searching hotels: {str(e)}"
    
    @tool
    def search_hotels_by_rating(min_rating: str) -> str:
        """Search for hotels with minimum rating. Rating should be between 1.0 and 5.0."""
        try:
            rating = float(min_rating)
            if rating < 1.0 or rating > 5.0:
                return "Rating must be between 1.0 and 5.0"
            
            tools_instance = HotelBotTools()
            hotels = tools_instance.search_service.search_hotels_by_rating(rating)
            
            if not hotels:
                return f"No hotels found with rating {rating} or higher."
            
            result = f"Found {len(hotels)} hotels with {rating}+ stars:\n\n"
            for hotel in hotels:
                result += f"🏨 **{hotel['name']}** (Hotel ID: {hotel['id']})\n"
                result += f"   📍 {hotel['city']}\n"
                result += f"   ⭐ Stars: {hotel['stars']}/5\n"
                if hotel.get('description'):
                    result += f"   📝 {hotel['description']}\n"
                result += f"   🏠 Available Rooms: {hotel['available_rooms']}\n"
                if hotel.get('amenities'):
                    result += f"   🎯 Amenities: {', '.join(hotel['amenities'])}\n"
                result += "\n"
            
            return result
            
        except ValueError:
            return "Invalid rating format. Please provide a number between 1.0 and 5.0"
        except Exception as e:
            return f"Error searching hotels by rating: {str(e)}"
    
    @tool
    def get_available_rooms(filters: str = "") -> str:
        """Get available rooms with optional filters. Pass filters as a string like 'hotel_id:1,room_type:single,max_price:200'"""
        try:
            tools_instance = HotelBotTools()
            
            # Parse filters
            hotel_id_int = None
            room_type = None
            max_price_float = None
            
            if filters:
                for filter_item in filters.split(','):
                    if ':' in filter_item:
                        key, value = filter_item.split(':', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'hotel_id' and value.isdigit():
                            hotel_id_int = int(value)
                        elif key == 'room_type':
                            room_type = value
                        elif key == 'max_price':
                            try:
                                max_price_float = float(value)
                            except ValueError:
                                pass
            
            rooms = tools_instance.search_service.get_available_rooms(
                hotel_id=hotel_id_int,
                room_type=room_type,
                max_price=max_price_float
            )
            
            if not rooms:
                return "No available rooms found with the specified criteria."
            
            result = f"Found {len(rooms)} available rooms:\n\n"
            for room in rooms:
                result += f"🏠 **Room {room['room_number']}** - {room['room_type']}\n"
                result += f"   🏨 Hotel: {room['hotel_name']}\n"
                result += f"   📍 Location: {room['city']}\n"
                result += f"   💰 Price: ${room['price_per_night']}/night\n"
                result += f"   👥 Capacity: {room['capacity']} guests\n"
                result += f"   🆔 Room ID: {room['id']}\n"
                if room.get('amenities'):
                    result += f"   🎯 Amenities: {', '.join(room['amenities'])}\n"
                result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error fetching available rooms: {str(e)}"
    
    @tool
    def get_room_types_and_prices(hotel_id: str = "") -> str:
        """Get room types and their price ranges. Optionally filter by hotel_id."""
        try:
            tools_instance = HotelBotTools()
            
            hotel_id_int = int(hotel_id) if hotel_id and hotel_id.isdigit() else None
            
            room_types = tools_instance.search_service.get_room_types_and_prices(hotel_id_int)
            
            if not room_types:
                return "No room types found."
            
            result = "Available room types and prices:\n\n"
            for room_type in room_types:
                result += f"🏠 **{room_type['room_type']}**\n"
                if hotel_id_int:
                    result += f"   🏨 Hotel: {room_type['hotel_name']}\n"
                else:
                    result += f"   🏨 Hotel: {room_type['hotel_name']} ({room_type['city']})\n"
                result += f"   📊 Available: {room_type['available_count']} rooms\n"
                result += f"   💰 Price Range: ${room_type['min_price']:.2f} - ${room_type['max_price']:.2f}\n"
                result += f"   📈 Average Price: ${room_type['avg_price']:.2f}/night\n\n"
            
            return result
            
        except Exception as e:
            return f"Error fetching room types: {str(e)}"
    
    @tool
    def search_hotels_by_price_range(min_price: str, max_price: str) -> str:
        """Search hotels with rooms in a specific price range per night."""
        try:
            min_price_float = float(min_price)
            max_price_float = float(max_price)
            
            if min_price_float > max_price_float:
                return "Minimum price cannot be greater than maximum price."
            
            tools_instance = HotelBotTools()
            hotels = tools_instance.search_service.search_hotels_by_price_range(min_price_float, max_price_float)
            
            if not hotels:
                return f"No hotels found with rooms in the price range ${min_price} - ${max_price}."
            
            result = f"Found {len(hotels)} hotels with rooms in ${min_price} - ${max_price} range:\n\n"
            for hotel in hotels:
                result += f"🏨 **{hotel['name']}**\n"
                result += f"   📍 {hotel['city']}\n"
                result += f"   ⭐ Stars: {hotel['stars']}/5\n"
                if hotel.get('description'):
                    result += f"   📝 {hotel['description']}\n"
                result += f"   💰 Room Price Range: ${hotel['min_room_price']:.2f} - ${hotel['max_room_price']:.2f}\n"
                result += f"   🏠 Available Rooms: {hotel['total_rooms']}\n"
                if hotel.get('amenities'):
                    result += f"   🎯 Amenities: {', '.join(hotel['amenities'])}\n"
                result += "\n"
            
            return result
            
        except ValueError:
            return "Invalid price format. Please provide valid numbers."
        except Exception as e:
            return f"Error searching hotels by price range: {str(e)}"
    
    @tool
    def get_hotel_details(hotel_id: str) -> str:
        """Get detailed information about a specific hotel including all its rooms."""
        try:
            hotel_id_int = int(hotel_id)
            
            tools_instance = HotelBotTools()
            
            # Get hotel info using service layer
            hotel = tools_instance.search_service.get_hotel_by_id(hotel_id_int)
            
            if not hotel:
                return f"Hotel with ID {hotel_id} not found."
            
            # Get room details
            rooms = tools_instance.search_service.get_available_rooms(hotel_id=hotel_id_int)
            
            result = f"🏨 **{hotel['name']}** (ID: {hotel['id']})\n"
            result += f"📍 Address: {hotel['address']}, {hotel['city']}\n"
            result += f"⭐ Stars: {hotel['stars']}/5\n"
            if hotel.get('description'):
                result += f"📝 Description: {hotel['description']}\n"
            if hotel.get('phone_number'):
                result += f"📞 Phone: {hotel['phone_number']}\n"
            if hotel.get('email'):
                result += f"📧 Email: {hotel['email']}\n"
            result += f"🏠 Total Rooms: {hotel['total_rooms']}\n"
            result += f"✅ Available Rooms: {hotel['available_rooms']}\n"
            if hotel.get('amenities'):
                result += f"🎯 Amenities: {', '.join(hotel['amenities'])}\n"
            result += "\n"
            
            if rooms:
                result += "**Available Rooms:**\n"
                for room in rooms:
                    result += f"  • Room {room['room_number']} ({room['room_type']}) - ${room['price_per_night']}/night (Capacity: {room['capacity']})\n"
            else:
                result += "No rooms currently available.\n"
            
            return result
            
        except ValueError:
            return "Invalid hotel ID format. Please provide a valid number."
        except Exception as e:
            return f"Error fetching hotel details: {str(e)}"

    @tool
    def search_hotel_by_name(hotel_name: str) -> str:
        """Search for a hotel by its name and get its details and available rooms."""
        try:
            tools_instance = HotelBotTools()
            
            # Search for hotel by name using service layer
            hotel = tools_instance.search_service.search_hotel_by_name(hotel_name)
            
            if not hotel:
                return f"No hotel found with name '{hotel_name}'. Please try a different name or search by city."
            
            # Get available rooms for this hotel
            rooms = tools_instance.search_service.get_available_rooms(hotel_id=hotel['id'])
            
            result = f"🏨 **{hotel['name']}** (Hotel ID: {hotel['id']})\n"
            result += f"📍 Address: {hotel['address']}, {hotel['city']}\n"
            result += f"⭐ Stars: {hotel['stars']}/5\n"
            if hotel.get('description'):
                result += f"📝 Description: {hotel['description']}\n"
            if hotel.get('phone_number'):
                result += f"📞 Phone: {hotel['phone_number']}\n"
            if hotel.get('email'):
                result += f"📧 Email: {hotel['email']}\n"
            result += f"🏠 Total Rooms: {hotel['total_rooms']}\n"
            result += f"✅ Available Rooms: {hotel['available_rooms']}\n"
            if hotel.get('amenities'):
                result += f"🎯 Amenities: {', '.join(hotel['amenities'])}\n"
            result += "\n"
            
            if rooms:
                result += "**Available Room Types:**\n"
                room_types = {}
                for room in rooms:
                    room_type = room['room_type']
                    if room_type not in room_types:
                        room_types[room_type] = []
                    room_types[room_type].append(room)
                
                for room_type, type_rooms in room_types.items():
                    result += f"\n🏠 **{room_type}** ({len(type_rooms)} available)\n"
                    for room in type_rooms[:3]:  # Show first 3 rooms of each type
                        result += f"  • Room {room['room_number']} - ${room['price_per_night']}/night (Capacity: {room['capacity']})\n"
                    if len(type_rooms) > 3:
                        result += f"  • ... and {len(type_rooms) - 3} more {room_type} rooms\n"
            else:
                result += "No rooms currently available at this hotel.\n"
            
            return result
            
        except Exception as e:
            return f"Error searching hotel by name: {str(e)}"

    @tool
    def check_room_availability_by_dates(room_id: str, check_in_date: str, check_out_date: str) -> str:
        """Check if a specific room is available for given dates. Dates should be in YYYY-MM-DD format."""
        try:
            tools_instance = HotelBotTools()
            
            # Parse dates
            try:
                check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-12-25)."
            
            # Validate dates
            if check_in >= check_out:
                return "Check-out date must be after check-in date."
            
            if check_in < date.today():
                return "Check-in date cannot be in the past."
            
            room_id_int = int(room_id)
            
            tools_instance = HotelBotTools()
            
            # First check if room exists and is generally available
            room = tools_instance.search_service.get_room_by_id(room_id_int)
            
            if not room:
                return f"Room with ID {room_id} not found or not available."
            
            # Check for conflicting bookings
            conflict_count = tools_instance.search_service.check_booking_conflict(room_id_int, check_in, check_out)
            
            if conflict_count > 0:
                return f"❌ Room {room['room_number']} at {room['hotel_name']} is not available for {check_in_date} to {check_out_date}. Please choose different dates or another room."
            
            # Calculate stay details
            nights = (check_out - check_in).days
            total_cost = float(room['price_per_night']) * nights
            
            result = f"✅ Room {room['room_number']} at {room['hotel_name']} is available!\n\n"
            result += f"📅 Check-in: {check_in_date}\n"
            result += f"📅 Check-out: {check_out_date}\n"
            result += f"🛏️ Nights: {nights}\n"
            result += f"🏠 Room Type: {room['room_type']}\n"
            result += f"👥 Capacity: {room['capacity']} guests\n"
            result += f"💰 Price per night: ${room['price_per_night']}\n"
            result += f"💵 Total cost: ${total_cost:.2f}\n\n"
            result += f"🏨 Hotel: {room['hotel_name']}\n"
            result += f"📍 Location: {room['address']}, {room['city']}\n"
            if room.get('phone_number'):
                result += f"📞 Phone: {room['phone_number']}\n"
            result += f"\nTo book this room, use the book_room tool with room_id: {room_id}"
            
            return result
            
        except ValueError:
            return "Invalid room ID format. Please provide a valid number."
        except Exception as e:
            return f"Error checking room availability: {str(e)}"

    @tool
    def book_room(room_id: str, guest_name: str, guest_email: str, guest_phone: str, check_in_date: str, check_out_date: str) -> str:
        """Book a room for a guest. All parameters are required. Dates should be in YYYY-MM-DD format."""
        try:
            tools_instance = HotelBotTools()
            
            # Validate inputs
            if not all([room_id, guest_name, guest_email, guest_phone, check_in_date, check_out_date]):
                return "All booking details are required: room_id, guest_name, guest_email, guest_phone, check_in_date, check_out_date."
            
            # Validate email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, guest_email):
                return "Invalid email format. Please provide a valid email address."
            
            # Validate phone format
            phone_pattern = r'^\+?[0-9\s\-()]{7,20}$'
            if not re.match(phone_pattern, guest_phone):
                return "Invalid phone format. Please provide a valid phone number."
            
            # Parse dates
            try:
                check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-12-25)."
            
            # Validate dates
            if check_in >= check_out:
                return "Check-out date must be after check-in date."
            
            if check_in < date.today():
                return "Check-in date cannot be in the past."
            
            room_id_int = int(room_id)
            
            tools_instance = HotelBotTools()
            
            # Check if room is still available for the requested dates
            room = tools_instance.search_service.get_room_by_id(room_id_int)
            
            if not room:
                return f"Room with ID {room_id} not found or not available."
            
            # Check for conflicting bookings
            conflict_count = tools_instance.search_service.check_booking_conflict(room_id_int, check_in, check_out)
            
            if conflict_count > 0:
                return f"❌ Room {room['room_number']} at {room['hotel_name']} is not available for {check_in_date} to {check_out_date}. Please choose different dates or another room."

            
            # Calculate booking details
            nights = (check_out - check_in).days
            total_amount = float(room['price_per_night']) * nights
            
            # Create booking using service layer
            booking_id = tools_instance.search_service.create_booking(
                room_id_int, guest_name, guest_email, guest_phone, check_in, check_out, total_amount
            )
            
            if not booking_id:
                return "Error creating booking. Please try again."
            
            # Update room availability if booking is for current dates
            if check_in <= date.today() <= check_out:
                tools_instance.search_service.update_room_availability(room_id_int, False)
            
            # Generate booking confirmation
            result = f"🎉 Booking Confirmed! 🎉\n\n"
            result += f"📋 Booking ID: {booking_id}\n"
            result += f"👤 Guest: {guest_name}\n"
            result += f"📧 Email: {guest_email}\n"
            result += f"📞 Phone: {guest_phone}\n\n"
            result += f"🏨 Hotel: {room['hotel_name']}\n"
            result += f"📍 Address: {room['address']}, {room['city']}\n"
            result += f"🏠 Room: {room['room_number']} ({room['room_type']})\n"
            result += f"👥 Capacity: {room['capacity']} guests\n\n"
            result += f"📅 Check-in: {check_in_date}\n"
            result += f"📅 Check-out: {check_out_date}\n"
            result += f"🛏️ Nights: {nights}\n"
            result += f"💰 Rate: ${room['price_per_night']}/night\n"
            result += f"💵 Total Amount: ${total_amount:.2f}\n\n"
            if room.get('hotel_email'):
                result += f"For any inquiries, contact the hotel at {room['hotel_email']}"
                if room.get('phone_number'):
                    result += f" or {room['phone_number']}"
            result += f"\n\nThank you for choosing {room['hotel_name']}! 🌟"
            
            return result
            
        except ValueError:
            return "Invalid room ID format. Please provide a valid number."
        except Exception as e:
            return f"Error booking room: {str(e)}"

    @tool
    def get_booking_details(booking_id: str) -> str:
        """Get details of a specific booking by booking ID."""
        try:
            tools_instance = HotelBotTools()
            booking_id_int = int(booking_id)
            
            booking = tools_instance.search_service.get_booking_by_id(booking_id_int)
            
            if not booking:
                return f"Booking with ID {booking_id} not found."
            
            # Calculate nights
            nights = (booking['check_out'] - booking['check_in']).days
            
            result = f"📋 Booking Details (ID: {booking_id})\n\n"
            result += f"👤 Guest: {booking['guest_name']}\n"
            result += f"📧 Email: {booking['guest_email']}\n"
            result += f"📞 Phone: {booking['guest_phone']}\n\n"
            result += f"🏨 Hotel: {booking['hotel_name']}\n"
            result += f"📍 Address: {booking['address']}, {booking['city']}\n"
            result += f"🏠 Room: {booking['room_number']} ({booking['room_type']})\n"
            result += f"👥 Capacity: {booking['capacity']} guests\n\n"
            result += f"📅 Check-in: {booking['check_in']}\n"
            result += f"📅 Check-out: {booking['check_out']}\n"
            result += f"🛏️ Nights: {nights}\n"
            result += f"💰 Rate: ${booking['price_per_night']}/night\n"
            result += f"💵 Total Amount: ${booking['total_amount']:.2f}\n"
            result += f"📊 Status: {booking['status'].upper()}\n"
            result += f"📅 Booked on: {booking['created_at'].strftime('%Y-%m-%d %H:%M')}\n\n"
            
            if booking.get('hotel_email'):
                result += f"For inquiries, contact: {booking['hotel_email']}"
                if booking.get('phone_number'):
                    result += f" or {booking['phone_number']}"
            
            return result
            
        except ValueError:
            return "Invalid booking ID format. Please provide a valid number."
        except Exception as e:
            return f"Error retrieving booking details: {str(e)}"

    @tool
    def cancel_booking(booking_id: str, reason: str = "Guest requested") -> str:
        """Cancel a booking by booking ID. Optionally provide a reason for cancellation."""
        try:
            tools_instance = HotelBotTools()
            booking_id_int = int(booking_id)
            
            # Get booking details first
            booking = tools_instance.search_service.get_confirmed_booking_by_id(booking_id_int)
            
            if not booking:
                return f"Booking with ID {booking_id} not found or already cancelled."
            
            # Update booking status
            tools_instance.search_service.cancel_booking(booking_id_int)
            
            # If booking was for current dates, make room available again
            if booking['check_in'] <= date.today() <= booking['check_out']:
                tools_instance.search_service.update_room_availability(booking['room_id'], True)
            
            result = f"❌ Booking Cancelled\n\n"
            result += f"📋 Booking ID: {booking_id}\n"
            result += f"👤 Guest: {booking['guest_name']}\n"
            result += f"🏨 Hotel: {booking['hotel_name']}\n"
            result += f"🏠 Room: {booking['room_number']} ({booking['room_type']})\n"
            result += f"📅 Original dates: {booking['check_in']} to {booking['check_out']}\n"
            result += f"💵 Refund amount: ${booking['total_amount']:.2f}\n"
            result += f"📝 Reason: {reason}\n\n"
            result += f"The booking has been successfully cancelled. "
            
            if booking['check_in'] > date.today():
                result += f"The room is now available for other guests."
            
            return result
            
        except ValueError:
            return "Invalid booking ID format. Please provide a valid number."
        except Exception as e:
            return f"Error cancelling booking: {str(e)}"

    @tool
    def search_available_rooms_by_dates(city: str, check_in_date: str, check_out_date: str, room_type: str = "", max_price: str = "") -> str:
        """Search for available rooms in a city for specific dates. Room type and max price are optional filters."""
        try:
            tools_instance = HotelBotTools()
            
            # Parse dates
            try:
                check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
                check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
            except ValueError:
                return "Invalid date format. Please use YYYY-MM-DD format (e.g., 2024-12-25)."
            
            # Validate dates
            if check_in >= check_out:
                return "Check-out date must be after check-in date."
            
            if check_in < date.today():
                return "Check-in date cannot be in the past."
            
            # Parse optional filters
            room_type_filter = room_type if room_type else None
            max_price_filter = None
            if max_price:
                try:
                    max_price_filter = float(max_price)
                except ValueError:
                    pass
            
            # Search for available rooms using service layer
            rooms = tools_instance.search_service.search_available_rooms_by_dates(
                city, check_in, check_out, room_type_filter, max_price_filter
            )
            
            if not rooms:
                return f"No available rooms found in {city} for {check_in_date} to {check_out_date}."
            
            # Calculate stay details
            nights = (check_out - check_in).days
            
            result = f"Found {len(rooms)} available rooms in {city} for {check_in_date} to {check_out_date} ({nights} nights):\n\n"
            
            for room in rooms:
                total_cost = float(room['price_per_night']) * nights
                
                result += f"🏨 **{room['hotel_name']}** ({room['stars']} stars)\n"
                result += f"   📍 {room['address']}, {room['city']}\n"
                result += f"   🏠 Room {room['room_number']} - {room['room_type']}\n"
                result += f"   👥 Capacity: {room['capacity']} guests\n"
                result += f"   💰 ${room['price_per_night']}/night × {nights} nights = ${total_cost:.2f}\n"
                result += f"   🆔 Room ID: {room['id']}\n"
                if room.get('amenities'):
                    result += f"   🎯 Amenities: {', '.join(room['amenities'])}\n"
                result += f"   📋 To book: use room_id {room['id']}\n\n"
            
            return result
            
        except Exception as e:
            return f"Error searching available rooms: {str(e)}"


class HotelBotLangGraph:
    """LangGraph-based hotel chatbot with improved state management"""
    
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0.7,
            model="gpt-3.5-turbo",
            openai_api_key=self.openai_api_key
        )
        
        # Initialize tools
        self.tools = [
            HotelBotTools.search_hotels_by_city,
            HotelBotTools.search_hotels_by_rating,
            HotelBotTools.get_available_rooms,
            HotelBotTools.get_room_types_and_prices,
            HotelBotTools.search_hotels_by_price_range,
            HotelBotTools.get_hotel_details,
            HotelBotTools.search_hotel_by_name,
            HotelBotTools.check_room_availability_by_dates,
            HotelBotTools.book_room,
            HotelBotTools.get_booking_details,
            HotelBotTools.cancel_booking,
            HotelBotTools.search_available_rooms_by_dates
        ]
        
        # Create the LLM with tools
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Initialize memory
        self.memory = MemorySaver()
        
        # Build the graph
        self.app = self._build_graph()
    
    def _build_graph(self):
        """Build the LangGraph workflow"""
        
        # Create the graph
        workflow = StateGraph(State)
        
        # Define the chatbot node
        def chatbot(state: State):
            """Main chatbot logic"""
            current_date = date.today().strftime("%Y-%m-%d")
            system_message = f"""You are a helpful and friendly hotel booking assistant. Your name is HotelBot. 

Today's date is {current_date}.

You have access to a comprehensive hotel database and can help users:
- Search for hotels in specific cities
- Find hotels by rating/stars
- Check room availability and types
- Get price information
- Provide detailed hotel information
- Search for specific hotels by name
- Check room availability for specific dates
- Book rooms for guests
- View booking details
- Cancel bookings
- Search for available rooms by dates and location

Booking Process Guidelines:
- When users want to book a room, collect ALL required information: room_id, guest_name, guest_email, guest_phone, check_in_date, check_out_date
- Always check room availability for specific dates before booking
- Use YYYY-MM-DD format for dates (e.g., 2025-07-25)
- Validate that check-in date is not in the past and check-out is after check-in
- After booking, provide complete confirmation details including booking ID
- For date searches, ask users for their preferred check-in and check-out dates
- Always show total cost calculations (price per night × number of nights)

General Guidelines:
- Be conversational and friendly
- Ask clarifying questions when needed
- Provide detailed, helpful responses
- Use emojis to make responses more engaging
- Remember the conversation context from previous messages
- When users ask about room types or availability at a specific hotel, use the hotel name or ID from previous search results
- If a user asks about "this hotel" or "that hotel", refer to the most recently mentioned hotel in the conversation
- Always include hotel IDs and room IDs in search results so users can reference them later
- When showing hotel or room information, include relevant details like prices, ratings, and availability
- For booking confirmations, provide booking ID and all relevant details

Date Format: Always use YYYY-MM-DD format for dates (e.g., 2025-07-25, 2025-08-01)

Remember: When users ask follow-up questions about a specific hotel, use the search_hotel_by_name tool or get_hotel_details with the hotel ID to get current information.

Always be helpful and provide the most relevant information based on the user's needs."""
            
            messages = [{"role": "system", "content": system_message}] + state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        # Define individual tool nodes - each handles multiple calls of the same tool in parallel
        def search_hotels_by_city_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "search_hotels_by_city"]
            results = []
            
            if not tool_calls:
                return {"messages": []}
            
            # Execute multiple calls of the same tool in parallel using ThreadPoolExecutor
            def execute_tool_call(tool_call):
                try:
                    result = HotelBotTools.search_hotels_by_city.invoke(tool_call["args"])
                    return ToolMessage(content=result, tool_call_id=tool_call["id"])
                except Exception as e:
                    return ToolMessage(content=f"Error: {str(e)}", tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=min(len(tool_calls), 5)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def search_hotels_by_rating_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "search_hotels_by_rating"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.search_hotels_by_rating.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def get_available_rooms_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "get_available_rooms"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.get_available_rooms.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def get_room_types_and_prices_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "get_room_types_and_prices"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.get_room_types_and_prices.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def search_hotels_by_price_range_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "search_hotels_by_price_range"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.search_hotels_by_price_range.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def get_hotel_details_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "get_hotel_details"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.get_hotel_details.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def search_hotel_by_name_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "search_hotel_by_name"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.search_hotel_by_name.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def check_room_availability_by_dates_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "check_room_availability_by_dates"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.check_room_availability_by_dates.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def book_room_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "book_room"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.book_room.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def get_booking_details_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "get_booking_details"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.get_booking_details.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def cancel_booking_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "cancel_booking"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.cancel_booking.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        
        def search_available_rooms_by_dates_node(state: State):
            tool_calls = [tc for tc in state["messages"][-1].tool_calls if tc["name"] == "search_available_rooms_by_dates"]
            results = []
            
            def execute_tool_call(tool_call):
                result = HotelBotTools.search_available_rooms_by_dates.invoke(tool_call["args"])
                return ToolMessage(content=result, tool_call_id=tool_call["id"])
            
            with ThreadPoolExecutor(max_workers=len(tool_calls)) as executor:
                future_to_tool = {executor.submit(execute_tool_call, tc): tc for tc in tool_calls}
                for future in as_completed(future_to_tool):
                    results.append(future.result())
            
            return {"messages": results}
        # Route to appropriate tool nodes
        def route_tools(state: State):
            """Route to appropriate tool nodes based on tool calls - enables parallel execution"""
            last_message = state["messages"][-1]
            
            if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
                return END
            
            # Group tool calls by tool name to enable parallel execution
            tool_groups = {}
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                if tool_name not in tool_groups:
                    tool_groups[tool_name] = []
                tool_groups[tool_name].append(tool_call)
            
            # Send each group to appropriate tool nodes for parallel execution
            sends = []
            for tool_name, tool_calls in tool_groups.items():
                # Create a message with only the tool calls for this specific tool
                try:
                    tool_message = last_message.model_copy()
                    tool_message.tool_calls = tool_calls
                except Exception:
                    # Fallback if model_copy fails
                    tool_message = last_message
                
                if tool_name == "search_hotels_by_city":
                    sends.append(Send("search_hotels_by_city_node", {"messages": [tool_message]}))
                elif tool_name == "search_hotels_by_rating":
                    sends.append(Send("search_hotels_by_rating_node", {"messages": [tool_message]}))
                elif tool_name == "get_available_rooms":
                    sends.append(Send("get_available_rooms_node", {"messages": [tool_message]}))
                elif tool_name == "get_room_types_and_prices":
                    sends.append(Send("get_room_types_and_prices_node", {"messages": [tool_message]}))
                elif tool_name == "search_hotels_by_price_range":
                    sends.append(Send("search_hotels_by_price_range_node", {"messages": [tool_message]}))
                elif tool_name == "get_hotel_details":
                    sends.append(Send("get_hotel_details_node", {"messages": [tool_message]}))
                elif tool_name == "search_hotel_by_name":
                    sends.append(Send("search_hotel_by_name_node", {"messages": [tool_message]}))
                elif tool_name == "check_room_availability_by_dates":
                    sends.append(Send("check_room_availability_by_dates_node", {"messages": [tool_message]}))
                elif tool_name == "book_room":
                    sends.append(Send("book_room_node", {"messages": [tool_message]}))
                elif tool_name == "get_booking_details":
                    sends.append(Send("get_booking_details_node", {"messages": [tool_message]}))
                elif tool_name == "cancel_booking":
                    sends.append(Send("cancel_booking_node", {"messages": [tool_message]}))
                elif tool_name == "search_available_rooms_by_dates":
                    sends.append(Send("search_available_rooms_by_dates_node", {"messages": [tool_message]}))
            
            return sends if sends else END
        
        # Add nodes to the graph
        workflow.add_node("chatbot", chatbot)
        workflow.add_node("search_hotels_by_city_node", search_hotels_by_city_node)
        workflow.add_node("search_hotels_by_rating_node", search_hotels_by_rating_node)
        workflow.add_node("get_available_rooms_node", get_available_rooms_node)
        workflow.add_node("get_room_types_and_prices_node", get_room_types_and_prices_node)
        workflow.add_node("search_hotels_by_price_range_node", search_hotels_by_price_range_node)
        workflow.add_node("get_hotel_details_node", get_hotel_details_node)
        workflow.add_node("search_hotel_by_name_node", search_hotel_by_name_node)
        workflow.add_node("check_room_availability_by_dates_node", check_room_availability_by_dates_node)
        workflow.add_node("book_room_node", book_room_node)
        workflow.add_node("get_booking_details_node", get_booking_details_node)
        workflow.add_node("cancel_booking_node", cancel_booking_node)
        workflow.add_node("search_available_rooms_by_dates_node", search_available_rooms_by_dates_node)
        
        # Add edges
        workflow.add_edge(START, "chatbot")
        workflow.add_conditional_edges("chatbot", route_tools)
        
        # All tool nodes return to chatbot
        workflow.add_edge("search_hotels_by_city_node", "chatbot")
        workflow.add_edge("search_hotels_by_rating_node", "chatbot")
        workflow.add_edge("get_available_rooms_node", "chatbot")
        workflow.add_edge("get_room_types_and_prices_node", "chatbot")
        workflow.add_edge("search_hotels_by_price_range_node", "chatbot")
        workflow.add_edge("get_hotel_details_node", "chatbot")
        workflow.add_edge("search_hotel_by_name_node", "chatbot")
        workflow.add_edge("check_room_availability_by_dates_node", "chatbot")
        workflow.add_edge("book_room_node", "chatbot")
        workflow.add_edge("get_booking_details_node", "chatbot")
        workflow.add_edge("cancel_booking_node", "chatbot")
        workflow.add_edge("search_available_rooms_by_dates_node", "chatbot")
        
        # Compile the graph
        return workflow.compile(checkpointer=self.memory)
    
    def chat(self, message: str, thread_id: str = "default") -> str:
        """Main chat method"""
        try:
            # Create the input
            input_message = {"messages": [HumanMessage(content=message)]}
            
            # Configure the thread with recursion limit
            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": 50  # Increase recursion limit
            }
            
            # Run the graph
            result = self.app.invoke(input_message, config)
            
            # Return the last message content
            return result["messages"][-1].content
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or rephrase your question."
    
    def reset_memory(self, thread_id: str = "default"):
        """Reset the conversation memory for a specific thread"""
        try:
            # Clear the memory for this thread
            config = {"configurable": {"thread_id": thread_id}}
            # Since MemorySaver doesn't have a direct clear method, we'll create a new thread
            # by simply using a new thread_id in future conversations
            return f"Memory cleared for thread {thread_id}"
        except Exception as e:
            return f"Error clearing memory: {str(e)}"
    
    def get_conversation_history(self, thread_id: str = "default") -> List[BaseMessage]:
        """Get the current conversation history for a thread"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            # Get the current state
            current_state = self.app.get_state(config)
            return current_state.values.get("messages", [])
        except Exception as e:
            print(f"Error getting conversation history: {str(e)}")
            return []
    
    def visualize_graph(self):
        """Print the graph structure (for debugging)"""
        try:
            from langgraph.graph import Graph
            print("Graph structure:")
            print("Nodes:", list(self.app.get_graph().nodes.keys()))
            print("Edges:", list(self.app.get_graph().edges))
        except Exception as e:
            print(f"Error visualizing graph: {str(e)}")


def main():
    """Main function to run the LangGraph chatbot"""
    print("🏨 Welcome to HotelBot (LangGraph Edition)! 🏨")
    print("I can help you find hotels, check room availability, get pricing information, and book rooms!")
    print("Available features:")
    print("  • Search hotels by city, rating, or price range")
    print("  • Check room availability for specific dates")
    print("  • Book rooms (I'll collect all your details)")
    print("  • View and cancel bookings")
    print("  • Get detailed hotel information")
    print("\nType 'quit' to exit, 'reset' to clear conversation history, or 'graph' to see the graph structure.\n")
    
    try:
        # Initialize chatbot
        chatbot = HotelBotLangGraph()
        thread_id = "user_session_1"  # You can use different thread IDs for different users
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("🤖 HotelBot: Thank you for using HotelBot! Have a great day! 🌟")
                break
            
            if user_input.lower() == 'reset':
                chatbot.reset_memory(thread_id)
                thread_id = f"user_session_{datetime.now().timestamp()}"  # Create new thread
                print("🤖 HotelBot: Conversation history cleared! How can I help you today? 😊")
                continue
            
            if user_input.lower() == 'graph':
                chatbot.visualize_graph()
                continue
            
            if not user_input:
                continue
            
            # Get response from chatbot
            response = chatbot.chat(user_input, thread_id)
            print(f"🤖 HotelBot: {response}\n")
            
    except KeyboardInterrupt:
        print("\n🤖 HotelBot: Goodbye! 👋")
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        print("Please make sure your OpenAI API key is set in the .env file.")


if __name__ == "__main__":
    main()
