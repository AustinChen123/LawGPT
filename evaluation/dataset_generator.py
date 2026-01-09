import json
import os
import random
import glob
from rag.gemini_api import GeminiLLMAPI
from config.settings import Settings

DATA_DIR = "data/de"
OUTPUT_FILE = "evaluation/benchmark_dataset.json"
NUM_SAMPLES = 5 # Generate 5 test cases for the benchmark

def generate_benchmark():
    print("🎓 Initializing Dataset Generator (The 'Teacher')...")
    settings = Settings()
    llm = GeminiLLMAPI(api_key=settings.GOOGLE_API_KEY, model="gemini-flash-latest")
    
    # 1. Load Raw Data
    files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    if not files:
        print("❌ No data found in data/de. Please run crawler first.")
        return

    selected_files = random.sample(files, min(len(files), NUM_SAMPLES))
    dataset = []

    print(f"📄 Selected {len(selected_files)} documents for question generation.")

    for file_path in selected_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Combine all sections to give context
        full_text = "\n".join([f"{s['section']}: {s['content']}" for s in data.get('sections', [])])
        
        # 2. Prompt for Synthetic Data Generation (SDG)
        prompt = (
            f"You are a strict law professor creating an exam for law students.\n"
            f"Based ONLY on the following German legal text, generate a specific, practical legal question and its correct answer.\n\n"
            f"**Legal Text:**\n{full_text[:5000]} ... (truncated)\n\n"
            f"**Task:**\n"
            f"1. Generate a **Question** that requires understanding this specific statute. It should not be a simple 'What is paragraph X?' but a scenario or specific inquiry.\n"
            f"2. Provide the **Ground Truth** (The ideal answer) based strictly on the text.\n\n"
            f"**Output Format (JSON only):**\n"
            f'{{"question": "...", "ground_truth": "..."}}'
        )
        
        try:
            response = llm.generate_response(prompt).strip()
            # Clean JSON markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
                
            qa_pair = json.loads(response)
            qa_pair["source_file"] = os.path.basename(file_path)
            dataset.append(qa_pair)
            print(f"✅ Generated QA for {qa_pair['source_file']}")
        except Exception as e:
            print(f"⚠️ Failed to generate for {file_path}: {e}")

    # 3. Save Dataset
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    
    print(f"🎉 Benchmark dataset saved to {OUTPUT_FILE} with {len(dataset)} cases.")

if __name__ == "__main__":
    generate_benchmark()
