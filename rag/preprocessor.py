from llama_index.core.node_parser import SentenceSplitter
from typing import List
from rag.gemini_api import BaseLLMAPI, GeminiEmbeddingAPI


class Preprocessor:
    """
    預處理模組：負責文本分段與嵌入
    """

    def __init__(self, embedding_api: BaseLLMAPI, chunk_size: int = 2048, chunk_overlap: int = 200):
        """
        初始化預處理模組
        :param embedding_api: 實現 BaseEmbeddingAPI 的嵌入 API
        :param chunk_size: 文本分段大小 (Default increased to 2048 for Structural Chunking)
        :param chunk_overlap: 文本分段重疊大小
        """
        self.embedding_api = embedding_api
        self.chunk_size = chunk_size
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    def process_text(self, text: str) -> List[dict]:
        """
        Structural Chunking:
        - If text < chunk_size, keep it whole (preserve section integrity).
        - If text > chunk_size, split it using SentenceSplitter.
        """
        if len(text) <= self.chunk_size:
            chunks = [text]
        else:
            chunks = self.splitter.split_text(text)
            
        results = [{"chunk": chunk, "embedding": self.embedding_api.embed_text(
            chunk)} for chunk in chunks]
        return results
