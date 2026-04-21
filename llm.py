import os
import json
import logging
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Prompt defining the required JSON structure
SYSTEM_PROMPT = """
You are a document analyzer. Extract the following information from the provided text and strictly output ONLY valid JSON.
Do not include markdown blocks like ```json ... ```, just the raw JSON object.

The required JSON schema is:
{
    "summary": "A 2-3 sentence summary of the text.",
    "entities": ["list", "of", "key", "entities", "like", "people", "places", "organizations"],
    "sentiment": "Positive, Negative, or Neutral",
    "questions": ["Question 1 generated from text?", "Question 2?", "Question 3?"]
}
"""

from google.api_core.exceptions import NotFound

@retry(
    stop=stop_after_attempt(2), # Reduced to 2 to fail faster on bad models
    wait=wait_exponential(multiplier=1, min=2, max=10),
    before_sleep=lambda retry_state: logger.warning(f"Retrying LLM call... Attempt {retry_state.attempt_number}")
)
async def analyze_chunk_with_llm(text_chunk: str, api_key: str) -> dict:
    """
    Sends a chunk of text to Gemini API asynchronously and requests JSON output.
    """
    genai.configure(api_key=api_key)
    
    # Initialize the model using a more resilient model name alias
    model = genai.GenerativeModel('gemini-2.5-flash', system_instruction=SYSTEM_PROMPT)
    
    logger.info(f"Sending chunk to LLM ({len(text_chunk)} characters)...")
    
    try:
        response = await model.generate_content_async(
            text_chunk,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )
    except NotFound as e:
        logger.error(f"Model not found. Error: {e}")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                logger.info(f"Available model: {m.name}")
        raise ValueError("The requested Gemini model is not available for this API key.")

    
    try:
        response_text = response.text.strip()
        parsed_json = json.loads(response_text)
        return parsed_json
    except json.JSONDecodeError as e:
        logger.error(f"Failed to decode JSON from LLM: {response_text}")
        raise ValueError(f"LLM returned invalid JSON: {e}")
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        if "NotFound" in str(e) or "404" in str(e):
            logger.info("Attempting to list available models to diagnose NotFound error...")
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        logger.info(f"Available model: {m.name}")
            except Exception as inner_e:
                logger.error(f"Failed to list models: {inner_e}")
        raise e
