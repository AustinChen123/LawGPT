@phase1-4 @integration @e2e
Feature: End-to-End Query Workflow
  As a user
  I want to ask legal questions and get accurate answers
  So that I can understand German law

  Background:
    Given the LawGPT system is fully operational
    And all components are initialized

  @critical @smoke
  Scenario: Simple legal question - Complete workflow
    Given a user asks "What is BGB § 433?"
    When the system processes the query
    Then it should:
      | step                  | action                          |
      | Detect language       | English                         |
      | Select retrieval      | Vector DB (specific law query)  |
      | Search documents      | Find BGB § 433                  |
      | Extract context       | Get full section content        |
      | Generate answer       | Explain Kaufvertrag definition  |
      | Cite sources          | BGB § 433 with link             |
      | Translate if needed   | Keep English                    |
    And the answer should be accurate and complete
    And total latency should be under 3 seconds

  @critical
  Scenario: Complex multi-step reasoning query
    Given a user asks "Can my landlord increase rent and evict me at the same time?"
    When the system processes the query
    Then the agent should:
      | step | reasoning                              |
      | 1    | Two separate issues: rent increase + eviction |
      | 2    | Search for "Mieterhöhung" laws         |
      | 3    | Search for "Kündigung" laws            |
      | 4    | Compare and analyze both               |
      | 5    | Formulate comprehensive answer         |
    And cite multiple law sections (BGB § 558, § 573, etc.)
    And explain the relationship between both issues
    And provide practical guidance

  Scenario: Query requiring web search fallback
    Given Pinecone vector database is unavailable
    And a user asks "What are the recent changes to rental law?"
    When the system detects vector DB failure
    Then it should automatically fallback to web search
    And search "neue Mietrecht Änderungen 2024"
    And retrieve recent legal updates
    And inform user that results are from web search
    And still provide accurate answer

  Scenario: Multilingual query flow
    Given a user asks in Chinese "租房合同可以隨時終止嗎?"
    When the system processes the query
    Then it should:
      | step                 | action                             |
      | Detect language      | Traditional Chinese                |
      | Translate to German  | "Kann Mietvertrag jederzeit..."   |
      | Search German laws   | Find relevant BGB sections         |
      | Generate answer      | In German                          |
      | Translate to Chinese | Final answer in Traditional Chinese|
    And maintain legal terminology accuracy
    And preserve law references (BGB § 573)

  @conversation-flow
  Scenario: Multi-turn conversation with context
    Given the following conversation:
      | turn | user_message                                      |
      | 1    | "What is BGB § 433?"                              |
      | 2    | "What are the exceptions?"                        |
      | 3    | "Can you give an example?"                        |
    When each turn is processed
    Then turn 2 should understand "exceptions" refers to § 433
    And turn 3 should provide example of § 433 exceptions
    And conversation memory should retain all context
    And not require re-searching for § 433 in turns 2-3

  Scenario: Context switching in conversation
    Given a conversation about rental law
    And user suddenly asks "What about employment law termination?"
    When the agent processes the new topic
    Then it should recognize topic change
    And not confuse rental termination with employment termination
    And search appropriate laws (Arbeitsrecht)
    And maintain both contexts in memory

  @hybrid-retrieval
  Scenario: Hybrid retrieval for comprehensive answer
    Given hybrid retrieval mode is active
    And a user asks "What is Kaufvertrag in German law?"
    When the system searches
    Then vector database should find BGB § 433 (fast, accurate)
    And web search should find explanatory articles (context-rich)
    And results should be merged and reranked
    And answer should combine statutory definition + practical explanation

  Scenario: Adaptive retrieval based on query type
    Given adaptive retrieval mode
    When user asks "BGB § 433" (specific law)
    Then vector database should be prioritized
    When user asks "latest contract law changes" (recent info)
    Then web search should be prioritized
    And each should use optimal retrieval strategy

  @error-recovery
  Scenario: Graceful degradation with partial failures
    Given vector database is slow (>3s response time)
    And web search is available
    When a user query is received
    Then system should timeout vector search at 3s
    And immediately use web search results
    And inform user of degraded performance
    And still deliver an answer

  Scenario: Complete system failure handling
    Given all retrieval methods fail
    When a user asks a question
    Then the system should:
      | action                          | message                           |
      | Detect all failures             | -                                 |
      | Not fabricate information       | -                                 |
      | Return honest error             | "Unable to retrieve documents"    |
      | Suggest troubleshooting         | Check API keys, network, etc.     |
      | Offer to retry                  | Button to retry query             |

  @citation-accuracy
  Scenario: Accurate citation extraction
    Given a query about multiple laws
    When the agent generates answer mentioning:
      | law reference  |
      | BGB § 433      |
      | BGB § 434      |
      | BGB § 535      |
    Then all citations should be extracted
    And formatted consistently (BGB § 433, not "§433 BGB")
    And each should have clickable link
    And links should navigate to correct sections

  Scenario: Citation validation
    Given the agent mentions "BGB § 99999"
    When citation extraction runs
    Then it should detect invalid section number
    And flag as "citation not verified"
    And suggest user verify the reference

  @performance
  Scenario: Performance under load
    Given 10 users submit queries simultaneously
    When all queries are processed
    Then each should complete within 5 seconds
    And no query should fail due to resource contention
    And retrieval should use connection pooling
    And LLM calls should be batched where possible

  Scenario: Caching for common queries
    Given a user asks "What is BGB § 433?"
    And this query was asked 1 minute ago
    When the system processes the query
    Then it should check cache first
    And return cached results (if still valid)
    And save 90% of processing time
    And token costs

  @data-privacy
  Scenario: No sensitive data retention
    Given a user asks about personal legal situation
    When the conversation ends
    Then conversation history should not be saved to disk
    And should only exist in session memory
    And be cleared when session ends
    And comply with GDPR requirements

  @quality-assurance
  Scenario: Answer quality validation
    Given a generated answer
    When quality checks are performed
    Then answer should:
      | criterion              | requirement              |
      | Cites sources          | At least 1 law reference |
      | Factual accuracy       | No hallucinated laws     |
      | Completeness           | Addresses question fully |
      | Professional tone      | Formal legal language    |
      | Disclaimer             | Suggests consulting lawyer|

  Scenario: Hallucination prevention
    Given the agent doesn't find relevant documents
    When generating an answer
    Then it should NOT invent legal information
    And should admit uncertainty
    And recommend consulting legal professional
    And explain why it couldn't find information
