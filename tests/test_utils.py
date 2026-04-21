import sys
import os

# This allows our tests to import from the parent directory (doc_analyzer)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import chunk_text

def test_chunk_text_basic():
    """Test that text is chunked correctly based on character limits."""
    
    # We create a simple dummy text
    sample_text = "This is a short sentence. Here is another one."
    
    # We ask our function to chunk it with a max length of 30 characters
    chunks = chunk_text(sample_text, max_chars=30)
    
    # Assertions are the core of testing. If these statements aren't True, the test fails!
    assert len(chunks) == 2, f"Expected 2 chunks, got {len(chunks)}"
    assert "This is a short sentence." in chunks[0]
    assert "Here is another one." in chunks[1]

def test_chunk_text_long_words():
    """Test chunking when a single word is very long."""
    sample_text = "Supercalifragilisticexpialidocious is a long word."
    chunks = chunk_text(sample_text, max_chars=20)
    
    assert len(chunks) == 3
