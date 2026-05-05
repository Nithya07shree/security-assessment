"""
GROQ client for AI API endpoints.

- Includes: Groq API call, JSON parsing, 3-retry with backoff, error logging
"""
import os
from groq import Groq
import logging
from dotenv import load_dotenv
import json
import time
from collections import deque
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from services.cache_service import (get_cached,set_cached, should_cache)

# Set up logging
logger = logging.getLogger(__name__)
load_dotenv()

class GroqService:
    def __init__(self, api_key: str= None):
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-8b-instant"
        self.response_times = deque(maxlen=10)
        self.cache_hits = 0
        self.cache_misses = 0

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1,min=2,max=10),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def call_groq(self,system_prompt:str, user_prompt:str, fresh=False)-> dict:
        cache_prompt = (system_prompt + user_prompt)
        if not fresh:
            cached = get_cached(cache_prompt)

        if cached:
            logger.info("CACHE_HIT")
            return cached
        start = time.perf_counter()
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
            elapsed_ms = (time.perf_counter() - start) * 1000
            self.response_times.append(elapsed_ms)
            raw_content = response.choices[0].message.content
            parsed_json = json.loads(raw_content)
            if should_cache(parsed_json):
                set_cached(cache_prompt, parsed_json)
                logger.info("CACHE STORED")
            return parsed_json
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq JSON respons: {str(e)}")
            raise # triggers retry is JSON is malformed
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            raise # trigger retry if any other exceptions