import json
import os
import time
from evaluation.metrics import RAGEvaluator
from agent.graph_agent import run_agent

def run_evaluation():
    """
    Loads test cases, runs them through the agent, and reports metrics.
    """
    print("Running evaluation suite...")
    
    # Load test cases
    test_file_path = "evaluation/test_cases.json"
    if not os.path.exists(test_file_path):
        print(f"Test case file not found at {test_file_path}")
        return

    with open(test_file_path, "r") as f:
        data = json.load(f)
        test_cases = data.get("questions", [])

    print(f"Loaded {len(test_cases)} test cases.")
    
    evaluator = RAGEvaluator()
    results = []
    
    # Run Eval Loop
    for i, case in enumerate(test_cases):
        question = case["question"]
        expected_keywords = case.get("expected_keywords", [])
        
        print(f"\nEvaluating Case #{i+1}: {question}")
        
        # 1. Run Agent
        try:
            agent_output = run_agent(question)
            answer = agent_output["answer"]
            docs = agent_output["documents"]
        except Exception as e:
            print(f"Agent failed: {e}")
            continue

        print(f"Agent Answer: {answer[:100]}...") # Print preview
        
        # 2. Run Metrics
        scores = evaluator.run_all_metrics(
            question=question, 
            answer=answer, 
            retrieved_docs=docs, 
            expected_keywords=expected_keywords
        )
        
        print(f"Scores: {scores}")
        
        results.append({
            "case_id": case.get("id"),
            "question": question,
            "answer": answer,
            "scores": scores
        })
        
        # Sleep to avoid rate limits
        time.sleep(5)

    # 3. Calculate Summary
    n = len(results)
    if n > 0:
        print("\n=== Evaluation Summary ===")
        print(f"Total Cases Evaluated: {n}")
        
        # Calculate averages dynamically
        metric_keys = results[0]["scores"].keys()
        for key in metric_keys:
            total = sum(r["scores"][key] for r in results)
            avg = (total / n) * 100
            print(f"{key}: {avg:.1f}%")
    else:
        print("No cases evaluated successfully.")

if __name__ == "__main__":
    run_evaluation()
