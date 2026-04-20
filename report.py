def generate_summary_report(results: list[dict], output_filepath: str):
    """
    Generates a plain-text summary report from the structured LLM results.
    """
    if not results:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write("No successful analyses were performed.\n")
        return

    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write("="*50 + "\n")
        f.write("LLM DOCUMENT ANALYSIS REPORT\n")
        f.write("="*50 + "\n\n")
        
        for idx, result in enumerate(results, 1):
            source = result.get('source', f"Document {idx}")
            f.write(f"--- Analysis for: {source} ---\n")
            f.write(f"Summary: {result.get('summary', 'N/A')}\n")
            f.write(f"Sentiment: {result.get('sentiment', 'N/A')}\n")
            f.write("Entities: ")
            entities = result.get('entities', [])
            f.write(", ".join(entities) if entities else "None")
            f.write("\n")
            
            f.write("Questions Generated:\n")
            questions = result.get('questions', [])
            if questions:
                for q in questions:
                    f.write(f"  - {q}\n")
            else:
                f.write("  None\n")
            
            f.write("\n" + "-"*40 + "\n\n")
