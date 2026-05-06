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
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=0.1,min=0.1,max=1.0),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def call_groq(self,system_prompt:str, user_prompt:str, fresh=False)-> dict:
        start = time.perf_counter()
        cache_prompt = (system_prompt + user_prompt)
        cached = None
        if not fresh:
            cached = get_cached(cache_prompt)
        if cached:
            self.cache_hits += 1
            logger.info("CACHE_HIT")
            cached["meta"] = {
                "confidence":cached.get("meta",{}).get("confidence",0.95),
                "model_used":self.model,
                "tokens_used":0,
                "response_time_ms":1,
                "cached":True
            }
            return cached
        self.cache_misses += 1
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
            parsed_json = json.loads(raw_content)
            elapsed_ms = round(
                (
                    time.perf_counter() - start
                )*1000,2
            )
            self.response_times.append(elapsed_ms)
            tokens_used=0
            if hasattr(response,"usage") and response.usage:
                tokens_used=response.usage.total_tokens
            parsed_json["meta"]={
                "confidence":parsed_json.get("confidence",0.85),
                "model_used":self.model,
                "tokens_used":tokens_used,
                "response_time_ms":elapsed_ms,
                "cached":False
            }
            if should_cache(parsed_json):
                set_cached(cache_prompt, parsed_json)
                logger.info("CACHE STORED")
            return parsed_json
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq JSON response: {str(e)}")
            return self._fallback_response()
        except Exception as e:
            logger.error(f"Groq API Error: {str(e)}")
            return self._fallback_response()
    
    def _fallback_response(self):
        return {
            "summary":"AI service temporarily unavailable.",
            "risk_level":"Unknown",
            "impact":"Live AI analysis unavailable.",
            "recommendation":"Retry shortly.",
            "confidence":0.0,
            "meta":{
                "confidence":0.0,
                "model_used":"fallback",
                "tokens_used":0,
                "response_time_ms":0,
                "cached":False,
                "is_fallback":True
            }
        }