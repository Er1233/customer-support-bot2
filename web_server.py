from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import logging
from bot import CustomerSupportBot

# Set up logging for web server
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("web_server.log")]
)
logger = logging.getLogger("web_server")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the bot
try:
    bot = CustomerSupportBot()
    logger.info("Bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    bot = None


@app.route('/')
def index():
    """Serve the demo HTML page"""
    html_content = '''<!DOCTYPE html>
<html>
<head>
    <title>Mshauri Tech - AI Customer Support Demo</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            max-width: 800px; 
            margin: 20px auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .chat-box { 
            border: 1px solid #ddd; 
            height: 500px; 
            overflow-y: scroll; 
            padding: 15px; 
            background: #fafafa;
            border-radius: 8px;
            margin-bottom: 15px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: 20%;
            text-align: right;
        }
        .bot-message {
            background: #e9ecef;
            color: #333;
            margin-right: 20%;
        }
        .typing-indicator {
            background: #e9ecef;
            color: #666;
            margin-right: 20%;
            font-style: italic;
        }
        .input-container {
            display: flex;
            gap: 10px;
        }
        .input-box { 
            flex: 1;
            padding: 12px; 
            border: 1px solid #ddd;
            border-radius: 6px;
            font-size: 16px;
        }
        .send-btn { 
            padding: 12px 24px; 
            background: #007bff; 
            color: white; 
            border: none; 
            border-radius: 6px;
            cursor: pointer;
            font-size: 16px;
        }
        .send-btn:hover {
            background: #0056b3;
        }
        .send-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            border-radius: 6px;
        }
        .status.online {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.offline {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Mshauri Tech - AI Customer Support</h1>
        <div id="status" class="status online">Bot is online and ready to help!</div>
        <div id="chat-box" class="chat-box">
            <div class="message bot-message">
                <strong>Support Bot:</strong> Hello! I'm here to help you with any questions about Mshauri Tech products and services. How can I assist you today?
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="message-input" class="input-box" placeholder="Type your message here..." maxlength="500">
            <button onclick="sendMessage()" id="send-btn" class="send-btn">Send</button>
        </div>
    </div>

    <script>
        let isTyping = false;

        async function sendMessage() {
            const input = document.getElementById('message-input');
            const chatBox = document.getElementById('chat-box');
            const sendBtn = document.getElementById('send-btn');

            const message = input.value.trim();
            if (!message || isTyping) return;

            // Disable input while processing
            isTyping = true;
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';

            // Add user message to chat
            addMessage('user', message);
            input.value = '';

            // Add typing indicator
            const typingId = addTypingIndicator();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: message, 
                        conversation_id: 'web_demo'
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                // Remove typing indicator
                removeTypingIndicator(typingId);

                if (data.success) {
                    addMessage('bot', data.response);
                } else {
                    addMessage('bot', data.error || 'Sorry, I encountered an error. Please try again.');
                }

            } catch (error) {
                console.error('Error:', error);
                removeTypingIndicator(typingId);
                addMessage('bot', 'Sorry, I could not connect to the support system. Please try again later.');
                updateStatus(false);
            }

            // Re-enable input
            isTyping = false;
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            input.focus();
        }

        function addMessage(sender, text) {
            const chatBox = document.getElementById('chat-box');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;

            const label = sender === 'user' ? 'You' : 'Support Bot';
            messageDiv.innerHTML = `<strong>${label}:</strong> ${escapeHtml(text)}`;

            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        function addTypingIndicator() {
            const chatBox = document.getElementById('chat-box');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message typing-indicator';
            typingDiv.id = 'typing-' + Date.now();
            typingDiv.innerHTML = '<strong>Support Bot:</strong> <span id="typing-dots">typing</span>';

            chatBox.appendChild(typingDiv);
            chatBox.scrollTop = chatBox.scrollHeight;

            // Animate typing dots
            animateTypingDots(typingDiv.id);

            return typingDiv.id;
        }

        function removeTypingIndicator(typingId) {
            const typingDiv = document.getElementById(typingId);
            if (typingDiv) {
                typingDiv.remove();
            }
        }

        function animateTypingDots(typingId) {
            const typingDiv = document.getElementById(typingId);
            if (!typingDiv) return;

            const dotsSpan = typingDiv.querySelector('#typing-dots');
            if (!dotsSpan) return;

            let dots = '';
            const interval = setInterval(() => {
                if (!document.getElementById(typingId)) {
                    clearInterval(interval);
                    return;
                }

                dots = dots.length >= 3 ? '' : dots + '.';
                dotsSpan.textContent = 'typing' + dots;
            }, 500);
        }

        function updateStatus(isOnline) {
            const statusDiv = document.getElementById('status');
            if (isOnline) {
                statusDiv.className = 'status online';
                statusDiv.textContent = 'Bot is online and ready to help!';
            } else {
                statusDiv.className = 'status offline';
                statusDiv.textContent = 'Bot is offline. Please try again later.';
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Enter key support
        document.getElementById('message-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Check bot status on load
        window.addEventListener('load', async function() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                updateStatus(data.healthy);
            } catch (error) {
                updateStatus(false);
            }
        });

        // Focus input on load
        document.getElementById('message-input').focus();
    </script>
</body>
</html>'''
    return render_template_string(html_content)


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests from the web interface"""
    try:
        if not bot:
            return jsonify({
                'success': False,
                'error': 'Bot is not available. Please try again later.'
            }), 503

        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid request format'
            }), 400

        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id', 'default')

        if not message:
            return jsonify({
                'success': False,
                'error': 'Message cannot be empty'
            }), 400

        # Get response from bot (without typing indicator for web)
        response = bot.chat(message, conversation_id, show_typing=False)

        logger.info(f"Chat request - ID: {conversation_id}, Message: {message[:50]}...")

        return jsonify({
            'success': True,
            'response': response,
            'conversation_id': conversation_id
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        if not bot:
            return jsonify({'healthy': False, 'message': 'Bot not initialized'})

        # Quick health check
        is_healthy, message = bot.health_check()
        return jsonify({'healthy': is_healthy, 'message': message})

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({'healthy': False, 'message': 'Health check failed'})


@app.route('/clear/<conversation_id>', methods=['POST'])
def clear_conversation(conversation_id):
    """Clear conversation history"""
    try:
        if not bot:
            return jsonify({'success': False, 'error': 'Bot not available'}), 503

        bot.clear_conversation(conversation_id)
        return jsonify({'success': True, 'message': 'Conversation cleared'})

    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to clear conversation'}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    if bot:
        print("🚀 Starting Mshauri Tech Customer Support Web Server...")
        print("🌐 Open your browser and go to: http://localhost:8000")
        print("📱 The web interface will be available there")
        print("⚡ Press Ctrl+C to stop the server")
        app.run(host='0.0.0.0', port=8000, debug=False)
    else:
        print("❌ Cannot start server: Bot initialization failed")
        print("Please check your configuration and try again.")