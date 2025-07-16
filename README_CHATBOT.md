# HotelBot - LangChain-Powered Hotel Booking Assistant 🏨

A sophisticated chatbot built with LangChain that helps users search for hotels, check room availability, and get pricing information through natural language conversation.

## Features

- 🤖 **Natural Language Processing**: Powered by OpenAI's GPT-3.5-turbo with LangChain
- 💭 **Memory Management**: Remembers conversation context for seamless interactions
- 🔧 **Multiple Tools**: Comprehensive database tools for hotel and room searches
- 🌐 **Web Interface**: Beautiful Streamlit web interface
- 📱 **Command Line Interface**: Terminal-based chat interface
- 🗄️ **PostgreSQL Integration**: Robust database connectivity
- 🔍 **Advanced Search**: Search by city, rating, price range, room type, and more

## Architecture

```
HotelBot System Architecture

User Input → LangChain Agent → Tools → PostgreSQL Database
     ↓              ↓            ↓           ↓
Web/CLI Interface → Memory → Results → Response Generation
```

## Tools Available

1. **search_hotels_by_city** - Find hotels in specific cities
2. **search_hotels_by_rating** - Filter hotels by minimum rating
3. **get_available_rooms** - Check room availability with filters
4. **get_room_types_and_prices** - Get room types and pricing information
5. **search_hotels_by_price_range** - Find hotels within budget
6. **get_hotel_details** - Get detailed hotel information

## Setup

### 1. Environment Variables

Create a `.env` file in the project root:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=hotelbot
DB_USER=your_username
DB_PASSWORD=your_password

# OpenAI API Key (required for chatbot)
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Make sure your PostgreSQL database is running and populated with hotel data.

```bash
# Run the database setup (if needed)
python populate_data.py
```

## Usage

### Command Line Interface

```bash
python chatbot.py
```

### Web Interface (Streamlit)

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

### Testing

```bash
# Test the chatbot tools
python test_chatbot_complete.py
```

## Example Conversations

### Basic Hotel Search
```
User: I'm looking for hotels in New York
Bot: Found 5 hotels in New York:

🏨 **Grand Central Hotel**
   📍 123 Park Avenue, New York, NY
   ⭐ Rating: 4.5/5.0
   🏠 Total Rooms: 150
   ✅ Available Rooms: 45

[Additional hotels...]
```

### Room Availability Check
```
User: Show me available suite rooms under $300
Bot: Found 3 available rooms:

🏠 **Room 501** - Executive Suite
   🏨 Hotel: Luxury Plaza Hotel
   📍 Location: Manhattan
   💰 Price: $275/night
   🆔 Room ID: 23

[Additional rooms...]
```

### Price Range Search
```
User: Find me budget hotels with rooms under $150
Bot: Found 8 hotels with rooms in $50 - $150 range:

🏨 **Budget Inn Downtown**
   📍 Brooklyn, NY
   ⭐ Rating: 3.5/5.0
   💰 Room Price Range: $89.00 - $149.00
   🏠 Available Rooms: 23

[Additional hotels...]
```

## Configuration

Customize the chatbot behavior in `config.py`:

```python
CHATBOT_CONFIG = {
    "temperature": 0.7,        # Response creativity (0-1)
    "model": "gpt-3.5-turbo",  # OpenAI model
    "memory_window": 10,       # Conversation memory
    "max_tokens": 1000,        # Response length
    "verbose": True            # Debug output
}
```

## Database Schema

The chatbot works with three main tables:

- **hotels**: Hotel information (name, location, rating)
- **rooms**: Room details (type, price, availability)
- **bookings**: Booking records (for context)

## API Integration

The chatbot uses these main services:

- **OpenAI API**: For natural language processing
- **PostgreSQL**: For data storage and retrieval
- **LangChain**: For agent orchestration and memory management

## Memory Management

The chatbot maintains conversation context using LangChain's `ConversationBufferWindowMemory`:

- Remembers last 10 exchanges by default
- Maintains context across tool calls
- Can be reset with `reset` command

## Error Handling

The chatbot includes comprehensive error handling:

- Database connection failures
- API rate limiting
- Invalid user inputs
- Tool execution errors

## Deployment

### Local Development
```bash
# Start the CLI chatbot
python chatbot.py

# Start the web interface
streamlit run streamlit_app.py
```

### Production Deployment
1. Set up environment variables
2. Configure database connection
3. Deploy using your preferred platform (Heroku, AWS, etc.)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your improvements
4. Submit a pull request

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Make sure `OPENAI_API_KEY` is set in your `.env` file
   - Get an API key from https://platform.openai.com/api-keys

2. **Database connection errors**
   - Check your PostgreSQL server is running
   - Verify database credentials in `.env`
   - Ensure database and tables exist

3. **Tool execution failures**
   - Check database connectivity
   - Verify table schema matches expected format
   - Check for data in the tables

### Debug Mode

Enable verbose logging by setting `verbose=True` in the agent executor or running:

```bash
export LANGCHAIN_VERBOSE=true
python chatbot.py
```

## License

MIT License - feel free to use and modify as needed.

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review the conversation logs
3. Test individual tools using the test script
4. Open an issue in the repository

---

**Happy Hotel Hunting! 🏨✨**
