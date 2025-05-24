README.md
Customer Support Bot
A simple, efficient customer support bot using Hugging Face's inference API.
Features

🤖 Uses Hugging Face's free API with models like Mistral-7B
💬 Maintains conversation context for personalized support
🚀 FastAPI backend for high performance
🐳 Docker ready for easy deployment
⚙️ Simple configuration via environment variables

Setup
Prerequisites

Python 3.8+
Hugging Face account (optional but recommended for API key)

Installation

Clone this repository
bashgit clone https://github.com/yourusername/customer-support-bot.git
cd customer-support-bot

Create and configure the .env file
bashcp .env.example .env
# Edit .env with your settings

Install dependencies
bashpip install -r requirements.txt


Usage
Run Locally
Start the API server:
bashpython api.py
Test with CLI tool:
bashpython cli.py
The API will be available at http://localhost:8000
API Endpoints

GET / - Check if API is running
GET /health - Health check endpoint
POST /chat - Send a message and get a response

Example request to /chat:
json{
  "message": "I need help with my order",
  "conversation_id": "customer123"
}
Example response:
json{
  "response": "I'd be happy to help with your order. Could you please provide your order number so I can look up the details?",
  "conversation_id": "customer123"
}
Deploy with Docker
Build and run the Docker container:
bashdocker build -t customer-support-bot .
docker run -p 8000:8000 customer-support-bot
Configuration
Edit the .env file to customize:

HUGGINGFACE_API_KEY: Your API key (optional)
HF_MODEL: Model to use (default: "mistralai/Mistral-7B-Instruct-v0.3")
COMPANY_NAME: Your company name
MAX_HISTORY: Number of previous exchanges to remember

Cloud Deployment
Deploy to Heroku
bashheroku create
git push heroku main
Deploy to AWS Elastic Beanstalk
basheb init
eb create
eb deploy
Customization
Edit config.py to update the PRODUCT_INFO with details about your products, services, and support policies.
License
MIT
Security
This application uses environment variables to manage sensitive information like API keys.
⚠️ IMPORTANT: API Security ⚠️

Never commit your .env file with real API keys to version control
Always use the provided .env.example as a template
Create your own local .env file with your actual credentials
Regularly rotate your API keys for better security
When deploying, use your cloud provider's secrets management:

Heroku: Config Vars
AWS: Parameter Store or Secrets Manager
Azure: Key Vault
GCP: Secret Manager


