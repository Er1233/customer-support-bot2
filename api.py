# api.py
# FastAPI web interface for the customer support bot

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bot import CustomerSupportBot
import uvicorn


# Initialize the bot
bot = CustomerSupportBot()

# Initialize FastAPI
app = FastAPI(
    title="Customer Support Bot API",
    description="Simple API for a customer support chatbot using Hugging Face models",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    conversation_id: str


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a customer support query and return a helpful response.

    - Use different conversation_id values to maintain separate conversation threads
    - The system will remember the context of recent messages
    """
    try:
        response = bot.chat(request.message, request.conversation_id)
        return {
            "response": response,
            "conversation_id": request.conversation_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.get("/")
async def root():
    """Check if the API is running"""
    return {
        "status": "online",
        "message": "Customer Support Bot API is running. Use /chat endpoint to interact."
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}


# Run the API server
if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)