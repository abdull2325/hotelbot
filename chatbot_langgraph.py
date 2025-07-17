import os
import json
from typing import List, Dict, Optional, Any, Annotated, TypedDict
from datetime import datetime, date
from dotenv import load_dotenv

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
            
            tools_instance.db.connect()
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
            
            tools_instance.db.disconnect()
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
            HotelBotTools.search_hotel_by_name
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
            system_message = """You are a helpful and friendly hotel booking assistant. Your name is HotelBot. 

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
- Remember the conversation context from previous messages
- When users ask about room types or availability at a specific hotel, use the hotel name or ID from previous search results
- If a user asks about "this hotel" or "that hotel", refer to the most recently mentioned hotel in the conversation
- Always include hotel IDs in search results so users can reference them later
- If a user asks about booking, explain that you can help them find hotels and rooms, but they would need to contact the hotel directly for actual booking
- When showing hotel or room information, include relevant details like prices, ratings, and availability

Remember: When users ask follow-up questions about a specific hotel, use the search_hotel_by_name tool or get_hotel_details with the hotel ID to get current information.

Always be helpful and provide the most relevant information based on the user's needs."""
            
            messages = [{"role": "system", "content": system_message}] + state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        # Define individual tool nodes
        def search_hotels_by_city_node(state: State):
            tool_call = state["messages"][-1].tool_calls[0]
            result = HotelBotTools.search_hotels_by_city.invoke(tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}
        
        def search_hotels_by_rating_node(state: State):
            tool_call = state["messages"][-1].tool_calls[0]
            result = HotelBotTools.search_hotels_by_rating.invoke(tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}
        
        def get_available_rooms_node(state: State):
            tool_call = state["messages"][-1].tool_calls[0]
            result = HotelBotTools.get_available_rooms.invoke(tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}
        
        def get_room_types_and_prices_node(state: State):
            tool_call = state["messages"][-1].tool_calls[0]
            result = HotelBotTools.get_room_types_and_prices.invoke(tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}
        
        def search_hotels_by_price_range_node(state: State):
            tool_call = state["messages"][-1].tool_calls[0]
            result = HotelBotTools.search_hotels_by_price_range.invoke(tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}
        
        def get_hotel_details_node(state: State):
            tool_call = state["messages"][-1].tool_calls[0]
            result = HotelBotTools.get_hotel_details.invoke(tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}
        
        def search_hotel_by_name_node(state: State):
            tool_call = state["messages"][-1].tool_calls[0]
            result = HotelBotTools.search_hotel_by_name.invoke(tool_call["args"])
            return {"messages": [ToolMessage(content=result, tool_call_id=tool_call["id"])]}
        
        # Route to appropriate tool nodes
        def route_tools(state: State):
            """Route to appropriate tool nodes based on tool calls"""
            last_message = state["messages"][-1]
            
            if not last_message.tool_calls:
                return END
            
            # Send to appropriate tool nodes based on tool names
            tool_calls = []
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                if tool_name == "search_hotels_by_city":
                    tool_calls.append(Send("search_hotels_by_city_node", {"messages": [last_message]}))
                elif tool_name == "search_hotels_by_rating":
                    tool_calls.append(Send("search_hotels_by_rating_node", {"messages": [last_message]}))
                elif tool_name == "get_available_rooms":
                    tool_calls.append(Send("get_available_rooms_node", {"messages": [last_message]}))
                elif tool_name == "get_room_types_and_prices":
                    tool_calls.append(Send("get_room_types_and_prices_node", {"messages": [last_message]}))
                elif tool_name == "search_hotels_by_price_range":
                    tool_calls.append(Send("search_hotels_by_price_range_node", {"messages": [last_message]}))
                elif tool_name == "get_hotel_details":
                    tool_calls.append(Send("get_hotel_details_node", {"messages": [last_message]}))
                elif tool_name == "search_hotel_by_name":
                    tool_calls.append(Send("search_hotel_by_name_node", {"messages": [last_message]}))
            
            return tool_calls
        
        # Add nodes to the graph
        workflow.add_node("chatbot", chatbot)
        workflow.add_node("search_hotels_by_city_node", search_hotels_by_city_node)
        workflow.add_node("search_hotels_by_rating_node", search_hotels_by_rating_node)
        workflow.add_node("get_available_rooms_node", get_available_rooms_node)
        workflow.add_node("get_room_types_and_prices_node", get_room_types_and_prices_node)
        workflow.add_node("search_hotels_by_price_range_node", search_hotels_by_price_range_node)
        workflow.add_node("get_hotel_details_node", get_hotel_details_node)
        workflow.add_node("search_hotel_by_name_node", search_hotel_by_name_node)
        
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
        
        # Compile the graph
        return workflow.compile(checkpointer=self.memory)
    
    def chat(self, message: str, thread_id: str = "default") -> str:
        """Main chat method"""
        try:
            # Create the input
            input_message = {"messages": [HumanMessage(content=message)]}
            
            # Configure the thread
            config = {"configurable": {"thread_id": thread_id}}
            
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
    print("I can help you find hotels, check room availability, and get pricing information.")
    print("Type 'quit' to exit, 'reset' to clear conversation history, or 'graph' to see the graph structure.\n")
    
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
