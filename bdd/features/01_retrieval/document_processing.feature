@phase1 @retrieval @document-processing
Feature: Document Processing and Chunking
  As a system administrator
  I want documents to be properly chunked and enriched with metadata
  So that retrieval quality is maximized

  Background:
    Given German legal documents in JSON format
    And the RecursiveCharacterTextSplitter is configured

  @critical @smoke
  Scenario: Legal-aware text chunking
    Given a legal document with multiple sections
    When the document is processed with legal separators
    Then chunks should respect section boundaries (§, Art.)
    And no section should be split mid-paragraph
    And each chunk should be between 400-500 tokens
    And overlap should be 100-150 tokens

  @critical
  Scenario: Parent-child document relationships
    Given a long legal section of 3000 tokens
    When parent-child splitting is applied
    Then multiple child chunks of ~400 tokens should be created
    And one parent document of ~2000 tokens should be preserved
    And each child should reference its parent ID
    And parent should contain full context of all children

  Scenario: Metadata extraction from legal documents
    Given a JSON document from gesetze-im-internet.de
    When metadata extraction is performed
    Then the following should be extracted:
      | field          | example                      |
      | main_topic     | Bürgerliches Gesetzbuch      |
      | law_category   | BGB                          |
      | section_title  | § 433 Kaufvertrag            |
      | section_number | 433                          |
      | link           | https://www.gesetze-im...    |
    And all metadata should be validated for completeness

  Scenario: Hierarchical metadata structure
    Given a legal document with nested structure
    When metadata extraction processes the hierarchy
    Then it should capture:
      | level | type              | example           |
      | 1     | Law category      | BGB               |
      | 2     | Book/Part         | Allgemeiner Teil  |
      | 3     | Section           | § 433             |
      | 4     | Paragraph         | Absatz 1          |
    And maintain parent-child relationships in metadata

  @edge-cases
  Scenario: Handling very short sections
    Given a legal section with only 50 tokens
    When chunking is applied
    Then the section should not be split
    And should be treated as a single chunk
    And still include full metadata

  Scenario: Handling very long sections
    Given a legal section with 5000 tokens
    When chunking is applied
    Then it should be split into multiple chunks
    And each chunk should have meaningful boundaries
    And section title should be preserved in each chunk's metadata
    And chunk sequence should be tracked (1/5, 2/5, etc.)

  Scenario: German special character handling
    Given legal text with "Ä Ö Ü ß §"
    When the text is processed
    Then special characters should be preserved in content
    But converted to ASCII in document IDs (ae, oe, ue, ss, #)
    And both forms should be searchable

  @validation
  Scenario: Empty content filtering
    Given a legal section with empty content or only "-"
    When the document is processed
    Then empty sections should be filtered out
    And not added to the vector database
    And a warning should be logged

  Scenario: Duplicate content detection
    Given multiple JSON files contain the same legal section
    When documents are processed
    Then duplicates should be detected by content hash
    And only unique documents should be kept
    And duplicate count should be logged

  Scenario: Link validation and formatting
    Given a legal section with a source URL
    When metadata is extracted
    Then the link should be validated for correct format
    And anchor tags (#p0017) should be preserved
    And broken links should be flagged but not block processing

  @performance
  Scenario: Batch document processing
    Given 1000 legal documents in JSON format
    When batch processing is performed
    Then all documents should be processed
    And processing rate should be at least 50 docs/second
    And memory usage should remain below 2GB
    And progress should be tracked every 100 documents

  Scenario: Resume capability for interrupted processing
    Given document processing is interrupted at document 500
    When processing is restarted
    Then it should resume from document 501
    And not reprocess already completed documents
    And progress.json should be updated incrementally

  @embedding
  Scenario: Embedding generation with rate limiting
    Given 1000 document chunks to embed
    And Gemini API rate limit of 1500 RPM
    When embeddings are generated
    Then requests should be throttled to stay under limit
    And actual rate should be ~1450 RPM (safety margin)
    And no API errors should occur due to rate limiting

  Scenario: Embedding retry on failure
    Given an embedding request fails with timeout
    When the retry logic is triggered
    Then it should retry with exponential backoff
    And maximum of 3 retry attempts
    And if all retries fail, skip the document and log error
    And continue processing remaining documents

  @quality
  Scenario: Chunk quality validation
    Given a processed document chunk
    When quality checks are performed
    Then chunk should contain at least 50 tokens
    And should not end mid-word
    And should have valid UTF-8 encoding
    And should include all required metadata fields

  Scenario: Semantic boundary preservation
    Given a legal section discussing multiple topics
    When chunking is performed
    Then chunks should maintain semantic coherence
    And topic shifts should occur at chunk boundaries
    And each chunk should be independently understandable

  @data-integrity
  Scenario: Source document traceability
    Given any document chunk in the vector database
    When tracing back to source
    Then the original JSON file should be identifiable
    And the exact section should be locatable
    And the processing timestamp should be recorded
    And version information should be preserved
