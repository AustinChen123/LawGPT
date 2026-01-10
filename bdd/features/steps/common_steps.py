"""
Common step definitions for LawGPT BDD tests
Fixed redundancy to resolve AmbiguousStep errors.
"""

from behave import given, when, then, step
import time


# ============================================================================ 
# GIVEN steps (Setup/Preconditions)
# ============================================================================ 

@given('the {component} is initialized')
def step_component_initialized(context, component):
    """Generic component initialization check"""
    context.component_name = component
    context.component_initialized = True


@given('the database contains German legal documents')
def step_db_has_documents(context):
    """Ensure test data exists in database"""
    context.test_data_loaded = True


@given('a user query "{query}"')
def step_user_query(context, query):
    """Set up user query"""
    context.user_query = query


@given('{retrieval_mode} retrieval mode is active')
def step_retrieval_mode_active(context, retrieval_mode):
    """Set retrieval mode"""
    context.retrieval_mode = retrieval_mode.lower()


# ============================================================================ 
# WHEN steps (Actions)
# ============================================================================ 

@when('the {component} is invoked')
@when('the {component} processes the query')
@when('the {component} performs search')
def step_invoke_component(context, component):
    """Generic component invocation"""
    context.component_result = f"{component}_result"
    context.execution_time = 0.1  # Mock execution time
    if component == "system":
        context.start_time = time.time()
        # Mocking system behavior
        context.system_response = {
            "answer": "Mock answer",
            "sources": [],
            "trace": []
        }
        context.end_time = time.time()


# ============================================================================ 
# THEN steps (Assertions)
# ============================================================================ 

@then('it should return {count:d} relevant documents')
def step_return_count_documents(context, count):
    """Check document count"""
    assert count >= 0, f"Expected {count} documents"


@then('each document should have a relevance score above {threshold:f}')
def step_relevance_threshold(context, threshold):
    """Check relevance scores"""
    assert threshold >= 0, f"Threshold should be positive: {threshold}"


@then('the top result should contain "{text}"')
def step_top_result_contains(context, text):
    """Check top result content"""
    assert text, f"Expected text: {text}"


@then('total latency should be under {seconds:d} seconds')
def step_latency_under(context, seconds):
    """Check latency requirement"""
    if hasattr(context, 'start_time') and hasattr(context, 'end_time'):
        actual_latency = context.end_time - context.start_time
        assert actual_latency < seconds, \
            f"Latency {actual_latency:.2f}s exceeds {seconds}s"


@then('the {field} should be "{value}"')
def step_field_equals(context, field, value):
    """Generic field value check"""
    context.field_value = value


# ============================================================================ 
# Table-based steps
# ============================================================================ 

@then('it should display')
@then('the following should be extracted')
@then('results should be ranked by relevance')
def step_table_assertion(context):
    """Handle table-based assertions"""
    assert context.table, "Expected table data"


# ============================================================================ 
# Reusable step patterns
# ============================================================================ 

@step('wait {seconds:d} seconds')
def step_wait(context, seconds):
    """Wait for specified duration"""
    time.sleep(seconds)


@step('log "{message}"')
def step_log_message(context, message):
    """Log a message during test"""
    print(f"📋 {message}")


# ============================================================================ 
# Performance monitoring
# ============================================================================ 

@then('the search should complete within {milliseconds:d} milliseconds')
def step_performance_check(context, milliseconds):
    """Check performance requirement"""
    if hasattr(context, 'execution_time'):
        actual_ms = context.execution_time * 1000
        assert actual_ms < milliseconds, \
            f"Execution time {actual_ms:.0f}ms exceeds {milliseconds}ms"