from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
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
    """Serve the integrated one-page website with AI chat"""
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mshauri Tech - AI-Powered Solutions</title>
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
            overflow-x: hidden;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        /* Header */
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 0;
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
            backdrop-filter: blur(10px);
        }

        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .logo {
            font-size: 1.8rem;
            font-weight: bold;
            background: linear-gradient(45deg, #fff, #f0f0f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .nav-menu {
            display: flex;
            list-style: none;
            gap: 2rem;
        }

        .nav-menu a {
            color: white;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.3s ease;
        }

        .nav-menu a:hover {
            color: #f1c40f;
        }

        /* Hero Section */
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 8rem 0 4rem;
            position: relative;
            overflow: hidden;
        }

        .hero::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="25" cy="25" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1.5" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="1" fill="rgba(255,255,255,0.1)"/></svg>');
            animation: float 20s infinite linear;
        }

        @keyframes float {
            0% { transform: translateY(0px) rotate(0deg); }
            100% { transform: translateY(-100px) rotate(360deg); }
        }

        .hero-content {
            position: relative;
            z-index: 2;
        }

        .hero h1 {
            font-size: 3.5rem;
            margin-bottom: 1rem;
            animation: fadeInUp 1s ease-out;
        }

        .hero p {
            font-size: 1.3rem;
            margin-bottom: 2rem;
            opacity: 0.9;
            animation: fadeInUp 1s ease-out 0.2s both;
        }

        .cta-button {
            display: inline-block;
            background: #f1c40f;
            color: #333;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1.1rem;
            transition: all 0.3s ease;
            animation: fadeInUp 1s ease-out 0.4s both;
        }

        .cta-button:hover {
            background: #e67e22;
            color: white;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }

        /* Services Section */
        .services {
            padding: 5rem 0;
            background: #f8f9fa;
        }

        .section-title {
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 3rem;
            color: #2c3e50;
        }

        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
        }

        .service-card {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .service-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .service-card:hover::before {
            left: 100%;
        }

        .service-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }

        .service-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }

        .service-card h3 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #2c3e50;
        }

        /* About Section */
        .about {
            padding: 5rem 0;
            background: white;
        }

        .about-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 3rem;
            align-items: center;
        }

        .about-text h2 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
            color: #2c3e50;
        }

        .about-text p {
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
            color: #555;
        }

        .about-image {
            text-align: center;
            font-size: 10rem;
            color: #667eea;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        /* Contact Section */
        .contact {
            padding: 5rem 0;
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
        }

        .contact-content {
            text-align: center;
        }

        .contact h2 {
            font-size: 2.5rem;
            margin-bottom: 2rem;
        }

        .contact-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
            margin-top: 3rem;
        }

        .contact-item {
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }

        .contact-item h3 {
            margin-bottom: 1rem;
            color: #f1c40f;
        }

        /* Footer */
        footer {
            background: #1a252f;
            color: white;
            text-align: center;
            padding: 2rem 0;
        }

        /* Chat Widget Styles */
        .chat-widget {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 1001;
        }

        .chat-button {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            position: relative;
        }

        .chat-button:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(0,0,0,0.4);
        }

        .chat-button.active {
            transform: rotate(45deg);
        }

        .chat-window {
            display: none;
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 400px;
            height: 600px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 50px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: slideUp 0.3s ease-out;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            position: relative;
        }

        .chat-status {
            position: absolute;
            top: 15px;
            right: 15px;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #27ae60;
        }

        .chat-status.offline {
            background: #e74c3c;
        }

        .chat-body {
            height: 400px;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }

        .chat-input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }

        .chat-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            outline: none;
            font-size: 14px;
        }

        .chat-send {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
        }

        .chat-send:disabled {
            background: #ccc;
            cursor: not-allowed;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 80%;
            word-wrap: break-word;
            animation: messageIn 0.3s ease-out;
        }

        @keyframes messageIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            text-align: right;
        }

        .message.bot {
            background: white;
            color: #333;
            margin-right: auto;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .typing-indicator {
            background: white;
            color: #666;
            margin-right: auto;
            font-style: italic;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        /* Quick Actions */
        .quick-actions {
            padding: 15px 20px;
            border-bottom: 1px solid #eee;
            text-align: center;
        }

        .quick-action {
            background: #f8f9fa;
            border: 1px solid #ddd;
            padding: 8px 15px;
            margin: 5px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.3s ease;
            display: inline-block;
        }

        .quick-action:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }

        /* Animations */
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* Responsive Design */
        @media (max-width: 768px) {
            .chat-window {
                width: calc(100vw - 40px);
                height: 70vh;
                right: 20px;
                left: 20px;
            }

            .hero h1 {
                font-size: 2.5rem;
            }

            .nav-menu {
                display: none;
            }

            .about-content {
                grid-template-columns: 1fr;
                text-align: center;
            }

            .about-image {
                font-size: 6rem;
            }
        }

        @media (max-width: 480px) {
            .hero {
                padding: 6rem 0 3rem;
            }

            .hero h1 {
                font-size: 2rem;
            }

            .hero p {
                font-size: 1.1rem;
            }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <header>
        <div class="container">
            <div class="header-content">
                <div class="logo">🤖 Mshauri Tech</div>
                <nav>
                    <ul class="nav-menu">
                        <li><a href="#home">Home</a></li>
                        <li><a href="#services">Services</a></li>
                        <li><a href="#about">About</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </nav>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section id="home" class="hero">
        <div class="container">
            <div class="hero-content">
                <h1>AI-Powered Customer Support</h1>
                <p>Experience the future of customer service with our intelligent AI assistant that understands, learns, and helps 24/7</p>
                <a href="#" class="cta-button" onclick="openChat()">Try AI Assistant</a>
            </div>
        </div>
    </section>

    <!-- Services Section -->
    <section id="services" class="services">
        <div class="container">
            <h2 class="section-title">Our AI Solutions</h2>
            <div class="services-grid">
                <div class="service-card">
                    <span class="service-icon">🤖</span>
                    <h3>Smart Chatbots</h3>
                    <p>Intelligent conversational AI that understands context and provides personalized responses to customer inquiries.</p>
                </div>
                <div class="service-card">
                    <span class="service-icon">📊</span>
                    <h3>Analytics & Insights</h3>
                    <p>Advanced analytics to understand customer behavior, preferences, and satisfaction metrics in real-time.</p>
                </div>
                <div class="service-card">
                    <span class="service-icon">🔧</span>
                    <h3>Custom Integration</h3>
                    <p>Seamless integration with your existing systems, CRM, and business processes for maximum efficiency.</p>
                </div>
                <div class="service-card">
                    <span class="service-icon">🌐</span>
                    <h3>Multi-Platform Support</h3>
                    <p>Deploy across web, mobile, social media, and messaging platforms for consistent customer experience.</p>
                </div>
                <div class="service-card">
                    <span class="service-icon">🎯</span>
                    <h3>Personalization</h3>
                    <p>AI-driven personalization that adapts to individual customer preferences and communication styles.</p>
                </div>
                <div class="service-card">
                    <span class="service-icon">⚡</span>
                    <h3>Real-time Support</h3>
                    <p>Instant responses and proactive customer engagement with 99.9% uptime guarantee.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- About Section -->
    <section id="about" class="about">
        <div class="container">
            <div class="about-content">
                <div class="about-text">
                    <h2>About Mshauri Tech</h2>
                    <p>We are pioneers in AI-powered customer support solutions, helping businesses transform their customer service experience through intelligent automation and human-like interactions.</p>
                    <p>Our cutting-edge technology combines natural language processing, machine learning, and deep understanding of customer psychology to create support systems that truly understand and help.</p>
                    <p>With over 500+ successful implementations and 99.5% customer satisfaction rate, we're trusted by businesses worldwide to deliver exceptional customer experiences.</p>
                </div>
                <div class="about-image">
                    🚀
                </div>
            </div>
        </div>
    </section>

    <!-- Contact Section -->
    <section id="contact" class="contact">
        <div class="container">
            <div class="contact-content">
                <h2>Get In Touch</h2>
                <p>Ready to revolutionize your customer support? Let's discuss how our AI solutions can transform your business.</p>
                <div class="contact-info">
                    <div class="contact-item">
                        <h3>📧 Email</h3>
                        <p>hello@mshauritech.com</p>
                    </div>
                    <div class="contact-item">
                        <h3>📱 Phone</h3>
                        <p>+1 (555) 123-4567</p>
                    </div>
                    <div class="contact-item">
                        <h3>💬 Live Chat</h3>
                        <p>Available 24/7 via AI Assistant</p>
                    </div>
                    <div class="contact-item">
                        <h3>🌍 Global</h3>
                        <p>Serving clients worldwide</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer>
        <div class="container">
            <p>&copy; 2025 Mshauri Tech. All rights reserved. Powering the future of customer support with AI.</p>
        </div>
    </footer>

    <!-- Chat Widget -->
    <div class="chat-widget">
        <button class="chat-button" onclick="toggleChat()" id="chatButton">
            💬
        </button>

        <div class="chat-window" id="chatWindow">
            <div class="chat-header">
                <h3>AI Assistant</h3>
                <div class="chat-status" id="chatStatus"></div>
                <p>Powered by Mshauri Tech</p>
            </div>

            <div class="quick-actions">
                <span class="quick-action" onclick="sendQuickMessage('What services do you offer?')">Services</span>
                <span class="quick-action" onclick="sendQuickMessage('How does your AI work?')">How it works</span>
                <span class="quick-action" onclick="sendQuickMessage('I need a demo')">Request Demo</span>
                <span class="quick-action" onclick="sendQuickMessage('Pricing information')">Pricing</span>
            </div>

            <div class="chat-body" id="chatBody">
                <div class="message bot">
                    <strong>AI Assistant:</strong> Hello! 👋 I'm here to help you learn about Mshauri Tech's AI-powered customer support solutions. How can I assist you today?
                </div>
            </div>

            <div class="chat-input-area">
                <input type="text" class="chat-input" id="chatInput" placeholder="Type your message..." maxlength="500" onkeypress="handleKeyPress(event)">
                <button class="chat-send" onclick="sendMessage()" id="sendButton">Send</button>
            </div>
        </div>
    </div>

    <script>
        let chatOpen = false;
        let isTyping = false;
        let conversationId = 'web_' + Date.now();

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            checkBotHealth();

            // Smooth scrolling for navigation links
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function (e) {
                    e.preventDefault();
                    const target = document.querySelector(this.getAttribute('href'));
                    if (target) {
                        target.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        });

        // Chat functionality
        function toggleChat() {
            const chatWindow = document.getElementById('chatWindow');
            const chatButton = document.getElementById('chatButton');

            if (chatOpen) {
                chatWindow.style.display = 'none';
                chatButton.classList.remove('active');
                chatOpen = false;
            } else {
                chatWindow.style.display = 'block';
                chatButton.classList.add('active');
                chatOpen = true;
                setTimeout(() => {
                    document.getElementById('chatInput').focus();
                }, 300);
            }
        }

        function openChat() {
            if (!chatOpen) {
                toggleChat();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('chatInput');
            const sendButton = document.getElementById('sendButton');
            const message = input.value.trim();

            if (!message || isTyping) return;

            isTyping = true;
            sendButton.disabled = true;
            sendButton.textContent = 'Sending...';

            addMessage('user', message);
            input.value = '';

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

                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

                const data = await response.json();
                removeTypingIndicator(typingId);

                if (data.success) {
                    addMessage('bot', data.response);
                    updateChatStatus(true);
                } else {
                    addMessage('bot', data.error || 'Sorry, I encountered an error. Please try again.');
                }

            } catch (error) {
                console.error('Chat error:', error);
                removeTypingIndicator(typingId);
                addMessage('bot', 'Sorry, I could not connect to the support system. Please try again later.');
                updateChatStatus(false);
            }

            isTyping = false;
            sendButton.disabled = false;
            sendButton.textContent = 'Send';
            input.focus();
        }

        function sendQuickMessage(message) {
            document.getElementById('chatInput').value = message;
            sendMessage();
        }

        function addMessage(sender, text) {
            const chatBody = document.getElementById('chatBody');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;

            const label = sender === 'user' ? 'You' : 'AI Assistant';
            messageDiv.innerHTML = `<strong>${label}:</strong> ${escapeHtml(text)}`;

            chatBody.appendChild(messageDiv);
            chatBody.scrollTop = chatBody.scrollHeight;
        }

        function addTypingIndicator() {
            const chatBody = document.getElementById('chatBody');
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message typing-indicator';
            typingDiv.id = 'typing-' + Date.now();
            typingDiv.innerHTML = '<strong>AI Assistant:</strong> <span id="typing-dots">thinking</span>';

            chatBody.appendChild(typingDiv);
            chatBody.scrollTop = chatBody.scrollHeight;

            animateTypingDots(typingDiv.id);
            return typingDiv.id;
        }

        function removeTypingIndicator(typingId) {
            const typingDiv = document.getElementById(typingId);
            if (typingDiv) typingDiv.remove();
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
                dotsSpan.textContent = 'thinking' + dots;
            }, 500);
        }

        async function checkBotHealth() {
            try {
                const response = await fetch('/health');
                const data = await response.json();
                updateChatStatus(data.healthy);
            } catch (error) {
                updateChatStatus(false);
            }
        }

        function updateChatStatus(isOnline) {
            const statusDiv = document.getElementById('chatStatus');
            statusDiv.className = isOnline ? 'chat-status' : 'chat-status offline';
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                sendMessage();
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Check bot health periodically
        setInterval(checkBotHealth, 30000);

        // Smooth scroll reveal animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe service cards for animations
        document.addEventListener('DOMContentLoaded', () => {
            document.querySelectorAll('.service-card').forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
                observer.observe(card);
            });
        });
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
            }), 503

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
        }), 500

    @app.route('/clear/<conversation_id>', methods=['POST'])
    def clear_conversation(conversation_id):
        """Clear conversation history"""
    try:
        if not bot:
            return jsonify({
                'success': False,
                'error': 'AI assistant not available'
            }), 503

        bot.clear_conversation(conversation_id)
        logger.info(f"Conversation cleared: {conversation_id}")

        return jsonify({
            'success': True,
            'message': 'Conversation cleared successfully'
        })

    except Exception as e:
        logger.error(f"Error clearing conversation {conversation_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to clear conversation'
        }), 500

@app.route('/api/status', methods=['GET'])
def api_status():
    """API status endpoint"""
    try:
        return jsonify({
            'status': 'online',
            'service': 'Mshauri Tech AI Assistant',
            'version': '1.0.0',
            'timestamp': time.time(),
            'bot_available': bot is not None
        })
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'status': 404
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status': 500
    }), 500

@app.errorhandler(503)
def service_unavailable(error):
    """Handle 503 errors"""
    return jsonify({
        'error': 'Service temporarily unavailable',
        'status': 503
    }), 503

    # Add CORS headers for all responses
@app.after_request
def after_request(response):
    """Add security headers and CORS"""
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

if __name__ == '__main__':
    if bot:
        print("🚀 Starting Mshauri Tech AI-Powered Website...")
        print("🌐 Open your browser and go to: http://localhost:8000")
        print("💬 Integrated AI chat assistant is ready!")
        print("📊 Health check available at: http://localhost:8000/health")
        print("⚡ Press Ctrl+C to stop the server")
        print("-" * 60)

        try:
            app.run(
                host='0.0.0.0',
                port=8000,
                debug=False,
                threaded=True
            )
        except KeyboardInterrupt:
            print("\n👋 Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            print(f"❌ Server error: {str(e)}")
    else:
        print("❌ Cannot start server: AI assistant initialization failed")
        print("🔧 Please check your bot configuration and try again.")
        print("📋 Check the web_server.log file for detailed error information.")