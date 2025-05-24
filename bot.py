import requests
import config
import logging
import time
import json
import threading
import sys

# Set up logging to only go to file (completely silent console)
logging.basicConfig(
    level=logging.ERROR,  # Only log errors
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("bot.log")]
)
logger = logging.getLogger("customer_support_bot")
# Disable all logging for requests library too
logging.getLogger("urllib3").setLevel(logging.WARNING)


class TypingIndicator:
    def __init__(self, message="🤖 Bot is typing"):
        self.message = message
        self.is_typing = False
        self.thread = None

    def start(self):
        self.is_typing = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_typing = False
        if self.thread:
            self.thread.join()
        # Clear the line completely
        print('\r' + ' ' * 60 + '\r', end='', flush=True)

    def _animate(self):
        dots = ""
        while self.is_typing:
            for i in range(4):
                if not self.is_typing:
                    break
                dots = "." * i
                print(f'\r{self.message}{dots}   ', end='', flush=True)
                time.sleep(0.4)


class CustomerSupportBot:
    def __init__(self):
        self.api_key = config.COHERE_API_KEY
        if not self.api_key or self.api_key == "your_cohere_api_key_here":
            raise ValueError("Please set a valid Cohere API key in your .env file")

        self.api_url = "https://api.cohere.ai/v1/chat"
        self.conversations = {}
        self.max_retries = 3
        self.typing_indicator = TypingIndicator()

    def create_system_message(self):
        return f"""You are a helpful customer support assistant for {config.COMPANY_NAME}.

INSTRUCTIONS:
- Be friendly, professional, and concise
- Provide clear, actionable answers
- If you don't know something, say so and offer to connect with a human agent
- Keep responses under 3 sentences when possible
- Be specific and helpful

COMPANY INFO:
{config.PRODUCT_INFO}

Always prioritize being helpful and accurate over being verbose."""

    def chat(self, user_message, conversation_id="default", show_typing=True):
        try:
            if conversation_id not in self.conversations:
                self.conversations[conversation_id] = []

            history = self.conversations[conversation_id]

            if show_typing:
                self.typing_indicator.start()

            try:
                response_text = self._generate_response(user_message, history)
            finally:
                if show_typing:
                    self.typing_indicator.stop()

            history.append({"role": "USER", "message": user_message})
            history.append({"role": "CHATBOT", "message": response_text})

            if len(history) > 10:
                history = history[-10:]

            self.conversations[conversation_id] = history
            return response_text

        except Exception:
            if show_typing:
                self.typing_indicator.stop()
            return "I'm sorry, I experienced a technical issue. Please try again."

    def _generate_response(self, user_message, history):
        for attempt in range(self.max_retries):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }

                chat_history = []
                for msg in history[-6:]:
                    chat_history.append({
                        "role": msg["role"],
                        "message": msg["message"]
                    })

                payload = {
                    "model": "command-r",
                    "message": user_message,
                    "chat_history": chat_history,
                    "preamble": self.create_system_message(),
                    "temperature": 0.3,
                    "max_tokens": 200,
                    "connectors": []
                }

                # Small delay to show typing indicator
                time.sleep(0.8)

                response = requests.post(self.api_url, headers=headers, json=payload, timeout=30)

                if response.status_code == 401:
                    return "Authentication error. Please check your API key."

                if response.status_code == 429:
                    time.sleep(2 ** attempt)
                    continue

                if response.status_code != 200:
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    return "I'm having trouble connecting right now. Please try again."

                result = response.json()

                if "text" in result:
                    generated_text = result["text"].strip()
                    return self._clean_response(generated_text)
                else:
                    return "I couldn't process that request. Could you try rephrasing?"

            except requests.exceptions.Timeout:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return "The request took too long. Please try again."

            except requests.exceptions.RequestException:
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return "Connection error. Please try again."

            except Exception:
                return "An unexpected error occurred. Please try again."

        return "I wasn't able to process your request. Please try again later."

    def _clean_response(self, response_text):
        if not response_text:
            return "I'm here to help! Could you please rephrase your question?"

        response = response_text.strip()

        unwanted_patterns = ["Assistant:", "Customer:", "Human:", "AI:", "Bot:", "Chatbot:"]
        for pattern in unwanted_patterns:
            if response.lower().startswith(pattern.lower()):
                response = response[len(pattern):].strip()

        if not response:
            return "I'm here to help! Could you please rephrase your question?"

        if response and not response.endswith(('.', '!', '?', ':')):
            response += '.'

        if len(response) > 500:
            response = response[:500].rsplit(' ', 1)[0] + '...'

        return response

    def stream_response(self, response_text, delay=0.02):
        """Stream response with typewriter effect"""
        for char in response_text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()

    def chat_with_effects(self, user_message, conversation_id="default", stream_output=True):
        """Clean chat with visual effects"""
        response = self.chat(user_message, conversation_id, show_typing=True)

        if stream_output:
            print("Bot: ", end='', flush=True)
            self.stream_response(response)
        else:
            print(f"Bot: {response}")

        return response


# Simple usage example
if __name__ == "__main__":
    try:
        bot = CustomerSupportBot()
        print("🤖 Customer Support Bot Ready!")
        print("Type 'quit' to exit\n")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ['quit', 'exit']:
                print("Bot: Goodbye! 👋")
                break

            if user_input.strip():
                bot.chat_with_effects(user_input)

    except Exception as e:
        print(f"Error starting bot: {e}")