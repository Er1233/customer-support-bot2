# human_fallback.py
# Simple human agent fallback system

import re
import logging
import time
from datetime import datetime
import json

logger = logging.getLogger("human_fallback")


class HumanFallbackHandler:
    def __init__(self):
        # Keywords that trigger human agent fallback
        self.trigger_keywords = [
            # Purchase/Sales related
            'buy', 'purchase', 'price', 'cost', 'pricing', 'quote', 'demo', 'trial',
            'sales', 'sell', 'order', 'payment', 'billing', 'invoice', 'contract',

            # Human agent requests
            'human', 'agent', 'person', 'representative', 'speak to someone',
            'talk to human', 'real person', 'customer service', 'support team',

            # Complex issues
            'urgent', 'emergency', 'complaint', 'refund', 'cancel', 'problem',
            'issue', 'help me', 'technical support', 'not working', 'broken'
        ]

        # Phrases that indicate need for human intervention
        self.trigger_phrases = [
            'speak to a human',
            'talk to someone',
            'human agent',
            'real person',
            'customer service',
            'I want to buy',
            'how much does it cost',
            'get a quote',
            'schedule a demo',
            'technical issue',
            'not satisfied',
            'cancel my',
            'refund my'
        ]

        # Store conversations flagged for human review
        self.flagged_conversations = {}

    def should_transfer_to_human(self, message):
        """
        Check if message should be transferred to human agent
        Returns: (should_transfer: bool, reason: str)
        """
        message_lower = message.lower().strip()

        # Check for direct phrases first
        for phrase in self.trigger_phrases:
            if phrase in message_lower:
                return True, f"Phrase detected: '{phrase}'"

        # Check for individual keywords
        words = re.findall(r'\b\w+\b', message_lower)
        triggered_keywords = [word for word in words if word in self.trigger_keywords]

        if triggered_keywords:
            # Multiple keywords increase confidence
            if len(triggered_keywords) >= 2:
                return True, f"Multiple keywords: {', '.join(triggered_keywords)}"

            # Single strong keywords
            strong_keywords = ['buy', 'purchase', 'human', 'agent', 'urgent', 'complaint']
            if any(keyword in triggered_keywords for keyword in strong_keywords):
                return True, f"Strong keyword: {triggered_keywords[0]}"

        return False, None

    def flag_conversation(self, conversation_id, user_message, reason):
        """Flag conversation for human agent review"""
        timestamp = datetime.now().isoformat()

        self.flagged_conversations[conversation_id] = {
            'timestamp': timestamp,
            'user_message': user_message,
            'reason': reason,
            'status': 'waiting_for_agent',
            'urgency': self.get_urgency_level(user_message)
        }

        # Log for human agent notification
        logger.info(f"HUMAN AGENT NEEDED - Conv: {conversation_id}, Reason: {reason}")

        # Here you could integrate with:
        # - Email notifications
        # - Slack/Teams alerts
        # - Ticketing systems
        # - SMS notifications

    def get_urgency_level(self, message):
        """Determine urgency level of the request"""
        message_lower = message.lower()

        urgent_keywords = ['urgent', 'emergency', 'asap', 'immediately', 'critical']
        high_keywords = ['complaint', 'angry', 'frustrated', 'disappointed']

        if any(word in message_lower for word in urgent_keywords):
            return 'urgent'
        elif any(word in message_lower for word in high_keywords):
            return 'high'
        else:
            return 'normal'

    def get_human_transfer_message(self, reason_category):
        """Get appropriate message for human transfer"""
        messages = {
            'sales': """I'll connect you with our sales team for detailed pricing and demos! 

📞 **Immediate Help:**
• Call: +1 (555) 123-4567
• Email: sales@mshauritech.com
• Book a demo: [Schedule here]

A sales representative will contact you within 1 hour during business hours (9 AM - 6 PM EAT).""",

            'support': """I'm connecting you with a human support specialist who can better assist you.

👨‍💼 **Human Support:**
• Live chat will connect shortly
• Email: support@mshauritech.com  
• Phone: +1 (555) 123-4567

Expected response time: 15-30 minutes during business hours.""",

            'technical': """This requires our technical team's expertise. I'm escalating this for you.

🔧 **Technical Support:**
• Priority ticket created
• Email: tech@mshauritech.com
• Your ticket ID: #{ticket_id}

A technical specialist will reach out within 2 hours.""",

            'general': """I'm connecting you with a human agent who can provide more personalized assistance.

💬 **Human Agent:**
• Transferring now...
• Email: hello@mshauritech.com
• Phone: +1 (555) 123-4567

Please hold while I connect you."""
        }

        return messages.get(reason_category, messages['general'])

    def categorize_request(self, message, reason):
        """Categorize the type of human assistance needed"""
        message_lower = message.lower()

        sales_keywords = ['buy', 'purchase', 'price', 'cost', 'quote', 'demo', 'sales']
        technical_keywords = ['technical', 'not working', 'broken', 'error', 'bug']

        if any(word in message_lower for word in sales_keywords):
            return 'sales'
        elif any(word in message_lower for word in technical_keywords):
            return 'technical'
        elif 'support' in message_lower or 'help' in message_lower:
            return 'support'
        else:
            return 'general'


# Integration with your existing bot.py
def add_fallback_to_existing_bot():
    """
    Add this method to your CustomerSupportBot class in bot.py
    """

    # Add to CustomerSupportBot.__init__():
    # self.fallback_handler = HumanFallbackHandler()

    # Modify the chat() method to include this check:
    def chat_with_fallback(self, user_message, conversation_id="default", show_typing=True):
        """Modified chat method with human fallback"""

        # Check if message should go to human first
        should_transfer, reason = self.fallback_handler.should_transfer_to_human(user_message)

        if should_transfer:
            # Flag conversation for human agent
            self.fallback_handler.flag_conversation(conversation_id, user_message, reason)

            # Categorize and respond appropriately
            category = self.fallback_handler.categorize_request(user_message, reason)
            return self.fallback_handler.get_human_transfer_message(category)

        # Continue with regular AI response
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
            return "I'm sorry, I experienced a technical issue. Let me connect you with a human agent."


# Simple notification system (optional)
def send_agent_notification(conversation_data):
    """Send notification to human agents - customize based on your setup"""

    # Email notification example
    def send_email_alert():
        subject = f"Human Agent Needed - {conversation_data['urgency'].upper()} Priority"
        body = f"""
        New conversation needs human attention:

        Conversation ID: {conversation_data.get('conversation_id')}
        Timestamp: {conversation_data['timestamp']}
        User Message: {conversation_data['user_message']}
        Reason: {conversation_data['reason']}
        Urgency: {conversation_data['urgency']}

        Please respond promptly.
        """
        # Implement your email sending logic here
        pass

    # Slack notification example
    def send_slack_alert():
        slack_message = {
            "text": f"🚨 Human Agent Needed - {conversation_data['urgency'].upper()} Priority",
            "attachments": [{
                "color": "warning",
                "fields": [
                    {"title": "Message", "value": conversation_data['user_message'], "short": False},
                    {"title": "Reason", "value": conversation_data['reason'], "short": True},
                    {"title": "Urgency", "value": conversation_data['urgency'], "short": True}
                ]
            }]
        }
        # Implement your Slack webhook logic here
        pass


# Usage example:
if __name__ == "__main__":
    fallback = HumanFallbackHandler()

    # Test messages
    test_messages = [
        "I want to buy your product",
        "Can I speak to a human?",
        "What's the pricing for your service?",
        "I need technical support",
        "How does your AI work?"
    ]

    for msg in test_messages:
        should_transfer, reason = fallback.should_transfer_to_human(msg)
        print(f"Message: '{msg}'")
        print(f"Transfer to human: {should_transfer}")
        if should_transfer:
            print(f"Reason: {reason}")
            category = fallback.categorize_request(msg, reason)
            print(f"Category: {category}")
        print("-" * 50)