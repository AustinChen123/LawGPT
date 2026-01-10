@phase4 @performance @quality
Feature: Performance and Quality Requirements
  As a system operator
  I want the system to meet performance and quality standards
  So that users have a reliable experience

  Background:
    Given the system is deployed in production
    And monitoring is active

  @critical @latency
  Scenario: Query latency targets
    Given a typical legal question
    When processed through the system
    Then latency should meet targets:
      | component         | target   | max acceptable |
      | Vector retrieval  | < 100ms  | 500ms          |
      | Web retrieval     | < 1000ms | 3000ms         |
      | LLM inference     | < 2000ms | 5000ms         |
      | Total end-to-end  | < 3000ms | 10000ms        |
    And 95th percentile should be under max acceptable

  Scenario: Retrieval latency by mode
    Given retrieval performance benchmarks
    Then average latencies should be:
      | mode     | avg latency | p95 latency | p99 latency |
      | vector   | 150ms       | 300ms       | 500ms       |
      | web      | 1500ms      | 2500ms      | 4000ms      |
      | hybrid   | 1800ms      | 3000ms      | 5000ms      |

  @throughput
  Scenario: Concurrent query handling
    Given 100 concurrent users
    When all submit queries simultaneously
    Then system should handle at least 50 queries/second
    And no more than 5% should timeout
    And average latency should remain under 5 seconds
    And no query should wait more than 30 seconds

  Scenario: Sustained load performance
    Given 1000 queries per hour for 24 hours
    When load is sustained
    Then system should maintain stable performance
    And no memory leaks should occur
    And latency should not degrade over time
    And error rate should remain below 1%

  @retrieval-quality
  Scenario: Vector retrieval accuracy
    Given a test set of 100 legal queries with known relevant documents
    When vector retrieval is performed
    Then accuracy should meet:
      | metric       | target | minimum acceptable |
      | Precision@5  | 90%    | 80%                |
      | Recall@10    | 85%    | 75%                |
      | MRR          | 0.90   | 0.80               |
    And top result should be relevant 90% of the time

  Scenario: Hybrid retrieval improvement
    Given the same test set
    When comparing vector-only vs hybrid retrieval
    Then hybrid should improve:
      | metric       | improvement |
      | Precision@5  | +5-10%      |
      | Recall@10    | +10-15%     |
      | Coverage     | +20%        |
    And handle edge cases better

  @answer-quality
  Scenario: Answer relevance scoring
    Given 50 test queries with gold standard answers
    When agent generates answers
    Then answer quality should achieve:
      | metric              | target | minimum |
      | Semantic similarity | 0.85   | 0.75    |
      | Citation accuracy   | 95%    | 90%     |
      | Factual correctness | 98%    | 95%     |
      | Completeness        | 90%    | 80%     |

  Scenario: Citation accuracy validation
    Given answers mentioning law references
    When citations are validated
    Then at least 95% should be correct
    And law references should be real (not hallucinated)
    And links should navigate to correct sections
    And no more than 2% should be broken links

  Scenario: Hallucination rate
    Given queries where relevant documents don't exist
    When agent generates answers
    Then hallucination rate should be below 2%
    And agent should admit uncertainty in 90%+ cases
    And not invent legal information

  @cost-efficiency
  Scenario: Token usage optimization
    Given 1000 queries processed
    When token usage is analyzed
    Then average tokens per query should be:
      | component      | target   | max acceptable |
      | Prompt tokens  | < 2000   | 4000           |
      | Completion     | < 500    | 1000           |
      | Total          | < 2500   | 5000           |
    And cost per query should be under $0.001

  Scenario: API call optimization
    Given a typical query workflow
    When API calls are counted
    Then it should minimize calls:
      | API               | target calls | reason                |
      | Embedding         | 1            | Query embedding only  |
      | Vector DB         | 1            | Single search         |
      | LLM inference     | 2-3          | Agent reasoning steps |
      | Web search (opt)  | 0-1          | Only if needed        |

  @reliability
  Scenario: System uptime
    Given production monitoring
    When tracked over 30 days
    Then system should achieve:
      | metric            | target |
      | Uptime            | 99.5%  |
      | Error rate        | < 0.5% |
      | Timeout rate      | < 1%   |
      | Success rate      | > 98%  |

  Scenario: Graceful degradation
    Given various failure scenarios:
      | failure           | expected behavior                |
      | Vector DB down    | Fallback to web search           |
      | Web search fails  | Use vector DB only               |
      | LLM timeout       | Retry with exponential backoff   |
      | Rate limit hit    | Queue request, inform user       |
    Then system should handle each gracefully
    And maintain partial functionality
    And inform user of degraded service

  @scalability
  Scenario: Horizontal scaling
    Given traffic increases 10x
    When additional server instances are added
    Then load should distribute evenly
    And performance should remain consistent
    And no single point of failure should exist

  Scenario: Database scalability
    Given vector database contains 1M documents
    When queries are executed
    Then retrieval latency should remain under 200ms
    And accuracy should not degrade
    And memory usage should be efficient

  @resource-usage
  Scenario: Memory consumption
    Given the system is running
    When processing typical workload
    Then memory usage should be:
      | component      | target  | max acceptable |
      | Agent process  | < 500MB | 1GB            |
      | Cache          | < 200MB | 500MB          |
      | Total          | < 1GB   | 2GB            |
    And no memory leaks over 24 hours

  Scenario: CPU utilization
    Given 10 concurrent queries
    When being processed
    Then CPU usage should be:
      | scenario        | avg CPU | peak CPU |
      | Idle            | < 5%    | -        |
      | Light load      | < 30%   | 50%      |
      | Normal load     | < 60%   | 80%      |
      | Peak load       | < 80%   | 95%      |

  @monitoring
  Scenario: Health check endpoint
    Given /health endpoint exists
    When polled every 30 seconds
    Then it should return status within 100ms
    And indicate component health:
      | component       | status   |
      | Vector DB       | healthy  |
      | LLM API         | healthy  |
      | Cache           | healthy  |
      | Overall         | healthy  |

  Scenario: Performance metrics tracking
    Given monitoring system
    When metrics are collected
    Then the following should be tracked:
      | metric                  | granularity |
      | Query latency (p50/p95) | Per minute  |
      | Error rate              | Per minute  |
      | Token usage             | Per hour    |
      | Cache hit rate          | Per hour    |
      | Retrieval accuracy      | Daily       |
      | Cost per query          | Daily       |

  @security-performance
  Scenario: Rate limiting
    Given rate limit of 100 queries per user per hour
    When a user exceeds the limit
    Then requests should be throttled
    And 429 Too Many Requests should be returned
    And not impact other users
    And reset after 1 hour

  Scenario: DDoS protection
    Given 10000 requests from single IP in 1 minute
    When attack is detected
    Then requests should be blocked
    And legitimate users should not be affected
    And incident should be logged
    And admin should be notified

  @quality-gates
  Scenario: Pre-deployment validation
    Given new code is ready for deployment
    When quality gates are checked
    Then all must pass:
      | gate                     | requirement         |
      | Unit tests               | 100% pass           |
      | Integration tests        | 100% pass           |
      | Performance regression   | < 10% latency increase|
      | Retrieval accuracy       | No regression       |
      | Security scan            | No critical issues  |
