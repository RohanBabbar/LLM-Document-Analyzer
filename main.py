import os
import logging
from dotenv import load_dotenv
import asyncio

from utils import extract_text_from_file, extract_text_from_url, chunk_text, save_to_json, save_to_csv
from llm import analyze_chunk_with_llm
from report import generate_summary_report

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def process_source(source: str, api_key: str) -> dict | None:
    """
    Processes a single source (file or URL) and returns the extracted structured data.
    """
    logger.info(f"Processing source: {source}")
    try:
        if source.startswith("http://") or source.startswith("https://"):
            text = await extract_text_from_url(source)
        else:
            text = extract_text_from_file(source)
            
        if not text.strip():
            logger.warning(f"Extracted text is empty for {source}. Skipping.")
            return None
            
        # For simplicity, if the text is very long, we could just take the first chunk, 
        # or aggregate results across chunks. Here we'll process the first chunk 
        # as it usually contains enough information for a document-level summary.
        # In a more complex system, we'd map-reduce over all chunks.
        chunks = chunk_text(text, max_chars=15000)
        main_chunk = chunks[0] 
        
        logger.info(f"Extracted {len(text)} characters. Using first chunk of {len(main_chunk)} characters.")
        
        result_json = await analyze_chunk_with_llm(main_chunk, api_key)
        
        # Add source identifier
        result_json['source'] = source
        return result_json
        
    except Exception as e:
        logger.error(f"Failed to process {source}: {e}")
        return None

async def main():
    load_dotenv(override=True)
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        logger.error("GEMINI_API_KEY not found or not set properly in .env")
        return
        
    inputs = [
        "https://en.wikipedia.org/wiki/Large_language_model",
        "sample.txt",
        "sample.pdf",
        "https://this-is-a-broken-url.com/404" # Should gracefully fail and skip
    ]
    
    # Create dummy local files for testing if they don't exist
    if not os.path.exists("sample.txt"):
        with open("sample.txt", "w") as f:
            f.write("The quick brown fox jumps over the lazy dog. This is a very simple text file to test the extraction capabilities of the system. The sentiment is generally positive.")
    
    all_results = []
    
    tasks = []
    for source in inputs:
        if source == "sample.pdf" and not os.path.exists(source):
            logger.warning("sample.pdf not found in local directory. Skipping.")
            continue
        tasks.append(process_source(source, api_key))
        
    logger.info("Starting concurrent processing...")
    results = await asyncio.gather(*tasks)
    
    all_results = [r for r in results if r is not None]

            
    if all_results:
        logger.info("Saving outputs...")
        save_to_json(all_results, "output.json")
        save_to_csv(all_results, "output.csv")
        generate_summary_report(all_results, "summary_report.txt")
        logger.info("Pipeline completed successfully! Check output.json, output.csv, and summary_report.txt")
    else:
        logger.warning("No successful results to save.")

if __name__ == "__main__":
    asyncio.run(main())
