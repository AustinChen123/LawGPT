@phase2 @agent @callbacks @tracing
Feature: Agent Callbacks and Reasoning Trace
  As a developer or power user
  I want to capture the agent's reasoning process
  So that I can debug, visualize, and understand decisions

  Background:
    Given the LegalAdvisorAgent is initialized
    And AgentTraceCallback is registered
    And TokenCountCallback is registered

  @critical @smoke
  Scenario: AgentTraceCallback captures all reasoning steps
    Given a user query "What is BGB § 433?"
    When the agent processes the query
    Then the trace should capture:
      | step_number | thought                          | action      | observation         |
      | 1           | Need to search for BGB § 433     | search_law  | Found section...    |
      | 2           | Information complete             | -           | Generate answer     |
    And each step should have a timestamp
    And each step should have duration in milliseconds

  @critical
  Scenario: Trace captures tool inputs and outputs
    Given the agent invokes search_law tool
    When the trace records the action
    Then it should capture:
      | field         | example                           |
      | action_name   | search_law                        |
      | action_input  | "Mietvertrag Kündigung"          |
      | observation   | Full tool output string           |
      | duration_ms   | 450                               |
      | timestamp     | 2024-01-15 10:30:45.123          |

  Scenario: Trace captures Thought process
    Given the agent is reasoning about a query
    When AgentTraceCallback captures the thought
    Then it should extract text between "Thought:" and "Action:"
    And clean formatting and extra whitespace
    And store as the "thought" field
    And preserve original phrasing

  Scenario: Trace handles final answer step
    Given the agent reaches a conclusion
    When it generates final answer
    Then the trace should capture:
      | field       | value                        |
      | thought     | "Ready to generate answer"   |
      | action      | "final_answer"               |
      | observation | The complete answer text     |

  @token-tracking
  Scenario: TokenCountCallback tracks prompt tokens
    Given the agent sends a prompt to LLM
    When the callback receives on_llm_start event
    Then it should estimate prompt tokens
    And add to total prompt_tokens counter
    And track per-call token usage

  Scenario: TokenCountCallback tracks completion tokens
    Given the LLM returns a response
    When the callback receives on_llm_end event
    Then it should extract completion_tokens from response
    And add to total completion_tokens counter
    And calculate total_tokens

  Scenario: Token usage includes all LLM calls
    Given the agent makes multiple LLM calls during reasoning
    When all calls complete
    Then total tokens should sum all individual calls
    And breakdown by prompt vs completion should be accurate
    And enable cost calculation

  @cost-calculation
  Scenario: Calculating cost from token usage
    Given prompt_tokens = 1000
    And completion_tokens = 500
    And Gemini 2.0 Flash pricing (prompt: $0.075/1M, completion: $0.30/1M)
    When cost is calculated
    Then estimated cost should be:
      | component  | calculation           | cost      |
      | Prompt     | 1000 * 0.075 / 1M     | $0.000075 |
      | Completion | 500 * 0.30 / 1M       | $0.000150 |
      | Total      | Sum                   | $0.000225 |

  @performance-tracking
  Scenario: Tracking retrieval latency
    Given the agent uses search_law tool
    When the trace records the action
    Then it should calculate retrieval_latency_ms
    And store it in metadata
    And enable performance analysis

  Scenario: Tracking total query latency
    Given a user query starts processing
    When processing completes
    Then total latency should be calculated
    And broken down by:
      | component        | approximate percentage |
      | Retrieval        | 30%                    |
      | LLM reasoning    | 50%                    |
      | Tool execution   | 15%                    |
      | Other overhead   | 5%                     |

  @callback-lifecycle
  Scenario: Callback initialization
    Given the agent is initialized
    When callbacks are registered
    Then AgentTraceCallback.trace should be empty list
    And TokenCountCallback counters should be zero
    And callbacks should be ready to record

  Scenario: Callback reset between queries
    Given the agent has processed a query
    And trace contains previous steps
    When a new query starts
    Then callbacks should be reset
    And trace should be cleared
    And token counters should restart at zero

  Scenario: Multiple callbacks coexist
    Given AgentTraceCallback and TokenCountCallback are both active
    When the agent processes a query
    Then both callbacks should receive events
    And not interfere with each other
    And both should produce complete outputs

  @error-handling
  Scenario: Callback handles malformed agent output
    Given the agent produces unexpected output format
    When the callback tries to parse thought/action
    Then it should catch the parsing error
    And log a warning
    And continue without crashing
    And mark that step as "parse_error"

  Scenario: Callback handles missing events
    Given on_tool_start is called but on_tool_end never fires
    When the trace is retrieved
    Then it should detect incomplete steps
    And mark them as "incomplete"
    And not include partial data in final trace

  @trace-export
  Scenario: Exporting trace as JSON
    Given a completed agent trace
    When trace.to_json() is called
    Then it should return valid JSON string
    And include all steps with full data
    And be parsable back to trace object

  Scenario: Exporting trace as structured data
    Given a completed agent trace
    When trace.get_trace() is called
    Then it should return list of dictionaries
    And each dictionary should have consistent schema
    And be ready for visualization or analysis

  @visualization-support
  Scenario: Trace format supports Mermaid diagram generation
    Given a multi-step reasoning trace
    When generating Mermaid diagram code
    Then trace should provide:
      | element      | usage                          |
      | step_id      | Node identifiers               |
      | thought      | Node labels                    |
      | action       | Edge labels                    |
      | flow         | Sequential connections         |

  Scenario: Trace format supports timeline visualization
    Given reasoning trace with timestamps and durations
    When creating timeline chart
    Then trace should provide:
      | data point     | value                    |
      | step_name      | "Step 1: search_law"     |
      | start_time     | Relative milliseconds    |
      | duration       | Time taken               |
      | action_type    | For color coding         |

  @metadata-enrichment
  Scenario: Adding custom metadata to trace
    Given an agent reasoning step
    When additional context is available
    Then trace should allow custom metadata
    And metadata should include:
      | field             | example                     |
      | retrieval_mode    | "hybrid"                    |
      | num_docs_found    | 5                           |
      | avg_relevance     | 0.87                        |
      | tool_version      | "1.0"                       |
