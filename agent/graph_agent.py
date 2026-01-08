import operator
import json
from typing import Annotated, Sequence, TypedDict, Literal

from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

from config.settings import Settings
from rag.gemini_api import GeminiLLMAPI
from rag.retriever import Retriever


# 1. Define the state for the graph
class AgentState(TypedDict):
    """
    Represents the state of our agent.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    documents: Annotated[list[dict], operator.add]
    intent: str # 'legal_query' or 'general_chat'

# 2. Define the tools
retriever = Retriever()

def retrieve_articles_tool(query: str, filters: dict = None) -> str:
    """
    Tool to retrieve relevant legal articles from the vector database.
    Returns a JSON string of the results.
    """
    print(f"--- Calling Retriever Tool with query: {query} ---")
    results = retriever.query(query_text=query, top_k=5)
    return json.dumps(results)

# 3. Create the LLM
settings = Settings()
llm = GeminiLLMAPI(api_key=settings.GOOGLE_API_KEY, model="gemini-flash-latest")

# 4. Define the nodes

def router_node(state: AgentState):
    """
    Classifies the user's intent to decide whether to use tools or answer directly.
    """
    print("--- Router Node ---")
    messages = state['messages']
    last_message = messages[-1]
    
    # Simple prompt-based classification
    # In a production system, this could be a specialized smaller model or a fine-tuned classifier.
    prompt = (
        f"Classify the following user query into one of two categories:\n"
        f"1. 'legal_query': The user is asking about laws, regulations, legal definitions, or legal advice (especially German law).\n"
        f"2. 'general_chat': The user is greeting, asking about general knowledge (e.g., cooking, weather), or making small talk.\n\n"
        f"User Query: {last_message.content}\n\n"
        f"Output ONLY the category name ('legal_query' or 'general_chat')."
    )
    
    try:
        intent = llm.generate_response(prompt).strip().lower()
        # Fallback if model outputs extra text
        if "legal" in intent:
            intent = "legal_query"
        else:
            intent = "general_chat"
    except:
        intent = "legal_query" # Default to legal query on error
        
    print(f"--- Intent Detected: {intent} ---")
    return {"intent": intent}

def tool_decision_node(state: AgentState):
    """
    If intent is legal_query, constructs the tool call.
    """
    print("--- Tool Decision Node ---")
    messages = state['messages']
    last_message = messages[-1]
    
    # We construct the tool call manually for the retriever
    tool_call = {
        "name": "retrieve_articles_tool",
        "args": {"query": last_message.content},
        "id": "1",
    }
    return {
        "messages": [AIMessage(content="", tool_calls=[tool_call])]
    }

def generation_node(state: AgentState):
    """
    Generates a final answer. 
    It handles both cases: with retrieved docs (legal) or without (general).
    """
    print("--- Generation Node ---")
    messages = state['messages']
    intent = state.get('intent', 'general_chat')
    
    # Find tool messages to extract docs
    tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
    
    new_documents = []
    for msg in tool_messages:
        try:
            docs = json.loads(msg.content)
            if isinstance(docs, list):
                new_documents.extend(docs)
        except:
            pass

    # Construct Prompt
    original_question = next(msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage))
    
    if intent == "legal_query":
        if not new_documents:
            # Fallback if retrieval returned nothing
            document_str = "No specific legal documents found."
        else:
            document_str = "\n\n".join(
                [f"Citation: {doc['metadata'].get('link', 'N/A')}\nContent: {doc['metadata'].get('content', 'N/A')}" for doc in new_documents]
            )

        prompt = (
            f"You are a legal assistant. Answer based *only* on the provided documents.\n\n"
            f"**User Question:**\n{original_question}\n\n"
            f"**Legal Documents:**\n{document_str}\n\n"
            f"**Instructions:**\n"
            f"1. Answer using ONLY the information above.\n"
            f"2. Cite the source for every claim.\n"
            f"3. If documents are irrelevant/empty, state you cannot answer based on available texts.\n"
            f"4. Do NOT include a disclaimer.\n\n"
            f"**Answer:**"
        )
    else:
        # General Chat Prompt
        prompt = (
            f"You are LawGPT, a helpful assistant. The user is engaging in general conversation.\n"
            f"**User Input:** {original_question}\n\n"
            f"**Instructions:**\n"
            f"1. Respond politely and helpfully.\n"
            f"2. If the user asks for legal advice, kindly remind them you specialize in German Law and they should ask a specific legal question.\n"
            f"3. Do NOT invent legal advice.\n"
            f"4. Do NOT include a disclaimer.\n\n"
            f"**Response:**"
        )

    try:
        response_text = llm.generate_response(prompt)
        return {"messages": [AIMessage(content=response_text)]}
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(f"!! {error_msg}")
        return {"messages": [AIMessage(content="System Error: Rate limit or API issue.")]}

# 5. Define Conditional Logic
def route_step(state: AgentState) -> Literal["tools", "generator"]:
    if state["intent"] == "legal_query":
        return "tools"
    return "generator"

# 6. Create the graph
tool_node = ToolNode([retrieve_articles_tool])

workflow = StateGraph(AgentState)

# Nodes
workflow.add_node("router", router_node)
workflow.add_node("tool_decision", tool_decision_node) # Creates the tool call message
workflow.add_node("tool_execution", tool_node) # Actually executes the tool
workflow.add_node("generator", generation_node)

# Edges
workflow.set_entry_point("router")

# Router decides: Go to Tool Decision (Legal) or Direct Generation (General)
workflow.add_conditional_edges(
    "router",
    route_step,
    {
        "tools": "tool_decision",
        "generator": "generator"
    }
)

# Legal Path: Decision -> Execution -> Generator
workflow.add_edge("tool_decision", "tool_execution")
workflow.add_edge("tool_execution", "generator")

# General Path: Router -> Generator (Implicit in conditional edge)

workflow.add_edge("generator", END)

# Compile
app = workflow.compile()

def run_agent(question: str) -> dict:
    """Helper for BDD tests"""
    initial_state = {
        "messages": [HumanMessage(content=question)],
        "documents": [],
        "intent": ""
    }
    final_state = app.invoke(initial_state)
    
    retrieved_docs = []
    for msg in final_state['messages']:
        if isinstance(msg, ToolMessage):
            try:
                docs = json.loads(msg.content)
                if isinstance(docs, list):
                    retrieved_docs.extend(docs)
            except:
                pass
                
    return {
        "answer": final_state['messages'][-1].content,
        "documents": retrieved_docs
    }

def main():
    print("Agentic RAG system starting...")
    res = run_agent("Hello, who are you?")
    print(f"Q: Hello\nA: {res['answer']}")
    print("-" * 20)
    res = run_agent("What is BGB § 2247?")
    print(f"Q: BGB 2247\nA: {res['answer']}")

if __name__ == "__main__":
    main()
