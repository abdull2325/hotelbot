#!/usr/bin/env python3
"""
Test script to compare LangChain and LangGraph chatbots
"""

import time
from chatbot import HotelChatbot
from chatbot_langgraph import HotelBotLangGraph

def test_chatbot_responses():
    """Test both chatbots with sample queries"""
    
    print("🏨 Testing Hotel Chatbots - LangChain vs LangGraph 🏨\n")
    
    # Test queries
    test_queries = [
        "Find hotels in New York",
        "Show me hotels with 4+ star rating",
        "What rooms are available under $200?",
        "Tell me about Grand Palace Hotel",
        "Find hotels in Miami"
    ]
    
    try:
        # Initialize both chatbots
        print("Initializing chatbots...")
        langchain_bot = HotelChatbot()
        langgraph_bot = HotelBotLangGraph()
        print("✅ Both chatbots initialized successfully!\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"{'='*60}")
            print(f"Test {i}: {query}")
            print(f"{'='*60}")
            
            # Test LangChain chatbot
            print("\n🔧 LangChain Response:")
            start_time = time.time()
            try:
                lc_response = langchain_bot.chat(query)
                lc_time = time.time() - start_time
                print(f"⏱️  Time: {lc_time:.2f}s")
                print(f"📝 Response: {lc_response[:200]}...")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                lc_time = 0
            
            # Test LangGraph chatbot
            print("\n🔗 LangGraph Response:")
            start_time = time.time()
            try:
                lg_response = langgraph_bot.chat(query)
                lg_time = time.time() - start_time
                print(f"⏱️  Time: {lg_time:.2f}s")
                print(f"📝 Response: {lg_response[:200]}...")
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                lg_time = 0
            
            # Performance comparison
            if lc_time > 0 and lg_time > 0:
                if lg_time < lc_time:
                    print(f"\n🚀 LangGraph was {(lc_time - lg_time):.2f}s faster")
                else:
                    print(f"\n🚀 LangChain was {(lg_time - lc_time):.2f}s faster")
            
            print("\n" + "="*60 + "\n")
        
        # Test memory functionality
        print("Testing Memory Functionality:")
        print("-" * 30)
        
        # Test conversation context
        print("\n🔧 Testing LangChain Memory:")
        langchain_bot.chat("Find hotels in Boston")
        response1 = langchain_bot.chat("What about the first hotel?")
        print(f"Context response: {response1[:100]}...")
        
        print("\n🔗 Testing LangGraph Memory:")
        langgraph_bot.chat("Find hotels in Boston", "test_thread")
        response2 = langgraph_bot.chat("What about the first hotel?", "test_thread")
        print(f"Context response: {response2[:100]}...")
        
        print("\n✅ Testing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print("Please make sure your OpenAI API key is set in the .env file.")

def interactive_comparison():
    """Interactive comparison between both chatbots"""
    
    print("🏨 Interactive Chatbot Comparison 🏨")
    print("Type your query and see responses from both chatbots")
    print("Commands: 'quit' to exit, 'reset' to clear memory, 'switch' to use only one bot")
    print("-" * 60)
    
    try:
        # Initialize both chatbots
        langchain_bot = HotelChatbot()
        langgraph_bot = HotelBotLangGraph()
        
        use_both = True
        thread_id = "interactive_session"
        
        while True:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                langchain_bot.reset_memory()
                langgraph_bot.reset_memory(thread_id)
                print("🔄 Memory cleared for both chatbots!")
                continue
            
            if user_input.lower() == 'switch':
                use_both = not use_both
                mode = "both chatbots" if use_both else "LangGraph only"
                print(f"🔄 Switched to {mode} mode")
                continue
            
            if not user_input:
                continue
            
            if use_both:
                # Show both responses
                print("\n🔧 LangChain Bot:")
                try:
                    lc_response = langchain_bot.chat(user_input)
                    print(f"   {lc_response}")
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
                
                print("\n🔗 LangGraph Bot:")
                try:
                    lg_response = langgraph_bot.chat(user_input, thread_id)
                    print(f"   {lg_response}")
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
            else:
                # Show only LangGraph response
                print("\n🔗 LangGraph Bot:")
                try:
                    lg_response = langgraph_bot.chat(user_input, thread_id)
                    print(f"   {lg_response}")
                except Exception as e:
                    print(f"   ❌ Error: {str(e)}")
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Automated testing")
    print("2. Interactive comparison")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        test_chatbot_responses()
    elif choice == "2":
        interactive_comparison()
    else:
        print("Invalid choice. Running automated testing...")
        test_chatbot_responses()
