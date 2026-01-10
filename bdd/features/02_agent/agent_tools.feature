@phase2 @agent @tools
Feature: Agent Tool Functionality
  As an agent
  I want access to specialized tools
  So that I can perform specific tasks efficiently

  Background:
    Given all agent tools are initialized
    And proper API credentials are configured

  @critical @smoke
  Scenario: search_law tool basic functionality
    Given the search_law tool
    And a query "Kündigungsfrist Mietvertrag"
    When the tool is invoked
    Then it should return a formatted string with:
      | field           | presence |
      | Document title  | Yes      |
      | Law reference   | Yes      |
      | Content preview | Yes      |
      | Source link     | Yes      |
      | Relevance score | Yes      |
    And results should be numbered [1], [2], [3]...

  Scenario: search_law with metadata filtering
    Given the search_law tool
    And query "Vertragsrecht"
    And filter {"law_category": "BGB"}
    When the tool is invoked with filters
    Then all returned documents should be from BGB
    And metadata should confirm the filtering
    And results should indicate filter was applied

  Scenario: search_law with top_k parameter
    Given the search_law tool
    And query "Kaufvertrag"
    And top_k parameter set to 3
    When the tool is invoked
    Then exactly 3 results should be returned
    And they should be the top 3 most relevant

  @critical
  Scenario: cite_law tool extracts legal references
    Given the cite_law tool
    And text "Nach BGB § 433 und § 434 sowie StGB § 263"
    When the tool is invoked
    Then it should extract:
      | law  | section |
      | BGB  | 433     |
      | BGB  | 434     |
      | StGB | 263     |
    And format them as structured list
    And remove duplicates

  Scenario: cite_law handles various citation formats
    Given the cite_law tool
    And text containing various formats:
      | format                    |
      | BGB § 433                 |
      | BGB §433                  |
      | § 433 BGB                 |
      | GG Art. 1                 |
      | Artikel 1 GG              |
    When the tool processes all formats
    Then all should be correctly extracted
    And normalized to consistent format

  Scenario: cite_law handles no citations
    Given the cite_law tool
    And text with no legal citations
    When the tool is invoked
    Then it should return "No citations found"
    And not throw an error

  @critical
  Scenario: translate tool basic translation
    Given the translate tool
    And text "Die Rechtsfähigkeit beginnt mit Vollendung der Geburt"
    And target language "en"
    When the tool is invoked
    Then it should return English translation
    And preserve legal terminology accuracy
    And keep law references untranslated (e.g., "BGB §1")

  Scenario: translate tool handles multiple languages
    Given the translate tool
    And German legal text
    When translating to different targets:
      | target_lang | expected_output_language |
      | en          | English                  |
      | zh          | Simplified Chinese       |
      | zh-tw       | Traditional Chinese      |
    Then all translations should be accurate
    And maintain legal precision

  Scenario: translate preserves legal citations
    Given text "Nach BGB § 433 ist der Verkäufer verpflichtet..."
    When translated to English
    Then "BGB § 433" should remain unchanged
    And not be translated to "Civil Code § 433"

  @critical
  Scenario: get_full_context retrieves parent document
    Given the get_full_context tool
    And a section identifier "BGB § 433"
    When the tool is invoked
    Then it should return the complete section
    And include all subsections (Absatz 1, 2, etc.)
    And provide surrounding context
    And include proper formatting

  Scenario: get_full_context handles invalid references
    Given the get_full_context tool
    And an invalid section "BGB § 99999"
    When the tool is invoked
    Then it should return "Section not found"
    And suggest checking the reference
    And not throw an error

  @tool-descriptions
  Scenario: Tool descriptions are clear and helpful
    Given all tools are registered
    When the agent needs to select a tool
    Then each tool description should clearly state:
      | element         | requirement                      |
      | Purpose         | What the tool does               |
      | Parameters      | What inputs it expects           |
      | Output format   | What it returns                  |
      | Use cases       | When to use it                   |
      | Examples        | Sample invocations               |
    And help the agent make correct choices

  @error-handling
  Scenario: Tool handles missing parameters
    Given the search_law tool
    And query parameter is missing
    When the tool is invoked
    Then it should return a clear error message
    And specify which parameter is missing
    And provide example of correct usage

  Scenario: Tool handles invalid parameter types
    Given the search_law tool
    And top_k parameter is a string instead of int
    When the tool is invoked
    Then it should validate parameter types
    And return a type error message
    And not cause system crash

  Scenario: Tool timeout handling
    Given the search_law tool
    And a search takes longer than 10 seconds
    When timeout is reached
    Then the tool should cancel the operation
    And return a timeout error
    And allow the agent to try alternative approaches

  @performance
  Scenario: Tool execution time tracking
    Given any tool is invoked
    When execution begins
    Then start time should be recorded
    When execution completes
    Then end time should be recorded
    And duration should be calculated
    And included in tool output metadata

  Scenario: Parallel tool execution
    Given multiple independent tool calls
    When the agent needs results from multiple tools
    Then tools should execute in parallel where possible
    And not wait for sequential completion
    And aggregate results efficiently

  @caching
  Scenario: Tool result caching
    Given the search_law tool
    And the same query is executed twice within 5 minutes
    When the second call is made
    Then the cached result should be returned
    And no new API call should be made
    And cache hit should be logged

  Scenario: Cache invalidation
    Given cached tool results exist
    When cache TTL of 15 minutes expires
    Then cached results should be invalidated
    And next call should fetch fresh results
    And update the cache

  @integration
  Scenario: Tool integration with retrieval modes
    Given the search_law tool
    And the agent is in "vector" retrieval mode
    When the tool is invoked
    Then it should use vector database retriever
    And if mode is "web"
    Then it should use web search retriever
    And maintain consistent interface regardless of mode
