
import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from dotenv import load_dotenv

from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

from database import DatabaseConnection
from hotel_search_service import HotelSearchService

# Load environment variables
load_dotenv(override=True)

class HotelBotTools:
    """Tools for the hotel chatbot to interact with the database"""
    
    def __init__(self):
        self.search_service = HotelSearchService()
        self.db = DatabaseConnection()
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
                result += f"   📍 {hotel['address']}, {hotel['city']}, {hotel['country']}\n"
                result += f"   ⭐ Rating: {hotel['rating']}/5.0\n"
                result += f"   🏠 Total Rooms: {hotel['total_rooms']}\n"
                result += f"   ✅ Available Rooms: {hotel['available_rooms']}\n\n"
            
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
            
            result = f"Found {len(hotels)} hotels with rating {rating}+ stars:\n\n"
            for hotel in hotels:
                result += f"🏨 **{hotel['name']}** (Hotel ID: {hotel['id']})\n"
                result += f"   📍 {hotel['city']}, {hotel['country']}\n"
                result += f"   ⭐ Rating: {hotel['rating']}/5.0\n"
                result += f"   🏠 Available Rooms: {hotel['available_rooms']}\n\n"
            
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
                result += f"   🆔 Room ID: {room['id']}\n\n"
            
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
                result += f"   📍 {hotel['city']}, {hotel['country']}\n"
                result += f"   ⭐ Rating: {hotel['rating']}/5.0\n"
                result += f"   💰 Room Price Range: ${hotel['min_room_price']:.2f} - ${hotel['max_room_price']:.2f}\n"
                result += f"   🏠 Available Rooms: {hotel['total_rooms']}\n\n"
            
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
            
            # Get hotel info
            hotel_query = """
            SELECT h.*, 
                   COUNT(r.id) as total_rooms,
                   COUNT(CASE WHEN r.is_available = true THEN 1 END) as available_rooms
            FROM hotels h
            LEFT JOIN rooms r ON h.id = r.hotel_id
            WHERE h.id = %s
            GROUP BY h.id, h.name, h.address, h.city, h.country, h.rating, h.created_at;
            """
            
            hotels = tools_instance.db.execute_query(hotel_query, (hotel_id_int,))
            
            if not hotels:
                return f"Hotel with ID {hotel_id} not found."
            
            hotel = hotels[0]
            
            # Get room details
            rooms = tools_instance.search_service.get_available_rooms(hotel_id=hotel_id_int)
            
            result = f"🏨 **{hotel['name']}** (ID: {hotel['id']})\n"
            result += f"📍 Address: {hotel['address']}, {hotel['city']}, {hotel['country']}\n"
            result += f"⭐ Rating: {hotel['rating']}/5.0\n"
            result += f"🏠 Total Rooms: {hotel['total_rooms']}\n"
            result += f"✅ Available Rooms: {hotel['available_rooms']}\n\n"
            
            if rooms:
                result += "**Available Rooms:**\n"
                for room in rooms:
                    result += f"  • Room {room['room_number']} ({room['room_type']}) - ${room['price_per_night']}/night\n"
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
            
            # Search for hotel by name
            search_query = """
            SELECT h.*, 
                   COUNT(r.id) as total_rooms,
                   COUNT(CASE WHEN r.is_available = true THEN 1 END) as available_rooms
            FROM hotels h
            LEFT JOIN rooms r ON h.id = r.hotel_id
            WHERE LOWER(h.name) LIKE LOWER(%s)
            GROUP BY h.id, h.name, h.address, h.city, h.country, h.rating, h.created_at;
            """
            
            tools_instance.db.connect()
            hotels = tools_instance.db.execute_query(search_query, (f"%{hotel_name}%",))
            
            if not hotels:
                return f"No hotel found with name '{hotel_name}'. Please try a different name or search by city."
            
            hotel = hotels[0]
            
            # Get available rooms for this hotel
            rooms = tools_instance.search_service.get_available_rooms(hotel_id=hotel['id'])
            
            result = f"🏨 **{hotel['name']}** (Hotel ID: {hotel['id']})\n"
            result += f"📍 Address: {hotel['address']}, {hotel['city']}, {hotel['country']}\n"
            result += f"⭐ Rating: {hotel['rating']}/5.0\n"
            result += f"🏠 Total Rooms: {hotel['total_rooms']}\n"
            result += f"✅ Available Rooms: {hotel['available_rooms']}\n\n"
            
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
                        result += f"  • Room {room['room_number']} - ${room['price_per_night']}/night\n"
                    if len(type_rooms) > 3:
                        result += f"  • ... and {len(type_rooms) - 3} more {room_type} rooms\n"
            else:
                result += "No rooms currently available at this hotel.\n"
            
            tools_instance.db.disconnect()
            return result
            
        except Exception as e:
            return f"Error searching hotel by name: {str(e)}"


class HotelChatbot:
    """Main chatbot class with memory and LangChain integration"""
    
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
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            k=10,  # Remember last 10 exchanges
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize tools
        self.tools = [
            HotelBotTools.search_hotels_by_city,
            HotelBotTools.search_hotels_by_rating,
            HotelBotTools.get_available_rooms,
            HotelBotTools.get_room_types_and_prices,
            HotelBotTools.search_hotels_by_price_range,
            HotelBotTools.get_hotel_details,
            HotelBotTools.search_hotel_by_name
        ]
        
        # Create prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful and friendly hotel booking assistant. Your name is HotelBot. 

You have access to a comprehensive hotel database and can help users:
- Search for hotels in specific cities
- Find hotels by rating
- Check room availability and types
- Get price information
- Provide detailed hotel information
- Search for specific hotels by name

Guidelines:
- Be conversational and friendly
- Ask clarifying questions when needed
- Provide detailed, helpful responses
- Use emojis to make responses more engaging
- Remember the conversation context
- When users ask about room types or availability at a specific hotel, use the hotel name or ID from previous search results
- If a user asks about "this hotel" or "that hotel", refer to the most recently mentioned hotel in the conversation
- Always include hotel IDs in search results so users can reference them later
- If a user asks about booking, explain that you can help them find hotels and rooms, but they would need to contact the hotel directly for actual booking
- When showing hotel or room information, include relevant details like prices, ratings, and availability

Remember: When users ask follow-up questions about a specific hotel, use the search_hotel_by_name tool or get_hotel_details with the hotel ID to get current information.

Always be helpful and provide the most relevant information based on the user's needs."""),
            
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        # Create agent executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def chat(self, message: str) -> str:
        """Main chat method"""
        try:
            response = self.agent_executor.invoke({"input": message})
            return response["output"]
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again or rephrase your question."
    
    def reset_memory(self):
        """Reset the conversation memory"""
        self.memory.clear()
    
    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the current conversation history"""
        return self.memory.chat_memory.messages


def main():
    """Main function to run the chatbot"""
    print("🏨 Welcome to HotelBot! 🏨")
    print("I can help you find hotels, check room availability, and get pricing information.")
    print("Type 'quit' to exit or 'reset' to clear conversation history.\n")
    
    try:
        # Initialize chatbot
        chatbot = HotelChatbot()
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("HotelBot: Thank you for using HotelBot! Have a great day! 🌟")
                break
            
            if user_input.lower() == 'reset':
                chatbot.reset_memory()
                print("HotelBot: Conversation history cleared! How can I help you today? 😊")
                continue
            
            if not user_input:
                continue
            
            # Get response from chatbot
            response = chatbot.chat(user_input)
            print(f"HotelBot: {response}\n")
            
    except KeyboardInterrupt:
        print("\nHotelBot: Goodbye! 👋")
    except Exception as e:
        print(f"Error initializing chatbot: {str(e)}")
        print("Please make sure your OpenAI API key is set in the .env file.")


if __name__ == "__main__":
    main()
