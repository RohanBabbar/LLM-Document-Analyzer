# LLM Document Analyzer Pipeline

A modular Python data pipeline that ingests unstructured text from URLs and files (PDF, TXT), processes it, and extracts structured insights using Google's Gemini LLM. 

This project was built without relying on heavy orchestration frameworks like LangChain, opting instead for direct API integration with robust exponential backoff error handling.

## Features
- **Multi-source Ingestion**: Parses local `.txt` and `.pdf` files (using PyMuPDF) as well as web URLs (using BeautifulSoup).
- **Automated Chunking**: Slices long documents into manageable chunks to respect LLM context limits.
- **Resilient API Calls**: Uses the `tenacity` library to automatically retry failed LLM API requests (e.g., rate limits) with exponential backoff.
- **Structured JSON Output**: Enforces strict JSON schema generation from the LLM.
- **Data Export**: Saves extracted data (summaries, entities, sentiment, questions) to JSON, CSV, and generates a plain-text summary report.
- **Graceful Error Handling**: Skips broken URLs and missing files without crashing the entire pipeline.

## Setup & Installation

1. Clone this repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and add your Gemini API Key:
   ```
   GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

Simply run the main orchestrator script:
```bash
python main.py
```

The script will iterate over the predefined inputs and generate:
- `output.json`: The raw structured JSON from the LLM.
- `output.csv`: The same data formatted in CSV for easy viewing.
- `summary_report.txt`: A clean, human-readable summary of all processed documents.
