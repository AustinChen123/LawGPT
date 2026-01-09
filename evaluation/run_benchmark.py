import json
import os
import time
from evaluation.dataset_generator import generate_benchmark
from evaluation.judge import RagasJudge
from agent.graph_agent import run_agent

DATASET_FILE = "evaluation/benchmark_dataset.json"

def run_benchmark():
    # 1. Ensure Dataset Exists
    if not os.path.exists(DATASET_FILE):
        print("📉 No benchmark dataset found. Generating one now...")
        generate_benchmark()
    
    with open(DATASET_FILE, "r") as f:
        test_cases = json.load(f)
        
    print(f"🚀 Starting Benchmark on {len(test_cases)} cases...")
    
    judge = RagasJudge()
    results = []
    
    for i, case in enumerate(test_cases):
        print(f"\n--- Case {i+1}/{len(test_cases)} ---")
        question = case["question"]
        ground_truth = case["ground_truth"]
        
        print(f"Q: {question}")
        
        # 2. Run Agent
        try:
            output = run_agent(question)
            answer = output["answer"]
            
            # Extract text from retrieved docs for the judge
            retrieved_texts = [d.get('metadata', {}).get('content', '') for d in output["documents"]]
            
        except Exception as e:
            print(f"❌ Agent Failed: {e}")
            continue
            
        # 3. Grade
        print("⚖️  Grading...")
        context_recall = judge.evaluate_context_recall(ground_truth, retrieved_texts)
        faithfulness = judge.evaluate_faithfulness(answer, retrieved_texts)
        
        print(f"   -> Context Recall: {context_recall:.2f}")
        print(f"   -> Faithfulness:   {faithfulness:.2f}")
        
        results.append({
            "question": question,
            "ground_truth": ground_truth,
            "answer": answer,
            "metrics": {
                "context_recall": context_recall,
                "faithfulness": faithfulness
            }
        })
        
        time.sleep(5) # Rate limit protection

    # 4. Summary
    if results:
        avg_recall = sum(r["metrics"]["context_recall"] for r in results) / len(results)
        avg_faith = sum(r["metrics"]["faithfulness"] for r in results) / len(results)
        
        print("\n🏆 Benchmark Results 🏆")
        print(f"Total Cases: {len(results)}")
        print(f"Average Context Recall: {avg_recall:.2%}")
        print(f"Average Faithfulness:   {avg_faith:.2%}")
        
        # Save results
        with open("evaluation/report.json", "w") as f:
            json.dump(results, f, indent=2)
            
if __name__ == "__main__":
    run_benchmark()
