import json
import csv
import pandas as pd
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
import aiohttp
import asyncio

def extract_text_from_file(filepath: str) -> str:
    """Extracts text from a local .txt or .pdf file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    elif ext == '.pdf':
        text = ""
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text
    else:
        raise ValueError(f"Unsupported file format: {ext}")

async def extract_text_from_url(url: str) -> str:
    """Fetches and extracts main text content from a URL asynchronously."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=10) as response:
            response.raise_for_status()
            html = await response.text()
            
    soup = BeautifulSoup(html, 'html.parser')
    
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()
        
    text = soup.get_text(separator=' ', strip=True)
    return text
def chunk_text(text: str, max_chars: int = 15000) -> list[str]:
    """Simple chunking by character length to avoid exceeding context window."""
    # A simple approach to chunking without relying on complex tokenizers or frameworks
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > max_chars:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
            
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def save_to_json(data: list[dict], filepath: str):
    """Saves a list of dictionaries to a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def save_to_csv(data: list[dict], filepath: str):
    """Saves a list of dictionaries to a CSV file."""
    if not data:
        return
    df = pd.DataFrame(data)
    df.to_csv(filepath, index=False, encoding='utf-8')
