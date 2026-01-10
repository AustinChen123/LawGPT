@phase3 @ui @streamlit
Feature: Streamlit User Interface
  As a user
  I want an intuitive web interface
  So that I can easily interact with the legal advisor agent

  Background:
    Given the Streamlit application is running
    And main_streamlit_v2.py is loaded
    And the agent is initialized

  @critical @smoke
  Scenario: Basic UI layout and navigation
    Given a user opens the application
    Then the page title should be "LawGPT - AI Legal Advisor"
    And the sidebar should be visible
    And the main chat area should be displayed
    And the interface should be responsive

  @critical
  Scenario: Sidebar configuration options
    Given the sidebar is open
    Then it should display:
      | section              | options                              |
      | Retrieval Mode       | auto, vector, web, hybrid            |
      | Language             | en, de, zh, zh-tw                    |
      | Visualization        | Show reasoning, metrics, tokens      |
      | Advanced Settings    | Top-K, Temperature, Max iterations   |
      | API Keys             | Google API Key, Pinecone API Key     |

  Scenario: Retrieval mode selector
    Given the retrieval mode dropdown
    When the user selects "hybrid"
    Then the agent should use hybrid retrieval
    And a tooltip should explain the mode
    And the selection should persist in session

  Scenario: Language selector
    Given the language dropdown
    When the user selects "zh-tw"
    Then answers should be in Traditional Chinese
    And the flag emoji "🇹🇼" should be displayed
    And the selection should be remembered

  @chat-interface
  Scenario: User sends a message
    Given the chat input field
    When the user types "What is BGB § 433?" and hits enter
    Then the message should appear in chat history
    And a loading spinner should show
    And the agent should process the query
    And the response should appear below

  Scenario: Chat history display
    Given multiple messages have been exchanged
    Then all messages should be visible in chronological order
    And user messages should be right-aligned
    And assistant messages should be left-aligned
    And each message should have a timestamp

  Scenario: Clear chat history
    Given the chat contains multiple messages
    When the user clicks "Clear History" button
    Then all messages should be removed
    And session state should be reset
    And memory should be cleared
    And a fresh conversation should start

  @visualization-toggles
  Scenario: Toggle reasoning visualization
    Given "Show Agent Reasoning" is checked
    And the agent processes a query
    Then reasoning steps should be displayed
    And user can expand/collapse each step
    When "Show Agent Reasoning" is unchecked
    And another query is processed
    Then reasoning should not be displayed

  Scenario: Toggle retrieval metrics
    Given "Show Retrieval Metrics" is checked
    And the agent processes a query
    Then metrics dashboard should appear
    And display relevance scores, latency, document count
    When unchecked, metrics should be hidden

  Scenario: Toggle token usage
    Given "Show Token Usage" is checked
    And the agent completes a query
    Then token statistics should be displayed
    And cost estimation should be shown
    When unchecked, token info should be hidden

  @error-handling
  Scenario: Missing API key warning
    Given no Google API key is configured
    When the user tries to send a message
    Then an error message should appear
    And prompt to enter API key in sidebar
    And not attempt to call the API

  Scenario: Network error display
    Given the agent encounters network error
    When processing a query
    Then a friendly error message should display
    And suggest checking internet connection
    And offer to retry the query
    And not crash the interface

  Scenario: Timeout handling
    Given a query takes longer than 30 seconds
    When timeout occurs
    Then show "Processing is taking longer than expected"
    And offer cancel option
    And allow user to continue waiting or abort

  @session-management
  Scenario: Session state persistence
    Given the user has configured settings
    And had a conversation
    When the page is refreshed
    Then configuration should be restored
    But conversation history should be cleared
    And a fresh session should start

  Scenario: Multiple browser tabs
    Given the user opens the app in two tabs
    When both tabs send queries
    Then each tab should have independent session
    And not interfere with each other
    And maintain separate conversation histories

  @accessibility
  Scenario: Keyboard navigation
    Given the application is loaded
    When the user navigates using Tab key
    Then all interactive elements should be reachable
    And focus indicators should be visible
    And Enter key should submit chat input

  Scenario: Screen reader compatibility
    Given a screen reader is active
    When the user navigates the interface
    Then all elements should have proper ARIA labels
    And chat messages should be announced
    And buttons should be clearly labeled

  @responsive-design
  Scenario: Mobile viewport
    Given the application on mobile device
    Then the sidebar should collapse to hamburger menu
    And chat input should remain accessible
    And text should be readable without zooming
    And buttons should be touch-friendly (min 44px)

  Scenario: Desktop viewport
    Given the application on desktop
    Then the sidebar should be always visible
    And layout should use available width efficiently
    And font sizes should be appropriate (16px base)

  @advanced-settings
  Scenario: Adjust Top-K slider
    Given the advanced settings panel
    When the user moves Top-K slider to 8
    Then the agent should retrieve 8 documents
    And the change should take effect immediately
    And a tooltip should explain what Top-K means

  Scenario: Adjust temperature slider
    Given the temperature slider set to 0.1
    When the user changes it to 0.5
    Then the agent should use higher temperature
    And responses should be more creative
    And a warning should show if set too high (>0.7)

  Scenario: Adjust max iterations
    Given max iterations slider
    When set to 3
    Then the agent should stop after 3 reasoning steps
    And complex queries might not complete
    And a warning should inform about this trade-off
