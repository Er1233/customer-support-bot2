from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import logging
import time
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
    """Serve the ShopEasy HTML page with integrated chatbot"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopEasy - Your Online Store</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Header */
        header {
            background: #2c3e50;
            color: white;
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: bold;
        }

        .cart-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .cart-btn {
            background: #e74c3c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.9rem;
        }

        .cart-btn:hover {
            background: #c0392b;
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 4rem 0;
        }

        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }

        .hero p {
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }

        /* Products Section */
        .products {
            padding: 4rem 0;
            background: #f8f9fa;
        }

        .section-title {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: #2c3e50;
        }

        .product-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
        }

        .product-card {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }

        .product-card:hover {
            transform: translateY(-5px);
        }

        .product-image {
            width: 100%;
            height: 200px;
            background: #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            color: #666;
        }

        .product-info {
            padding: 1.5rem;
        }

        .product-title {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
            color: #2c3e50;
        }

        .product-description {
            color: #666;
            margin-bottom: 1rem;
        }

        .product-price {
            font-size: 1.5rem;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 1rem;
        }

        .add-to-cart {
            width: 100%;
            background: #27ae60;
            color: white;
            border: none;
            padding: 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 1rem;
            transition: background 0.3s ease;
        }

        .add-to-cart:hover {
            background: #219a52;
        }

        /* Footer */
        footer {
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 2rem 0;
        }

        .footer-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-bottom: 2rem;
        }

        .footer-section h3 {
            margin-bottom: 1rem;
        }

        .footer-bottom {
            border-top: 1px solid #34495e;
            padding-top: 1rem;
        }

        /* Chatbot Styles */
        .chatbot-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1000;
        }

        .chatbot-button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .chatbot-button:hover {
            transform: scale(1.1);
        }

        .chatbot-window {
            display: none;
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 350px;
            height: 500px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
            overflow: hidden;
            z-index: 1000;
        }

        .chatbot-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chatbot-close {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
        }

        .chatbot-body {
            height: 320px;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .chatbot-input-area {
            padding: 15px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }

        .chatbot-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 6px;
            outline: none;
        }

        .chatbot-send {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 6px;
            cursor: pointer;
        }

        .chatbot-send:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .chat-message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
        }

        .chat-message.user {
            background: #667eea;
            color: white;
            margin-left: auto;
            text-align: right;
        }

        .chat-message.bot {
            background: white;
            color: #333;
            margin-right: auto;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .typing-indicator {
            background: white;
            color: #666;
            margin-right: auto;
            font-style: italic;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .quick-actions {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }

        .quick-action-btn {
            background: #f8f9fa;
            border: 1px solid #ddd;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            transition: background 0.3s ease;
        }

        .quick-action-btn:hover {
            background: #e9ecef;
        }

        .status-indicator {
            position: absolute;
            top: 5px;
            right: 5px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #27ae60;
        }

        .status-indicator.offline {
            background: #e74c3c;
        }

        @keyframes pulse {
            0% { box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
            50% { box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4); }
            100% { box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        }

        @media (max-width: 768px) {
            .chatbot-window {
                width: calc(100vw - 40px);
                right: 20px;
                left: 20px;
            }
            .hero h1 {
                font-size: 2rem;
            }
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">ShopEasy</div>
                <div class="cart-info">
                    <span id="cartCount">Cart (0)</span>
                    <button class="cart-btn" onclick="openCart()">View Cart</button>
                </div>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
        <div class="container">
            <h1>Welcome to ShopEasy</h1>
            <p>Discover amazing products at unbeatable prices with AI-powered customer support</p>
        </div>
    </section>

    <!-- Products Section -->
    <section class="products">
        <div class="container">
            <h2 class="section-title">Featured Products</h2>
            <div class="product-grid">
                <div class="product-card">
                    <div class="product-image">📱</div>
                    <div class="product-info">
                        <h3 class="product-title">Smartphone Pro</h3>
                        <p class="product-description">Latest flagship smartphone with advanced features</p>
                        <div class="product-price">$899.99</div>
                        <button class="add-to-cart" onclick="askChatbotAbout('Smartphone Pro')">Ask About Product</button>
                    </div>
                </div>

                <div class="product-card">
                    <div class="product-image">💻</div>
                    <div class="product-info">
                        <h3 class="product-title">Laptop Ultra</h3>
                        <p class="product-description">Powerful laptop for work and entertainment</p>
                        <div class="product-price">$1,299.99</div>
                        <button class="add-to-cart" onclick="askChatbotAbout('Laptop Ultra')">Ask About Product</button>
                    </div>
                </div>

                <div class="product-card">
                    <div class="product-image">🎧</div>
                    <div class="product-info">
                        <h3 class="product-title">Wireless Headphones</h3>
                        <p class="product-description">Premium noise-canceling headphones</p>
                        <div class="product-price">$299.99</div>
                        <button class="add-to-cart" onclick="askChatbotAbout('Wireless Headphones')">Ask About Product</button>
                    </div>
                </div>

                <div class="product-card">
                    <div class="product-image">⌚</div>
                    <div class="product-info">
                        <h3 class="product-title">Smart Watch</h3>
                        <p class="product-description">Track your fitness and stay connected</p>
                        <div class="product-price">$399.99</div>
                        <button class="add-to-cart" onclick="askChatbotAbout('Smart Watch')">Ask About Product</button>
                    </div>
                </div>

                <div class="product-card">
                    <div class="product-image">📷</div>
                    <div class="product-info">
                        <h3 class="product-title">Digital Camera</h3>
                        <p class="product-description">Capture memories in stunning quality</p>
                        <div class="product-price">$699.99</div>
                        <button class="add-to-cart" onclick="askChatbotAbout('Digital Camera')">Ask About Product</button>
                    </div>
                </div>

                <div class="product-card">
                    <div class="product-image">🖥️</div>
                    <div class="product-info">
                        <h3 class="product-title">Monitor 4K</h3>
                        <p class="product-description">Ultra HD monitor for crisp visuals</p>
                        <div class="product-price">$499.99</div>
                        <button class="add-to-cart" onclick="askChatbotAbout('Monitor 4K')">Ask About Product</button>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>About ShopEasy</h3>
                    <p>Your trusted online shopping destination with quality products and excellent AI-powered customer service.</p>
                </div>
                <div class="footer-section">
                    <h3>Customer Service</h3>
                    <p>Email: support@shopeasy.com<br>
                    Phone: 1-800-SHOP-NOW<br>
                    AI Chat: Available 24/7</p>
                </div>
                <div class="footer-section">
                    <h3>Follow Us</h3>
                    <p>Stay connected on social media for updates and special offers.</p>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; 2025 ShopEasy. All rights reserved. Powered by Mshauri Tech AI.</p>
            </div>
        </div>
    </footer>

    <!-- Chatbot Widget -->
    <div class="chatbot-widget">
        <button class="chatbot-button" onclick="toggleChatbot()" id="chatbotBtn">
            💬
            <div class="status-indicator" id="botStatus"></div>
        </button>
        <div class="chatbot-window" id="chatbotWindow">
            <div class="chatbot-header">
                <h3>ShopEasy AI Assistant</h3>
                <button class="chatbot-close" onclick="toggleChatbot()">×</button>
            </div>
            <div class="quick-actions">
                <button class="quick-action-btn" onclick="sendQuickMessage('Show me your best deals')">Best Deals</button>
                <button class="quick-action-btn" onclick="sendQuickMessage('I want to make a purchase')">Buy Now</button>
                <button class="quick-action-btn" onclick="sendQuickMessage('What are your shipping options?')">Shipping Info</button>
            </div>
            <div class="chatbot-body" id="chatbotBody">
                <div class="chat-message bot">
                    👋 Hi! I'm your ShopEasy AI assistant. I can help you with:
                    <br><br>
                    • Product information & specifications
                    <br>• Processing orders & payments
                    <br>• Shipping & return policies
                    <br>• Product recommendations
                    <br>• Technical support
                    <br><br>
                    How can I help you today?
                </div>
            </div>
            <div class="chatbot-input-area">
                <input type="text" class="chatbot-input" id="chatbotInput" placeholder="Type your message..." onkeypress="handleChatKeyPress(event)" maxlength="500">
                <button class="chatbot-send" onclick="sendMessage()" id="sendBtn">Send</button>
            </div>
        </div>
    </div>

    <script>
        // Global variables
        let chatbotOpen = false;
        let isTyping = false;
        let conversationId = 'shop_' + Date.now();

        // Initialize chatbot
        document.addEventListener('DOMContentLoaded', function() {
            checkBotHealth();

            // Auto-open chatbot with welcome message after 3 seconds
            setTimeout(() => {
                if (!chatbotOpen) {
                    const btn = document.getElementById('chatbotBtn');
                    btn.style.animation = 'pulse 1s infinite';
                }
            }, 3000);
        });

        // Check bot health status
        async function checkBotHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                updateBotStatus(data.healthy);
            } catch (error) {
                console.error('Health check failed:', error);
                updateBotStatus(false);
            }
        }

        function updateBotStatus(isOnline) {
            const statusIndicator = document.getElementById('botStatus');
            if (isOnline) {
                statusIndicator.className = 'status-indicator';
            } else {
                statusIndicator.className = 'status-indicator offline';
            }
        }

        function toggleChatbot() {
            const window = document.getElementById('chatbotWindow');
            const btn = document.getElementById('chatbotBtn');

            if (chatbotOpen) {
                window.style.display = 'none';
                btn.textContent = '💬';
                btn.innerHTML = '💬<div class="status-indicator" id="botStatus"></div>';
                chatbotOpen = false;
                checkBotHealth(); // Re-add status indicator
            } else {
                window.style.display = 'block';
                btn.textContent = '×';
                chatbotOpen = true;
                document.getElementById('chatbotInput').focus();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('chatbotInput');
            const sendBtn = document.getElementById('sendBtn');
            const message = input.value.trim();

            if (!message || isTyping) return;

            // Disable input while processing
            isTyping = true;
            sendBtn.disabled = true;
            sendBtn.textContent = 'Sending...';

            // Add user message to chat
            addChatMessage(message, 'user');
            input.value = '';

            // Add typing indicator
            const typingId = addTypingIndicator();

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        message: message,
                        conversation_id: conversationId
                    })
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();

                // Remove typing indicator
                removeTypingIndicator(typingId);

                if (data.success) {
                    addChatMessage(data.response, 'bot');
                    updateBotStatus(true);
                } else {
                    addChatMessage(data.error || 'Sorry, I encountered an error. Please try again.', 'bot');
                }

            } catch (error) {
                console.error('Chat error:', error);
                removeTypingIndicator(typingId);
                addChatMessage('Sorry, I could not connect to the support system. Please try again later.', 'bot');
                updateBotStatus(false);
            }

            // Re-enable input
            isTyping = false;
            sendBtn.disabled = false;
            sendBtn.textContent = 'Send';
            input.focus();
        }

        function sendQuickMessage(message) {
            if (!chatbotOpen) {
                toggleChatbot();
            }

            setTimeout(() => {
                const input = document.getElementById('chatbotInput');
                input.value = message;
                sendMessage();
            }, 300);
        }

        function askChatbotAbout(product) {
            if (!chatbotOpen) {
                toggleChatbot();
            }

            setTimeout(() => {
                const input = document.getElementById('chatbotInput');
                input.value = `Tell me about the ${product}`;
                sendMessage();
            }, 300);
        }

        function addChatMessage(message, sender) {
            const chatBody = document.getElementById('chatbotBody');
            const messageDiv = document.createElement('div');
            messageDiv.className = `chat-message ${sender}`;

            // Convert line breaks to HTML
            const formattedMessage = message.replace(/\n/g, '<br>');
            messageDiv.innerHTML = formattedMessage;

            chatBody.appendChild(messageDiv);
            chatBody.scrollTop = chatBody.scrollHeight;
        }

        function addTypingIndicator() {
            const chatBody = document.getElementById('chatbotBody');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'chat-message typing-indicator';
            typingDiv.id = 'typing-' + Date.now();
            typingDiv.innerHTML = '<span id="typing-dots">AI is thinking</span>';

            chatBody.appendChild(typingDiv);
            chatBody.scrollTop = chatBody.scrollHeight;

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
                dotsSpan.textContent = 'AI is thinking' + dots;
            }, 500);
        }

        function handleChatKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        // Cart functionality (integrated with chatbot)
        function addToCart(name, price) {
            askChatbotAbout(name);
        }

        function openCart() {
            if (!chatbotOpen) {
                toggleChatbot();
            }
            sendQuickMessage("I want to see my cart and checkout");
        }

        // Health monitoring
        setInterval(checkBotHealth, 30000); // Check every 30 seconds
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
                'error': 'AI assistant is not available. Please try again later.'
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

        # Log the chat request
        logger.info(f"Chat request - ID: {conversation_id}, Message: {message[:50]}...")

        # Get response from bot (without typing indicator for web)
        response = bot.chat(message, conversation_id, show_typing=False)

        return jsonify({
            'success': True,
            'response': response,
            'conversation_id': conversation_id
        })

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error. Please try again.'
        }), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for the chatbot"""
    try:
        if not bot:
            return jsonify({
                'healthy': False,
                'message': 'AI assistant not initialized'
            })

        # Quick health check
        is_healthy, message = bot.health_check()
        return jsonify({
            'healthy': is_healthy,
            'message': message
        })

    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'healthy': False,
            'message': 'Health check failed'
        })


@app.route('/clear/<conversation_id>', methods=['POST'])
def clear_conversation(conversation_id):
    """Clear conversation history for a specific user"""
    try:
        if not bot:
            return jsonify({
                'success': False,
                'error': 'AI assistant not available'
            }), 503

        bot.clear_conversation(conversation_id)
        logger.info(f"Cleared conversation: {conversation_id}")

        return jsonify({
            'success': True,
            'message': 'Conversation cleared successfully'
        })

    except Exception as e:
        logger.error(f"Error clearing conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear conversation'
        }), 500


@app.route('/api/products', methods=['GET'])
def get_products():
    """API endpoint to get product information"""
    try:
        products = [
            {
                'id': 1,
                'name': 'Smartphone Pro',
                'price': 899.99,
                'description': 'Latest flagship smartphone with advanced features',
                'specs': 'A16 processor, 128GB storage, Triple camera system, 5G connectivity'
            },
            {
                'id': 2,
                'name': 'Laptop Ultra',
                'price': 1299.99,
                'description': 'Powerful laptop for work and entertainment',
                'specs': 'Intel i7 processor, 16GB RAM, 512GB SSD, 15.6" 4K display'
            },
            {
                'id': 3,
                'name': 'Wireless Headphones',
                'price': 299.99,
                'description': 'Premium noise-canceling headphones',
                'specs': 'Active noise cancellation, 30-hour battery, Bluetooth 5.0'
            },
            {
                'id': 4,
                'name': 'Smart Watch',
                'price': 399.99,
                'description': 'Track your fitness and stay connected',
                'specs': 'Heart rate monitor, GPS, Water resistant, 7-day battery'
            },
            {
                'id': 5,
                'name': 'Digital Camera',
                'price': 699.99,
                'description': 'Capture memories in stunning quality',
                'specs': '24MP sensor, 4K video, Optical image stabilization'
            },
            {
                'id': 6,
                'name': 'Monitor 4K',
                'price': 499.99,
                'description': 'Ultra HD monitor for crisp visuals',
                'specs': '27" 4K display, HDR support, USB-C connectivity'
            }
        ]

        return jsonify({
            'success': True,
            'products': products
        })

    except Exception as e:
        logger.error(f"Error getting products: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve products'
        }), 500


@app.route('/api/status', methods=['GET'])
def system_status():
    """Get overall system status"""
    try:
        bot_healthy = False
        bot_message = "Bot not initialized"

        if bot:
            bot_healthy, bot_message = bot.health_check()

        return jsonify({
            'system': 'online',
            'bot': {
                'healthy': bot_healthy,
                'message': bot_message
            },
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        })

    except Exception as e:
        logger.error(f"System status error: {str(e)}")
        return jsonify({
            'system': 'error',
            'error': str(e),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        }), 500

if __name__ == '__main__':
    print("Starting ShopEasy Web Server...")
    print("Visit http://localhost:5000 to access the store")
    print("Press Ctrl+C to stop the server")

    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,  # Set to False for production
            threaded=True
        )
    except KeyboardInterrupt:
        print("\nShutting down ShopEasy Web Server...")
        logger.info("Server shutdown requested by user")
    except Exception as e:
        print(f"Failed to start server: {e}")
        logger.error(f"Server startup error: {str(e)}")
    finally:
        if bot:
            # Clean up bot resources if needed
            logger.info("Cleaning up bot resources...")
        print("Server stopped.")