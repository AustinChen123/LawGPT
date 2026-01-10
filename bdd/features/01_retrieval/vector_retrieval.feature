@phase1 @retrieval @vector
Feature: Vector Database Retrieval
  As a legal researcher
  I want to retrieve relevant German legal documents from vector database
  So that I can get accurate and fast answers to legal questions

  Background:
    Given the Pinecone vector database is initialized
    And the database contains German legal documents
    And the Gemini embedding model is configured

  @critical @smoke
  Scenario: Basic vector search with relevant results
    Given a user query "Kündigungsfrist Mietvertrag"
    When the vector retriever searches the database
    Then it should return 5 relevant documents
    And each document should have a relevance score above 0.7
    And the top result should contain "BGB" or "Mietrecht"
    And each result should include metadata with "main_topic", "section_title", "link"

  @critical
  Scenario: Vector search with metadata filtering
    Given a user query "Vertragsrecht"
    And metadata filter for law category "BGB"
    When the vector retriever searches with filters
    Then all returned documents should belong to "BGB"
    And no documents from other law categories should be returned
    And results should be ranked by relevance

  Scenario: Parent document retrieval
    Given a user query "§ 433 BGB"
    When the parent document retriever is invoked
    Then it should return the small chunk matching the query
    And it should also return the full parent section
    And the parent section should contain complete legal context
    And the parent should be at least 3x larger than the child chunk

  Scenario: Vector search with no relevant results
    Given a user query "alien invasion laws"
    When the vector retriever searches the database
    Then it should return an empty result set
    Or all results should have relevance scores below 0.5
    And the system should flag this as low-confidence retrieval

  Scenario: Multilingual embedding consistency
    Given a user query in English "contract termination notice period"
    And the same query translated to German "Kündigungsfrist Vertrag"
    When both queries are embedded and searched
    Then the top 3 results should be identical
    Or have at least 80% overlap in returned documents

  @performance
  Scenario: Vector search latency requirements
    Given a user query "Mietrecht Kündigung"
    When the vector retriever performs search
    Then the search should complete within 100 milliseconds
    And the embedding generation should take less than 200 milliseconds
    And the total retrieval time should be under 500 milliseconds

  Scenario: Batch vector search
    Given 10 user queries about different legal topics
    When batch vector search is performed
    Then all queries should be processed
    And results should be returned in the same order
    And no individual query should fail silently
    And total processing time should be less than 5 seconds

  Scenario: Vector search with MMR diversity
    Given a user query "Kaufvertrag BGB"
    When MMR (Maximal Marginal Relevance) is enabled
    Then results should cover diverse aspects of the topic
    And duplicate or highly similar results should be filtered
    And relevance scores should remain above 0.6

  @error-handling
  Scenario: Vector database connection failure
    Given the Pinecone connection is unavailable
    When a user attempts a vector search
    Then the system should catch the connection error
    And return a clear error message
    And suggest fallback to web search mode
    And log the error for monitoring

  Scenario: Invalid API key handling
    Given an invalid Pinecone API key is configured
    When the vector retriever is initialized
    Then it should raise an authentication error
    And provide instructions to check the API key
    And not proceed with query execution

  @edge-cases
  Scenario: Empty query handling
    Given an empty string as user query
    When the vector retriever processes the query
    Then it should reject the query with validation error
    And provide a helpful error message
    And not make unnecessary API calls

  Scenario: Very long query handling
    Given a user query with 500 words
    When the vector retriever processes the query
    Then it should truncate or summarize the query
    And still return relevant results
    And log a warning about query length

  Scenario: Special characters in query
    Given a query with German special characters "§ 433 Ä Ö Ü ß"
    When the vector retriever processes the query
    Then it should handle special characters correctly
    And return relevant results about "§ 433"
    And not fail due to encoding issues
