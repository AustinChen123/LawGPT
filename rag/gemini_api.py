from google.generativeai import embed_content
from rag.base_api import BaseEmbeddingAPI, BaseLLMAPI


class GeminiEmbeddingAPI(BaseEmbeddingAPI):
    """
    使用 Gemini 的嵌入 API 實現
    """

    def __init__(self, api_key: str):
        """
        初始化嵌入 API
        :param api_key: Google Generative AI 的 API Key
        """
        import google.generativeai as genai
        genai.configure(api_key=api_key)

    def embed_text(self, text: str) -> list:
        """
        將文本嵌入為向量
        :param text: 要嵌入的文本
        :return: 向量（list of float, 長度 768）
        """
        result = embed_content(
            model="models/text-embedding-004",
            content=text
        )
        return result["embedding"]


class GeminiLLMAPI(BaseLLMAPI):
    """
    使用 Gemini 的 LLM API 實現
    """

    def __init__(self, api_key: str, model: str = "models/gemini-1.5-flash", system_instruction: str = "You are a helpful assistant."):
        """
        初始化 LLM API
        :param model: 使用的 Gemini 模型
        :param system_instruction: 系統提示，可外部設置
        """
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel(
            model,
            system_instruction=system_instruction
        )

    def generate_response(self, prompt) -> str:
        """
        根據上下文和問題生成回答
        :param context: 提供的上下文
        :param question: 用戶的問題
        :return: 模型生成的回答
        """
        return self.llm.generate_content(prompt).text
