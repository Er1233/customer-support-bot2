# config.py - Updated for Cohere API
import os
from dotenv import load_dotenv

load_dotenv()

# Updated to use Cohere instead of Hugging Face
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "")
COMPANY_NAME = os.getenv("COMPANY_NAME", "Mshauri Tech")
MAX_HISTORY = int(os.getenv("MAX_HISTORY", 5))

PRODUCT_INFO = """
# Mshauri Tech Products & Services

- Mshauri Assistant: AI-powered customer support automation
- Mshauri Analytics: Customer interaction insights platform  
- Mshauri Connect: Omnichannel communication system
- Support hours: Monday-Friday, 9 AM - 6 PM EAT
- Support email: support@mshauri.tech

Our solutions help businesses automate customer support, gain insights from customer interactions, and manage multi-channel communications efficiently.
"""