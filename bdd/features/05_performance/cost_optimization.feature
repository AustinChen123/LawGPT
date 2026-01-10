@phase4 @performance @cost
Feature: Cost Optimization and Budget Management
  As a system administrator
  I want to optimize API costs
  So that the system remains economically viable

  Background:
    Given the system tracks API usage and costs
    And budget thresholds are configured

  @cost-tracking
  Scenario: Real-time cost calculation
    Given a query is processed
    When token usage is recorded
    Then cost should be calculated:
      | API            | pricing              | calculation              |
      | Gemini Embed   | $0.00001/1K tokens   | tokens * 0.00001 / 1000 |
      | Gemini LLM     | $0.075/1M prompt     | prompt * 0.075 / 1M     |
      | Gemini LLM     | $0.30/1M completion  | completion * 0.30 / 1M  |
      | Pinecone       | $70/month fixed      | Amortized per query     |
    And total cost per query should be tracked

  Scenario: Cost breakdown by component
    Given 1000 queries processed in a day
    When daily cost report is generated
    Then it should show breakdown:
      | component     | cost    | percentage |
      | Embeddings    | $0.50   | 5%         |
      | LLM calls     | $8.00   | 80%        |
      | Pinecone      | $2.33   | 15%        |
      | Total         | $10.83  | 100%       |

  @budget-alerts
  Scenario: Daily budget threshold warning
    Given daily budget is $20
    When costs reach $16 (80%)
    Then warning alert should be sent
    And dashboard should show warning
    And administrators should be notified
    And system should continue operating

  Scenario: Daily budget hard limit
    Given daily budget hard limit is $25
    When costs reach $25
    Then system should switch to cost-saving mode:
      | action                     | effect                    |
      | Prefer vector DB           | No web search API calls   |
      | Increase cache TTL         | Reuse results longer      |
      | Reduce top_k               | Fewer documents retrieved |
      | Limit max_iterations       | Shorter agent reasoning   |
    And inform users of degraded service

  @cost-optimization
  Scenario: Intelligent caching strategy
    Given cache is enabled
    When identical query appears within 1 hour
    Then cached result should be used
    And save:
      | cost component | savings  |
      | Embedding      | 100%     |
      | Retrieval      | 100%     |
      | LLM            | 100%     |
      | Total          | $0.0025  |

  Scenario: Query similarity caching
    Given query "BGB § 433 Kaufvertrag"
    And cached query "What is BGB § 433?"
    When semantic similarity > 0.95
    Then similar cached result should be offered
    And user can choose to use it (free)
    Or request fresh search (normal cost)

  Scenario: Batch processing for efficiency
    Given 10 documents need embedding
    When batch API is available
    Then documents should be batched
    And processed in single API call
    And save overhead costs

  @retrieval-mode-costs
  Scenario: Vector DB mode cost profile
    Given vector-only retrieval mode
    Then cost per query should be:
      | component     | cost       | notes                    |
      | Embedding     | $0.000008  | 1 query embedding        |
      | Pinecone      | $0.002     | Amortized fixed cost     |
      | LLM           | $0.0002    | Answer generation        |
      | Total         | ~$0.002    | Predictable, low-cost    |

  Scenario: Web search mode cost profile
    Given web-only retrieval mode
    Then cost per query should be:
      | component     | cost       | notes                    |
      | Web API       | $0         | DuckDuckGo free          |
      | LLM (extract) | $0.0003    | HTML processing          |
      | LLM (answer)  | $0.0002    | Answer generation        |
      | Total         | ~$0.0005   | Very low cost            |

  Scenario: Hybrid mode cost optimization
    Given hybrid retrieval mode
    When query is processed
    Then cost should be optimized:
      | scenario           | strategy                      | cost    |
      | Specific law (§)   | Vector only                   | $0.002  |
      | Recent update      | Web only                      | $0.0005 |
      | Complex research   | Hybrid (both)                 | $0.0025 |
    And adaptive mode minimizes unnecessary calls

  @token-optimization
  Scenario: Prompt compression
    Given a long retrieval context (3000 tokens)
    When generating answer
    Then system should compress context:
      | technique                | savings    |
      | Remove duplicates        | 10%        |
      | Truncate low-relevance   | 20%        |
      | Summarize verbose parts  | 15%        |
      | Total reduction          | 40%        |
    And maintain answer quality

  Scenario: Smart context window usage
    Given context window limit of 8000 tokens
    When multiple documents are retrieved
    Then system should prioritize:
      | priority | content              | tokens |
      | 1        | Highest relevance    | 2000   |
      | 2        | Medium relevance     | 1500   |
      | 3        | User query + history | 1000   |
      | 4        | System instructions  | 500    |
    And stay within limits without truncating critical info

  @free-tier-optimization
  Scenario: Operating on free tier only
    Given no paid API keys configured
    When system uses free resources:
      | resource            | cost    | limits              |
      | DuckDuckGo          | $0      | Reasonable usage    |
      | Local cache         | $0      | Memory limited      |
    Then cost per query should be $0
    And system should still function
    And users should be informed of limitations

  Scenario: Freemium model suggestion
    Given a user on free tier (web search only)
    And has made 50 queries
    When query patterns show high usage
    Then system should suggest upgrade:
      | benefit                | value                  |
      | Faster responses       | 3x speed improvement   |
      | Better accuracy        | +15% retrieval quality |
      | No rate limits         | Unlimited queries      |
      | Estimated cost         | $10-20/month           |

  @cost-monitoring
  Scenario: Monthly cost projection
    Given current usage rate
    When projection is calculated
    Then it should estimate:
      | metric              | value        |
      | Queries/day         | 500          |
      | Cost/day            | $15          |
      | Projected monthly   | $450         |
      | Budget status       | 90% of $500  |
    And warn if projection exceeds budget

  Scenario: Cost anomaly detection
    Given baseline cost is $10-15/day
    When cost suddenly spikes to $50/day
    Then anomaly alert should trigger
    And investigate causes:
      | possible cause       | action                    |
      | Abuse/bot traffic    | Enable rate limiting      |
      | Bug (infinite loop)  | Investigate code          |
      | Legitimate spike     | Increase budget           |

  @roi-tracking
  Scenario: Cost per successful query
    Given 1000 queries in a day
    And 980 successful (2% errors)
    And total cost $15
    When ROI is calculated
    Then cost per successful query = $15 / 980 = $0.0153
    And this should be tracked over time
    And optimization efforts should reduce this

  Scenario: Feature cost analysis
    Given different features:
      | feature               | queries/day | cost/day |
      | Basic Q&A             | 400         | $8       |
      | Multi-turn            | 100         | $3       |
      | Citation extraction   | 80          | $1.50    |
      | Translation           | 20          | $0.50    |
    Then cost-effectiveness of each should be evaluated
    And resource allocation adjusted accordingly
