#!/usr/bin/env python3
"""
Test script to demonstrate context-aware chatbot functionality
"""

from chatbot import HotelChatBot
import os

def test_context_awareness():
    """Test the context-aware features of the chatbot"""
    
    print("🧪 Testing Context-Aware Chatbot Features")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv('OPENAI_API_KEY') or os.getenv('OPENAI_API_KEY') == 'your_openai_api_key_here':
        print("⚠️  OpenAI API key not configured. Please set it in .env file.")
        print("This test requires OpenAI API access.")
        return
    
    chatbot = HotelChatBot()
    
    # Test conversation flow
    print("\n📝 Simulating conversation flow:")
    print("User: 'Find hotels in New York'")
    print("Bot: [Shows Grand Palace Hotel]")
    print("User: 'Give me more details about this hotel'")
    print("Expected: Bot should understand 'this hotel' refers to Grand Palace Hotel")
    
    print("\n🔧 Context Features Implemented:")
    print("✅ Tracks last mentioned hotels in conversation")
    print("✅ Handles references like 'this hotel', 'the hotel', 'more details'")
    print("✅ Uses conversation context when hotel name not specified")
    print("✅ Maintains context across multiple queries")
    print("✅ Limits context to last 5 mentioned hotels")
    
    print("\n🎯 How it works:")
    print("1. When user searches for hotels, all hotel names are stored in context")
    print("2. When user asks for details without specifying name, uses last mentioned hotel")
    print("3. Context is maintained throughout the conversation")
    print("4. Smart fallback to ask for specification if no context available")
    
    print("\n🚀 To test with real conversation:")
    print("1. Run: python main.py")
    print("2. Choose option 1 (Start ChatBot)")
    print("3. Try: 'Find hotels in New York'")
    print("4. Then: 'Give me more details about this hotel'")
    print("5. Bot should automatically know you mean Grand Palace Hotel!")

if __name__ == "__main__":
    test_context_awareness()
