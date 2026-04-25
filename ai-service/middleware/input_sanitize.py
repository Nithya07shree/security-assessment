"""
Input Sanitization Middleware

- strips HTML tags from user input using bleach
- detects common prompt injection patters and blocks them
- returns a HTTP 400 error if anything suspicious is found

- this file catches attempts like injection attacks and Cross-Site Scripting (XSS) before the prompt reach Groq
"""

import json
from typing_extensions import List
import bleach
from bs4 import BeautifulSoup
import logging
from functools import wraps
from flask import request, jsonify
import re

# Set up logging
logger = logging.getLogger(__name__)

# common prompt injection patterns 
# using raw strings (r"") and \b for word boundaries
PROMPT_INJECTION_PATTERNS = [
    r"\bignore previous instructions\b",
    r"\bignore all instructions\b",
    r"\bignore your instructions\b",
    r"\bdisregard previous\b",
    r"\bdisregard your instructions\b",
    r"\bdisregard the above\b",
    r"\bforget previous instructions\b",
    r"\bforget your instructions\b",
    r"\byou are now\b",
    r"\byou are a different\b",
    r"\bact as if you are\b",
    r"\bpretend you are\b",
    r"\bpretend to be\b",
    r"\byour new instructions\b",
    r"\boverride your instructions\b",
    r"\bdo not follow\b",
    r"\bbypass your\b",
    r"\bnew persona\b",
    r"\bjailbreak\b",
    r"\bdan mode\b",
    r"\bdeveloper mode\b",
    r"\bsystem prompt\b",
    r"\breveal your prompt\b",
    r"\bshow me your prompt\b",
    r"\bwhat are your instructions\b",
    r"\brepeat your instructions\b",
    r"\bprint your instructions\b",
]
# convert regular expression string into regex pattern object.
# this is done for faster performance
COMBINED_PATTERN = re.compile("|".join(PROMPT_INJECTION_PATTERNS), re.IGNORECASE)

def strip_html(text: str) -> str:
    """
    Remove all HTML tags from a string using bs4 + bleach library

    input(str): user input as text
    output(str): text after stripping html tags

    """
    if not isinstance(text, str):
        return text
    
    # bs4: delete content of script/style tags
    soup = BeautifulSoup(text,"html.parser")
    for script in soup(["script", "style", "template"]):
        script.decompose()

    cleaned_text = soup.get_text(separator=' ',strip=True)

    # Bleach: ensure no tags of any kind remains in the text
    final_text = bleach.clean(
        cleaned_text,
        tags=[],        # No tags allowed
        attributes={},  # No attributes allowed
        strip=True,     # Delete tags instead of escaping
        strip_comments=True,    # remove <!-- instructions -->
    )

    return " ".join(final_text.split())

def contains_prompt_injection(text: str)-> str | None:
    """
    Checks if input contains any known prompt injection patterns.

    Args:
        text (str): user input text

    Returns:
        str: prompt injection pattern string
    """
    if not isinstance(text,str):
        return None
    
    # remove extra whitespace/newlines
    # eg. "ignore \n all" becomes "ignore all"
    normalized_text = " ".join(text.split())

    match = COMBINED_PATTERN.search(normalized_text)
    if match:
        return match.group(0) # returns the exact string that triggered the match
    return None

def sanitize_text(text: str) -> tuple[str | None,str | None]:
    """
    Runs input text through two checks:
    1. Strip HTML
    2. Check for prompt injection

    Args:
        text (str): input text

    Returns:
        tuple[str | None,str | None]: cleaned_text, error_message or None
    
    If error_message is not None, caller should return a 400 response.
    If error_message is None, cleaned_text is safe to use.
    """
    if not isinstance(text,str) or not text.strip():
        return "",None
    
    # check original text for injections
    matched_pattern = contains_prompt_injection(text)

    # strip html tags regardless
    cleaned = strip_html(text)

    # if not found in original text, find again in cleaned text
    if not matched_pattern:
        matched_pattern = contains_prompt_injection(cleaned)

    if matched_pattern:
        logger.warning(
            f"Prompt injection attempt detected. "
            f"Pattern matched: '{matched_pattern}' | "
            f"Original input length: {len(text)} chars."
        )
        return None, f"Input contains disallowed content: '{matched_pattern}'"
    
    return cleaned, None

def sanitize_request_body(fields_to_check: list[str]):
    """
    A decorator we put on Flask route functions to sanitize specific flields in the incoming JSON request body.

    Args:
        fields_to_check (list[str]): list of field names to check (eg. ['text','description','title'])
    
    Usage example:
        @app.route('/endpoint_name', methods=['POST'])
        @sanitize_request_body(['text','description'])
        def describe():
            data = request.get_json()
            # here data['text'] and data['description'] are already sanitized
    
    If any field contains HTML or prompt injection, request is rejected immediately with a 400 response before the route function even runs.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args,**kwargs):
            # only process requests having a JSON body
            if not request.is_json:
                return jsonify({
                    "error": "Request body must be JSON",
                    "status": 400
                }),400
            
            data = request.get_json()
            # data was not parsable
            if data is None:
                return jsonify({
                    "error": "Could not parse JSON body",
                    "status":400
                }),400
            # check every field in the request body
            for field in fields_to_check:
                # ignore if field is not present
                if field not in data:
                    continue

                field_value = data[field]
                if not isinstance(field_value, str): # skipping non string type fields
                    continue

                cleaned_value, error = sanitize_text(field_value)
                if error:
                    logger.warning(
                        f"Rejecting request to {request.path} | "
                        f"Field: '{field}' | Reason: '{error}'"
                    )
                    return jsonify({
                        "error":"Input validation failed",
                        "details":error,
                        "field":field,
                        "status":400
                    }),400

                data[field]=cleaned_value
            return f(*args,**kwargs)
        return decorated_function
    return decorator

def register_sanitization_hooks(app):
    """
    A global hook on the Flask app that runs basic checks on every incoming request.

    Args:
        app (_type_): flask app

    This catches:
    - requests with more than 10000 characters, which can also be an attempt to overload the prompt
    - any json body fields containing html regardless of the route
    """

    MAX_FIELD_LENGTH = 10000

    @app.before_request
    def global_input_check():
        # skip GET requests and requests without a body
        if request.method in ('GET','HEAD','OPTIONS'):
            return None
        
        if not request.is_json:
            return None
        data = request.get_json(silent=True)
        if not data or not isinstance(data,dict):
            return None
        
        for key, value in data.items():
            if not isinstance(value,str):
                continue

            if len(value)> MAX_FIELD_LENGTH:
                logger.warning(
                    f"Field is too long, rejected | "
                    f"Field: '{key}' | "
                    f"Length: {len(value)} | "
                    f"Endpoint: {request.path}"
                )
                return jsonify({
                    "error": "Input too long",
                    "detail": f"Field '{key}' exceeds maximum allowed length of {MAX_FIELD_LENGTH} characters",
                    "field": key,
                    "status":400
                }),400
        return None