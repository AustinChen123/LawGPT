@phase3 @ui @visualization
Feature: Agent Reasoning Visualization Components
  As a user or developer
  I want to see how the agent thinks
  So that I can understand and trust its decisions

  Background:
    Given the Streamlit visualization module is loaded
    And the agent has processed a query with reasoning trace

  @critical @smoke
  Scenario: Reasoning timeline view
    Given agent reasoning trace with 3 steps
    When render_agent_trace() is called
    Then it should display timeline with:
      | step | icon | content                          |
      | 1    | 🔍   | Thought, Action, Observation     |
      | 2    | 📜   | Thought, Action, Observation     |
      | 3    | ✅   | Final thought and answer         |
    And steps should be visually separated by dividers

  @critical
  Scenario: Expandable reasoning steps
    Given a reasoning step with long observation
    When the step is displayed
    Then the observation should be in collapsible section
    And default state should be collapsed
    And user can click to expand
    And full content should be revealed

  Scenario: Step icons based on action type
    Given reasoning trace with different actions
    Then icons should match action type:
      | action         | icon |
      | search_law     | 🔍   |
      | cite_law       | 📜   |
      | translate      | 🌐   |
      | get_context    | 📖   |
      | final_answer   | ✅   |
      | error          | ❌   |

  @mermaid-diagram
  Scenario: Generate Mermaid flow diagram
    Given agent trace with sequential steps
    When generate_mermaid_flow() is called
    Then it should produce valid Mermaid syntax
    And nodes should represent thoughts
    And edges should represent actions
    And final answer should be highlighted
    And diagram should be rendered in Streamlit

  Scenario: Mermaid diagram with branches
    Given agent trace with self-correction
    When Mermaid diagram is generated
    Then it should show the branching logic
    And failed path should be visually distinct
    And successful path should lead to answer
    And decision points should be clear

  @plotly-charts
  Scenario: Interactive timeline chart
    Given reasoning trace with timestamps and durations
    When create_timeline_chart() is called
    Then it should create Plotly timeline
    And show start time and duration for each step
    And color code by action type
    And allow hover to see details
    And be interactive (zoom, pan)

  Scenario: Timeline chart performance breakdown
    Given query with total latency 2500ms
    Then timeline should show breakdown:
      | component         | duration | percentage |
      | search_law        | 450ms    | 18%        |
      | LLM reasoning 1   | 1200ms   | 48%        |
      | get_context       | 300ms    | 12%        |
      | LLM reasoning 2   | 550ms    | 22%        |

  @retrieval-metrics
  Scenario: Metrics dashboard display
    Given retrieval metadata from agent response
    When render_retrieval_metrics() is called
    Then it should display 4 metric cards:
      | metric          | example | unit  |
      | Retrieval Mode  | HYBRID  | -     |
      | Documents       | 5       | count |
      | Avg Relevance   | 87%     | %     |
      | Latency         | 450ms   | ms    |

  Scenario: Relevance distribution bar chart
    Given document scores [0.89, 0.85, 0.81, 0.78, 0.75]
    When metrics visualization is rendered
    Then a bar chart should show score distribution
    And bars should be color-coded (green for high, yellow for medium)
    And X-axis should label documents (Doc 1, Doc 2, etc.)
    And Y-axis should show relevance score 0-1

  Scenario: Metrics delta indicators
    Given current relevance of 87%
    And previous query relevance was 70%
    When metrics are displayed
    Then delta should show "+17%" in green
    And indicate improvement
    When current latency is 600ms and previous was 400ms
    Then delta should show "+200ms" in red with inverse coloring

  @token-usage
  Scenario: Token usage visualization
    Given token counts: prompt=1000, completion=500
    When render_token_usage() is called
    Then it should display 3 metrics:
      | metric              | value  |
      | Prompt Tokens       | 1,000  |
      | Completion Tokens   | 500    |
      | Estimated Cost      | $0.000225 |

  Scenario: Token distribution pie chart
    Given prompt_tokens and completion_tokens
    When token visualization is rendered
    Then a pie chart should show distribution
    And prompt section should be labeled with percentage
    And completion section should be labeled with percentage
    And total should equal 100%
    And chart should have donut hole for aesthetics

  Scenario: Cumulative cost tracking
    Given user has made 10 queries in session
    And each query has token usage
    When token usage is displayed
    Then cumulative cost should be shown
    And breakdown by query should be available
    And warning if approaching $1 threshold

  @citation-graph
  Scenario: Citation network visualization
    Given citations: [BGB § 433, BGB § 434, StGB § 263]
    When render_citation_graph() is called
    Then a Mermaid graph should be generated
    And each citation should be a node
    And relationships should be edges
    And law categories should be visually grouped

  Scenario: Citation with related laws
    Given BGB § 433 references § 535 and § 558
    When citation graph is rendered
    Then § 433 should be the central node
    And arrows should point to related sections
    And tooltip should show relationship type
    And clicking node should navigate to that law

  @source-documents
  Scenario: Source document cards
    Given agent retrieved 5 documents
    When sources are displayed
    Then each should be a card with:
      | field       | example                          |
      | Title       | BGB § 433 Kaufvertrag            |
      | Link        | Clickable URL                    |
      | Relevance   | 89% (progress bar)               |
      | Preview     | First 200 chars of content       |
      | Source Type | Vector DB / Web Search           |

  Scenario: Source document expansion
    Given a source document card
    When user clicks "Show Full Content"
    Then the card should expand
    And display complete document text
    And maintain formatting
    And provide copy button

  @performance-indicators
  Scenario: Real-time loading indicators
    Given agent is processing a query
    Then appropriate loading states should show:
      | stage              | indicator                    |
      | Retrieving docs    | "🔍 Searching..."            |
      | Reasoning          | "🤔 Thinking..."             |
      | Generating answer  | "✍️ Formulating answer..."   |

  Scenario: Progress bar for long operations
    Given a complex query taking >5 seconds
    When processing continues
    Then a progress bar should be displayed
    And show percentage completion estimate
    And allow cancellation

  @error-visualization
  Scenario: Error step highlighting
    Given reasoning trace contains an error step
    When visualization is rendered
    Then the error step should be highlighted in red
    And error message should be prominently displayed
    And recovery attempts should be shown

  @export-functionality
  Scenario: Export reasoning trace as JSON
    Given a completed conversation with reasoning
    When user clicks "Export Trace" button
    Then a JSON file should be downloaded
    And contain all reasoning steps
    And include metadata and timestamps
    And be human-readable with formatting

  Scenario: Export conversation as PDF
    Given a conversation history
    When user clicks "Export PDF"
    Then a PDF should be generated
    And include all messages with timestamps
    And include visualizations as images
    And maintain formatting and structure
