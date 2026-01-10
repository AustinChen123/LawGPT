Feature: Legal Information Retrieval and Answering
    As a user interested in German law
    I want to ask questions about specific legal requirements
    So that I can receive grounded answers with citations

    @smoke @retrieval
    Scenario: Validating requirements for a holographic will
        Given the law database contains BGB § 2247 regarding holographic wills
        When I ask "What are the requirements for a valid will in Germany?"
        Then the agent should retrieve documents related to "§ 2247"
        And the response should mention "handwritten"
        And the response should contain a legal citation like "§ 2247"

    @reasoning
    Scenario: Asking for legal definitions based on context
        Given the law database contains BGB § 2247 regarding holographic wills
        When I ask "Does a holographic will need to be typed?"
        Then the response should mention "handwritten"
        And the response should mention "signed"
        And the response should contain a legal citation like "§ 2247"

    @guardrails
    Scenario: Handling out-of-scope questions
        When I ask "What is the best recipe for German potato salad?"
        Then the response should mention "legal"
        And the response should not contain a legal citation like "§"