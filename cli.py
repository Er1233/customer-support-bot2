# cli.py
# Command-line interface for testing the bot

from bot import CustomerSupportBot


def run_cli():
    """Simple command-line interface for testing the bot"""
    print("Customer Support Bot CLI")
    print("Type 'exit' to quit")
    print("-" * 50)

    bot = CustomerSupportBot()
    conversation_id = "cli-session"

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            print("Thank you for using the Customer Support Bot!")
            break

        try:
            response = bot.chat(user_input, conversation_id)
            print(f"\nBot: {response}")
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    run_cli()