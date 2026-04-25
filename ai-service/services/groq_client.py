"""
GROQ client for AI API endpoints.

- Includes: Groq API call, JSON parsing, 3-retry with backoff, error logging
"""
import os
from groq import Groq
import logging
from dotenv import load_dotenv
import json
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

# Set up logging
logger = logging.getLogger(__name__)
load_dotenv()

class GroqService:
    def __init__(self, api_key: str= None):
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1,min=2,max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logger.warning)
    )
    def call_groq(self,system_prompt:str, user_prompt:str)-> dict:
        try:
            response = self.client.chat.completions.create(
                messages=[
                    {
                        'role':"system",
                        "content":system_prompt,
                    },
                    {
                        "role":"user",
                        "content":user_prompt,
                    }
                ],
                model=self.model,
                temperature=0.2,
                response_format={"type":"json_object"}
            )
            raw_content = response.choices[0].message.content
            return json.loads(raw_content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq JSON respons: {str(e)}")
            raise # triggers retry is JSON is malformed
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            raise # trigger retry if any other exceptions