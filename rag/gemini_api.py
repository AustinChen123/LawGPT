from google.genai import Client
from rag.base_api import BaseEmbeddingAPI, BaseLLMAPI


class GeminiEmbeddingAPI(BaseEmbeddingAPI):
    """
    Implementation of Embedding API using the new google.genai SDK
    """

    def __init__(self, api_key: str):
        """
        Initialize the Client
        :param api_key: Google Gen AI API Key
        """
        self.client = Client(api_key=api_key)

    def embed_text(self, text: str) -> list:
        """
        Embed text into vector
        :param text: Text to embed
        :return: Vector (list of float)
        """
        # The new SDK typically uses just the model name, e.g., "text-embedding-004"
        result = self.client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        # Accessing the first embedding's values (Native 768 dimension)
        return result.embeddings[0].values


class GeminiLLMAPI(BaseLLMAPI):
    """
    Implementation of LLM API using the new google.genai SDK
    """

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash", system_instruction: str = "You are a helpful assistant."):
        """
        Initialize LLM API
        :param model: Gemini model name
        :param system_instruction: System prompt
        """
        self.client = Client(api_key=api_key)
        # Removing "models/" prefix if present, as new SDK often handles it or prefers without, 
        # but let's be safe. Actually, let's keep it robust.
        self.model = model.replace("models/", "") 
        self.system_instruction = system_instruction

    def generate_response(self, prompt, images=None) -> str:
        """
        Generate response based on context and question, optionally with images.
        :param prompt: User prompt
        :param images: Optional image or list of images (PIL.Image or bytes)
        :return: Generated response text
        """
        contents = [prompt]
        if images:
            if isinstance(images, list):
                contents.extend(images)
            else:
                contents.append(images)

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
            config={"system_instruction": self.system_instruction}
        )
        return response.text