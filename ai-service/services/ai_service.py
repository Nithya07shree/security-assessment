"""
Shared AI service instances.

Use module-level singletons to keep cache and latency metrics centralized.
"""

from services.groq_client import GroqService

groq_service = GroqService()
