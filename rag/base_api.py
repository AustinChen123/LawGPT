from abc import ABC, abstractmethod


class BaseEmbeddingAPI(ABC):
    """
    抽象類別：定義嵌入模型的接口
    """
    @abstractmethod
    def embed_text(self, text: str) -> list:
        """
        將文本嵌入為向量
        :param text: 要嵌入的文本
        :return: 向量（list of float）
        """
        pass


class BaseLLMAPI(ABC):
    """
    抽象類別：定義 LLM 的接口
    """
    @abstractmethod
    def generate_response(self, context: str, question: str) -> str:
        """
        根據上下文和問題生成回答
        :param context: 提供的上下文
        :param question: 用戶的問題
        :return: 模型生成的回答
        """
        pass
