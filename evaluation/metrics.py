from typing import List, Dict
from rag.gemini_api import GeminiLLMAPI
from config.settings import Settings
import json
import re

class RAGEvaluator:
    def __init__(self):
        settings = Settings()
        self.judge_llm = GeminiLLMAPI(
            api_key=settings.GOOGLE_API_KEY, 
            model="gemini-flash-latest", 
            system_instruction="You are an impartial judge evaluating a legal AI assistant."
        )

    def evaluate_context_relevance(self, question: str, retrieved_docs: List[dict]) -> int:
        """
        Retrieval Precision: Are the retrieved documents relevant to the question? (0/1)
        """
        if not retrieved_docs:
            return 0
            
        doc_content = "\n".join([d.get('metadata', {}).get('content', '') for d in retrieved_docs])
        prompt = (
            f"Question: {question}\n"
            f"Retrieved Documents: {doc_content}\n\n"
            "Task: Determine if the retrieved documents contain information relevant to answering the question. "
            "Output only '1' for Yes or '0' for No."
        )
        try:
            response = self.judge_llm.generate_response(prompt).strip()
            return 1 if "1" in response else 0
        except Exception:
            return 0

    def evaluate_groundedness(self, answer: str, retrieved_docs: List[dict]) -> int:
        """
        Faithfulness: Is the answer fully derived from the retrieved documents? (0/1)
        """
        if not retrieved_docs:
            return 0 # No docs implies hallucination if there is an answer
            
        doc_content = "\n".join([d.get('metadata', {}).get('content', '') for d in retrieved_docs])
        prompt = (
            f"Retrieved Documents: {doc_content}\n"
            f"AI Answer: {answer}\n\n"
            "Task: Determine if the AI Answer is fully supported by the Retrieved Documents. "
            "If the answer contains any information NOT present in the documents (hallucination), output '0'. "
            "Otherwise, output '1'."
        )
        try:
            response = self.judge_llm.generate_response(prompt).strip()
            return 1 if "1" in response else 0
        except Exception:
            return 0

    def evaluate_answer_relevance(self, question: str, answer: str) -> int:
        """
        Relevance: Does the answer actually address the user's question? (0/1)
        """
        prompt = (
            f"Question: {question}\n"
            f"AI Answer: {answer}\n\n"
            "Task: Determine if the AI Answer directly addresses the Question. "
            "Output only '1' for Yes or '0' for No."
        )
        try:
            response = self.judge_llm.generate_response(prompt).strip()
            return 1 if "1" in response else 0
        except Exception:
            return 0

    def evaluate_citation_compliance(self, answer: str) -> int:
        """
        Legal Requirement: Does the answer contain citations (e.g., §, BGB)? (0/1)
        """
        # Simple regex check for common legal symbols or format
        # Looking for § symbol or "Art." or "Section"
        if re.search(r'(§|Art\.|Section)\s*\d+', answer):
            return 1
        return 0

    def evaluate_keyword_recall(self, answer: str, expected_keywords: List[str]) -> float:
        """
        Completeness: Percentage of expected keywords present. (0.0 - 1.0)
        """
        if not expected_keywords:
            return 1.0
        
        answer_lower = answer.lower()
        found_count = 0
        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                found_count += 1
                
        return found_count / len(expected_keywords)

    def run_all_metrics(self, question: str, answer: str, retrieved_docs: List[dict], expected_keywords: List[str] = []) -> Dict[str, float]:
        return {
            "context_relevance": float(self.evaluate_context_relevance(question, retrieved_docs)),
            "groundedness": float(self.evaluate_groundedness(answer, retrieved_docs)),
            "answer_relevance": float(self.evaluate_answer_relevance(question, answer)),
            "citation_compliance": float(self.evaluate_citation_compliance(answer)),
            "keyword_recall": self.evaluate_keyword_recall(answer, expected_keywords)
        }
