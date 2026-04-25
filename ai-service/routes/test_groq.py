from services.groq_client import GroqService

import os

GROQ_API_KEY:str | None = os.getenv("GROQ_API_KEY")
groq_service = GroqService(api_key = GROQ_API_KEY)

try:
    data = groq_service.call_groq("Explain the security rule: No open SSH ports.")
    print(data)
except Exception as e:
    print(f"Request failed after 3 attempts. Error: {e}")