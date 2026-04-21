import sys
import os
import pytest
from unittest.mock import AsyncMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm import analyze_chunk_with_llm

# pytest.mark.asyncio tells pytest this test uses async/await
@pytest.mark.asyncio
# @patch intercepts the GenerativeModel class before it runs
@patch("llm.genai.GenerativeModel")
async def test_analyze_chunk_success(mock_model_class):
    """Test that a successful LLM JSON response is parsed correctly."""
    
    # 1. We create a fake response object that looks exactly like what Gemini returns
    fake_response = AsyncMock()
    fake_response.text = '{"summary": "Fake summary", "sentiment": "Positive", "entities": [], "questions": []}'
    
    # 2. We create a fake model instance 
    mock_model_instance = AsyncMock()
    # 3. We tell our fake model to return our fake response when generate_content_async is called
    mock_model_instance.generate_content_async.return_value = fake_response
    
    # 4. We inject our fake model instance into the intercepted class
    mock_model_class.return_value = mock_model_instance
    
    # Now we run our actual code! It will use the fake model instead of the real one.
    result = await analyze_chunk_with_llm("Some text", api_key="fake_key")
    
    # Verify the code successfully parsed the fake JSON
    assert result["summary"] == "Fake summary"
    assert result["sentiment"] == "Positive"
