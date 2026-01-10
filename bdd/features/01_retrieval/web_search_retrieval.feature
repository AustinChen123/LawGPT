@phase1 @retrieval @web-search
Feature: Web Search Retrieval
  As a legal researcher without vector database access
  I want to retrieve German legal documents via web search
  So that I can still get answers without Pinecone subscription

  Background:
    Given the web search retriever is configured
    And DuckDuckGo search is available

  @critical @smoke
  Scenario: Basic web search for legal documents
    Given a user query "BGB § 433 Kaufvertrag"
    When the web search retriever performs search
    Then it should return search results from "gesetze-im-internet.de"
    And results should include relevant legal documents
    And each result should have a title, URL, and snippet
    And at least 3 results should be returned

  @critical
  Scenario: Web search with site restriction
    Given a user query "Mietrecht Kündigung"
    When web search is performed with site filter "gesetze-im-internet.de"
    Then all results should be from the official legal website
    And no results from commercial legal blogs should appear
    And results should prioritize official legal texts

  Scenario: HTML content extraction from official site
    Given a search result URL from "gesetze-im-internet.de"
    When the web retriever fetches and cleans the HTML
    Then it should extract legal section content from "jnnorm" class
    And remove navigation, ads, and scripts
    And preserve section titles and paragraph structure
    And limit content to 2000 characters

  Scenario: Web search for recent legal updates
    Given a user query "neue Gesetze 2024"
    When the web search retriever performs search
    Then it should return recent results
    And results should be sorted by date (newest first)
    And include publication dates in metadata

  @performance
  Scenario: Web search latency requirements
    Given a user query "Arbeitsrecht Kündigungsschutz"
    When the web search retriever performs search
    Then the search should complete within 2 seconds
    And HTML fetching should take less than 1 second per page
    And total retrieval time should be under 4 seconds

  Scenario: Multi-query web search
    Given a user query "Mietvertrag Pflichten"
    When the web retriever expands the query to multiple variations
    Then it should generate 3-5 related queries
    And search for each variation
    And merge and deduplicate results
    And rank by relevance

  @error-handling
  Scenario: Network timeout handling
    Given a search request to an unresponsive website
    When the timeout of 5 seconds is exceeded
    Then the web retriever should cancel the request
    And return partial results from successful requests
    And log the timeout error
    And not block other searches

  Scenario: Invalid search results handling
    Given a search that returns no relevant results
    When the web retriever processes the response
    Then it should return an empty result set
    And provide a "no results found" message
    And suggest query refinement tips

  Scenario: HTML parsing failure
    Given a search result with malformed HTML
    When the web retriever attempts to extract content
    Then it should catch the parsing error
    And skip that result gracefully
    And continue processing other results
    And log the parsing failure

  @edge-cases
  Scenario: Non-legal website filtering
    Given search results include commercial legal advice sites
    When the web retriever filters results
    Then it should deprioritize non-official sources
    And add a "unofficial source" warning to metadata
    And prioritize "gesetze-im-internet.de" and "dejure.org"

  Scenario: Handling paywalled content
    Given a search result leads to a paywalled page
    When the web retriever attempts to fetch content
    Then it should detect the paywall
    And mark the result as "access restricted"
    And not return empty or error content as valid result

  Scenario: Rate limiting handling
    Given 20 consecutive search requests
    When the search provider rate limit is hit
    Then the web retriever should detect rate limiting
    And implement exponential backoff
    And queue remaining requests
    And inform the user of the delay

  @alternative-providers
  Scenario: Fallback to Google Search API
    Given DuckDuckGo search fails
    And Google Search API credentials are configured
    When the web retriever switches to Google
    Then it should use the Google Search API
    And return results in the same format
    And log the provider switch

  Scenario: Search provider comparison
    Given the same query "BGB § 433"
    When searched on both DuckDuckGo and Google
    Then both should return relevant results
    And results should have at least 60% overlap
    And response time difference should be documented

  @free-tier-limits
  Scenario: Operating within free tier limits
    Given DuckDuckGo free tier restrictions
    When 100 searches are performed in an hour
    Then all searches should complete successfully
    And no API key or payment should be required
    And rate limiting should be self-managed

  Scenario: Multilingual web search
    Given a user query in English "German contract law"
    When the web retriever translates to German
    Then it should search for "deutsches Vertragsrecht"
    And return German legal documents
    And include translation metadata
