@phase2 @agent @react
Feature: ReAct Agent Reasoning and Actions
  As a user asking complex legal questions
  I want the agent to reason through problems step-by-step
  So that I receive well-thought-out and accurate answers

  Background:
    Given the LegalAdvisorAgent is initialized
    And ReAct agent with reasoning trace is active
    And agent tools are registered

  @critical @smoke
  Scenario: Basic reasoning loop - Thought, Action, Observation
    Given a user query "Can a landlord increase rent at any time?"
    When the ReAct agent processes the query
    Then the agent should:
      | step        | action                                    |
      | Thought 1   | Analyze query, decide to search law       |
      | Action 1    | search_law("Mieterhöhung Voraussetzungen")|
      | Observation 1| Retrieved BGB § 558 results              |
      | Thought 2   | Results sufficient, formulate answer      |
      | Final Answer| No, landlord needs valid reasons...       |
    And the reasoning trace should contain all steps

  @critical
  Scenario: Multi-step reasoning with tool chaining
    Given a user query "What are my rights if my landlord violates the contract?"
    When the agent reasons through the problem
    Then it should execute multiple actions in sequence:
      | step | tool              | purpose                           |
      | 1    | search_law        | Find contract violation laws      |
      | 2    | get_full_context  | Retrieve complete legal section   |
      | 3    | cite_law          | Extract specific citations        |
      | 4    | translate         | Translate to user's language      |
    And each action should inform the next thought
    And the final answer should synthesize all information

  Scenario: Agent decides no action needed
    Given a user query "Thank you for the help"
    When the agent processes the query
    Then it should recognize this as conversational
    And decide no tool action is needed
    And generate a polite response directly
    And not waste API calls on unnecessary searches

  Scenario: Agent self-correction after incorrect tool use
    Given a user query about "Strafrecht" (criminal law)
    When the agent initially searches with wrong keywords
    And observes irrelevant results
    Then it should recognize the mistake in its thought
    And try a corrected search with better keywords
    And eventually find relevant criminal law sections

  @tool-selection
  Scenario: Intelligent tool selection for specific law query
    Given a user query "What does BGB § 433 say?"
    When the agent analyzes the query
    Then it should recognize the specific law reference
    And choose search_law with exact section number
    And not waste time with translation
    And retrieve the exact section efficiently

  Scenario: Tool selection for context-seeking query
    Given a user query "Explain the concept of Kaufvertrag"
    When the agent analyzes the query
    Then it should recognize need for broad context
    And use search_law with broader query
    And then get_full_context for comprehensive information
    And possibly translate for explanation clarity

  Scenario: Tool selection for citation extraction
    Given agent has retrieved a long legal text
    When the agent needs to reference specific laws
    Then it should use cite_law tool
    And extract all § references
    And format them properly (BGB § 433, § 434)

  @max-iterations
  Scenario: Agent respects maximum iteration limit
    Given max_iterations is set to 5
    And a complex query requires many steps
    When the agent starts reasoning
    Then it should complete within 5 iterations
    Or gracefully stop and admit it needs more steps
    And provide the best answer possible so far

  Scenario: Agent reaches answer before max iterations
    Given max_iterations is set to 10
    And a simple query only needs 2 steps
    When the agent processes the query
    Then it should stop after finding the answer
    And not continue unnecessarily to max iterations
    And save computation costs

  @error-handling
  Scenario: Agent handles tool failure gracefully
    Given a user query requiring search
    When the search_law tool fails with network error
    Then the agent should observe the error
    And think of an alternative approach
    And try a different tool or strategy
    And inform the user if unable to proceed

  Scenario: Agent handles parsing errors
    Given the agent's output format is malformed
    When the executor detects parsing error
    Then it should invoke error recovery
    And prompt the agent to reformat
    And continue execution with corrected output

  Scenario: Agent handles timeout
    Given max_execution_time is 30 seconds
    And the agent gets stuck in complex reasoning
    When 30 seconds elapse
    Then execution should be terminated
    And partial results should be returned if available
    And timeout reason should be logged

  @memory-management
  Scenario: Agent uses conversation memory for context
    Given a user asks "What is BGB § 433?"
    And the agent provides an answer
    When the user follows up with "What are the exceptions?"
    Then the agent should recall "§ 433" from memory
    And understand "exceptions" refers to the previous law
    And provide relevant exceptions without re-searching § 433

  Scenario: Memory persists across session
    Given a conversation about rental law
    And the session is saved
    When the user returns later and asks "Can you remind me what we discussed?"
    Then the agent should retrieve conversation history
    And summarize previous topics (rental law)
    And offer to continue from where they left off

  @prompt-engineering
  Scenario: Agent follows system instructions
    Given the system prompt specifies "always cite sources"
    When the agent generates any legal answer
    Then the answer should include citations
    And provide links to source documents
    And follow the instructed format

  Scenario: Agent avoids hallucination
    Given the system prompt warns against speculation
    When the agent doesn't find relevant documents
    Then it should admit uncertainty
    And not make up legal information
    And suggest consulting a professional lawyer
    And not say "from documents" when there aren't any

  @intermediate-steps
  Scenario: Capturing detailed intermediate steps
    Given return_intermediate_steps is True
    When the agent processes a query
    Then the response should include:
      | field              | content                          |
      | output             | Final answer text                |
      | intermediate_steps | List of (action, observation)    |
      | reasoning_trace    | Thought process for each step    |
    And these can be used for visualization

  @language-handling
  Scenario: Agent handles multilingual queries
    Given a user asks in English "What is German contract law?"
    When the agent processes the query
    Then it should detect the language
    And translate to German for search
    And search German legal database
    And translate results back to English
    And cite German law names correctly (BGB, not "Civil Code")
