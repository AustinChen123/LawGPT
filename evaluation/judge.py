from rag.gemini_api import GeminiLLMAPI
from config.settings import Settings
import json

class RagasJudge:
    def __init__(self):
        settings = Settings()
        self.llm = GeminiLLMAPI(api_key=settings.GOOGLE_API_KEY, model="gemini-flash-latest")

    def evaluate_context_recall(self, ground_truth: str, retrieved_contexts: list) -> float:
        """
        RAGAS Metric: Context Recall
        Does the retrieved context contain the information needed to answer the ground truth?
        Score: 0.0 - 1.0
        """
        context_text = "\n".join(retrieved_contexts)
        prompt = (
            f"**Ground Truth Answer:** {ground_truth}\n\n"
            f"**Retrieved Context:**\n{context_text}\n\n"
            f"**Task:** Determine if the Retrieved Context contains the necessary information to derive the Ground Truth Answer.\n"
            f"Respond with a score between 0.0 (No relevant info) and 1.0 (All info present).\n"
            f"Output ONLY the number."
        )
        try:
            score = float(self.llm.generate_response(prompt).strip())
            return min(max(score, 0.0), 1.0)
        except:
            return 0.0

    def evaluate_faithfulness(self, answer: str, retrieved_contexts: list) -> float:
        """
        RAGAS Metric: Faithfulness
        Is the generated answer derived *only* from the retrieved context? (Hallucination check)
        Score: 0.0 - 1.0
        """
        if not retrieved_contexts:
            return 0.0 if answer else 1.0 # No context, no answer = faithful
            
        context_text = "\n".join(retrieved_contexts)
        prompt = (
            f"**Retrieved Context:**\n{context_text}\n\n"
            f"**Agent Answer:** {answer}\n\n"
            f"**Task:** Evaluate Faithfulness. Analyze each claim in the Agent Answer.\n"
            f"- If a claim is supported by Context, count it as verified.\n"
            f"- If a claim is NOT in Context, count it as hallucination.\n"
            f"Calculate the ratio of verified claims to total claims (0.0 to 1.0).\n"
            f"Output ONLY the number."
        )
        try:
            score = float(self.llm.generate_response(prompt).strip())
            return min(max(score, 0.0), 1.0)
        except:
            return 0.0
