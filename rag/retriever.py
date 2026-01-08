import pinecone
from rag.gemini_api import GeminiEmbeddingAPI
from config.settings import Settings

class Retriever:
    """
    Handles retrieval of documents from the vector database.
    """

    def __init__(self):
        """
        Initializes the retriever with Pinecone and embedding API.
        """
        self.settings = Settings()
        pc = pinecone.Pinecone(api_key=self.settings.PINECONE_API_KEY)
        self.index = pc.Index(host=self.settings.PINECONE_HOST)
        self.embedding_api = GeminiEmbeddingAPI(self.settings.GOOGLE_API_KEY)

    def query(self, query_text: str, top_k: int = 10) -> list[dict]:
        """
        Embeds a query and retrieves the top_k most relevant documents.

        Args:
            query_text: The text to search for.
            top_k: The number of documents to return.

        Returns:
            A list of dictionaries, where each dictionary represents a retrieved document
            with its metadata and score.
        """
        vector = self.embedding_api.embed_text(query_text)
        response = self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )
        matches = response.get("matches", [])
        return [
            {
                "id": match.get("id"),
                "score": match.get("score"),
                "metadata": match.get("metadata", {}),
            }
            for match in matches
        ]

    def get_definition(self, term: str) -> str:
        """
        A specialized function to retrieve a definition for a specific term.
        This could be implemented by searching for a specific metadata tag or by
        structuring queries in a specific way.
        
        For now, it's a placeholder that performs a standard query.
        """
        # This is a simplification. A real implementation might search for documents
        # tagged as "definition" or with the exact title of the term.
        results = self.query(f"Definition of {term}", top_k=1)
        if results and "content" in results[0].get("metadata", {}):
            return results[0]["metadata"]["content"]
        return "Definition not found."

    def list_related_articles(self, article_id: str) -> list[dict]:
        """
        Finds articles related to a given article_id.
        This could be implemented using Pinecone's `fetch` and then finding
        related articles based on metadata, or by using the vector of the given
        article to find similar vectors.

        For now, it's a placeholder.
        """
        # This is a simplification. A real implementation would be more sophisticated.
        print(f"Finding articles related to {article_id}... (Not yet implemented)")
        return []
