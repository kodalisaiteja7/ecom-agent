"""
Demo script to showcase the E-Commerce AI Agent without manual interaction.
This demonstrates the agent's capabilities programmatically.
"""
import asyncio
import os
from simple_agent import SimpleEcommerceAgent as EcommerceAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def demo():
    """Run a demonstration of the agent's capabilities."""

    print("\n" + "=" * 70)
    print("E-COMMERCE AI CUSTOMER SUPPORT - AUTOMATED DEMO")
    print("=" * 70)
    print("\nThis demo showcases the agent's CRUD capabilities:\n")

    # Initialize agent
    agent = EcommerceAgent()

    # Demo conversations
    demos = [
        {
            "title": "1. READ Operation - Searching for Products",
            "messages": [
                "Show me all electronics under $500"
            ]
        },
        {
            "title": "2. READ Operation - Checking Orders",
            "messages": [
                "Can you show me all orders?"
            ]
        },
        {
            "title": "3. CREATE Operation - Creating an Order (with confirmation)",
            "messages": [
                "I want to order 1 Wireless Mouse for Alice Johnson",
                "yes"
            ]
        },
        {
            "title": "4. UPDATE Operation - Updating Order Status (with confirmation)",
            "messages": [
                "Update order ORD-1002 to Shipped status",
                "confirm"
            ]
        },
        {
            "title": "5. Intent Adaptation - Changing Intent Mid-Conversation",
            "messages": [
                "Show me all products",
                "Actually, I want to update the price of USB-C Hub to 44.99",
                "no, cancel that"
            ]
        }
    ]

    for demo in demos:
        print("\n" + "=" * 70)
        print(demo["title"])
        print("=" * 70 + "\n")

        for i, user_msg in enumerate(demo["messages"]):
            print(f"User: {user_msg}")

            try:
                response = await agent.process_message(user_msg)
                print(f"\nAssistant: {response}\n")

                # Add a small delay between messages for readability
                await asyncio.sleep(0.5)

            except Exception as e:
                print(f"Error: {str(e)}\n")
                break

        # Reset agent between demos for clean state
        if demo != demos[-1]:  # Don't reset after last demo
            agent.reset()
            await asyncio.sleep(1)

    print("\n" + "=" * 70)
    print("DEMO COMPLETED!")
    print("=" * 70)
    print("\nTo try it yourself interactively, run:")
    print("  py chat_interface.py")
    print("\nor double-click:")
    print("  run.bat")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\nERROR: OPENAI_API_KEY environment variable not set!")
        print("Please check your .env file.\n")
        exit(1)

    try:
        asyncio.run(demo())
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!\n")
    except Exception as e:
        print(f"\nError running demo: {e}\n")