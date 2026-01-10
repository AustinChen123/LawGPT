@phase1 @retrieval @hybrid
Feature: Hybrid Retrieval Strategies
  As a power user
  I want the system to intelligently combine vector and web search
  So that I get the best of both retrieval methods

  Background:
    Given both vector database and web search are available
    And the hybrid retriever is configured

  @critical @smoke
  Scenario: Fallback strategy - Vector first, Web on failure
    Given the hybrid retriever is set to "fallback" mode
    And a user query "BGB § 433"
    When the vector search returns no results above threshold 0.7
    Then the system should automatically try web search
    And return results from web search
    And mark results with source "web_search_fallback"
    And log the fallback trigger

  @critical
  Scenario: Ensemble strategy - Merge vector and web results
    Given the hybrid retriever is set to "ensemble" mode
    And a user query "Mietrecht Kündigung"
    When both vector and web search are executed in parallel
    Then results from both sources should be merged
    And duplicates should be removed based on content similarity
    And results should be reranked by relevance
    And the top 5 results should be returned
    And each result should indicate its source

  @critical
  Scenario: Adaptive strategy - Query type detection
    Given the hybrid retriever is set to "adaptive" mode
    And a user query contains "§" and a specific law number
    When the adaptive strategy analyzes the query
    Then it should detect this as a "specific law query"
    And prioritize vector database search
    And skip web search unless vector fails
    And log the decision reasoning

  Scenario: Adaptive strategy - Recent law query detection
    Given the hybrid retriever is set to "adaptive" mode
    And a user query contains "2024" or "neu" or "aktuell"
    When the adaptive strategy analyzes the query
    Then it should detect this as a "recent law query"
    And prioritize web search for latest information
    And use vector search only for context enrichment
    And clearly mark which results are recent

  Scenario: Auto mode - No Pinecone key provided
    Given the hybrid retriever is set to "auto" mode
    And no Pinecone API key is configured
    When a user query is received
    Then the system should automatically use web search only
    And not attempt vector database connection
    And inform the user they are in "free mode"
    And suggest upgrading for faster results

  Scenario: Auto mode - Both retrievers available
    Given the hybrid retriever is set to "auto" mode
    And both Pinecone and web search are configured
    When a user query is received
    Then the system should use adaptive strategy
    And intelligently select retrieval method based on query
    And provide transparency on which method was used

  @performance
  Scenario: Ensemble parallel execution performance
    Given the hybrid retriever uses ensemble mode
    And a user query "Arbeitsrecht"
    When both retrievers execute in parallel
    Then total retrieval time should be only slightly higher than the slowest retriever
    And not the sum of both retrieval times
    And parallel execution should save at least 30% time

  Scenario: Hybrid result deduplication
    Given ensemble mode returns overlapping results
    When the same document appears in both vector and web results
    Then only one copy should be kept in final results
    And the kept result should combine metadata from both sources
    And relevance score should be the maximum of both scores
    And source should be marked as "vector+web"

  Scenario: Hybrid result reranking
    Given ensemble mode has merged 10 results (5 vector + 5 web)
    When cross-encoder reranker is applied
    Then results should be reordered by true relevance
    And the top result should be the most semantically relevant
    And source diversity should be maintained (not all from one source)

  @error-handling
  Scenario: Partial failure in ensemble mode
    Given ensemble mode is active
    And vector search fails with connection error
    But web search succeeds
    When the hybrid retriever processes results
    Then it should return web search results only
    And include a warning about vector search failure
    And suggest retrying later
    And not fail the entire query

  Scenario: Both retrievers fail in ensemble mode
    Given ensemble mode is active
    And vector search times out
    And web search is rate limited
    When the hybrid retriever attempts retrieval
    Then it should catch both errors
    And return a comprehensive error message
    And log both failures for monitoring
    And suggest checking system status

  Scenario: Confidence threshold for fallback trigger
    Given fallback mode is active
    And confidence threshold is set to 0.7
    When vector search returns results with max score 0.65
    Then fallback to web search should be triggered
    But if max score is 0.75
    Then fallback should not be triggered
    And vector results should be returned

  @adaptive-logic
  Scenario: Adaptive strategy - General exploration query
    Given a broad query "German contract law overview"
    When adaptive strategy analyzes the query
    Then it should detect this as "exploratory query"
    And use ensemble mode for comprehensive coverage
    And return diverse results from both sources

  Scenario: Adaptive strategy - Case law query
    Given a query mentioning "Urteil" or "Rechtsprechung"
    When adaptive strategy analyzes the query
    Then it should detect this as "case law query"
    And prioritize web search for recent cases
    And use vector search for related statutes

  Scenario: Adaptive strategy - Learning query
    Given a query with "erklären" or "verstehen" or "explain"
    When adaptive strategy analyzes the query
    Then it should detect this as "educational query"
    And use ensemble mode for rich context
    And prioritize results with comprehensive explanations

  @strategy-switching
  Scenario: Runtime strategy switching
    Given a user starts with fallback mode
    When they receive poor results
    And manually switch to ensemble mode
    Then the system should apply the new strategy immediately
    And re-execute the last query
    And compare results from both strategies

  Scenario: Strategy recommendation based on performance
    Given query history shows fallback triggers 80% of the time
    When the system analyzes usage patterns
    Then it should recommend switching to ensemble mode
    And explain the performance benefits
    And offer to change the default setting

  @cost-optimization
  Scenario: Cost-aware hybrid retrieval
    Given ensemble mode with both vector and web active
    And token usage is approaching monthly limit
    When a new query is received
    Then the system should prefer vector database (fixed cost)
    And minimize LLM-based web result processing
    And track and report cost savings

  Scenario: Free tier optimization
    Given a user on free tier (no Pinecone)
    And web search rate limits apply
    When multiple queries are received rapidly
    Then the system should implement smart caching
    And reuse recent search results when applicable
    And inform user of rate limit approaching
