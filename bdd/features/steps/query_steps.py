from behave import given, when, then
from agent.graph_agent import run_agent
import json

@given('the law database contains BGB § 2247 regarding holographic wills')
def step_impl(context):
    # Assumes data is already seeded via 'seed_test_data.py'
    pass

@when('I ask "{question}"')
def step_impl(context, question):
    context.response = run_agent(question)
    context.answer = context.response["answer"]
    context.docs = context.response["documents"]

@then('the agent should retrieve documents related to "{expected_id}"')
def step_impl(context, expected_id):
    # Check metadata 'section_title' for the expected ID (e.g., "§ 2247")
    found = False
    for doc in context.docs:
        meta = doc.get('metadata', {})
        section_title = meta.get('section_title', '')
        # Normalize: remove spaces to handle "§ 2247" vs "§2247"
        if expected_id.replace(" ", "") in section_title.replace(" ", ""):
            found = True
            break
    
    # Debug info
    if not found:
        titles = [d.get('metadata', {}).get('section_title') for d in context.docs]
        print(f"DEBUG: Retrieved Titles: {titles}")

    assert found, f"Expected document with section '{expected_id}' not found in retrieved docs."

@then('the response should mention "{keyword}"')
def step_impl(context, keyword):
    assert keyword.lower() in context.answer.lower(), f"Keyword '{keyword}' not found in agent answer: {context.answer}"

@then('the response should contain a legal citation like "{citation}"')
def step_impl(context, citation):
    # Normalize answer to handle LaTeX output from LLM (e.g., $\S 2247$)
    normalized_answer = context.answer.replace("$\S", "§").replace("\\S", "§")
    assert citation in normalized_answer or citation in context.answer, \
        f"Citation '{citation}' not found in agent answer: {context.answer}"

@then('the response should not contain a legal citation like "{citation}"')
def step_impl(context, citation):
    assert citation not in context.answer, f"Citation '{citation}' SHOULD NOT be in agent answer, but was found: {context.answer}"