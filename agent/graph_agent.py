import operator
import json
from typing import Annotated, Sequence, TypedDict

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

    Attributes:
        messages: The history of messages in the conversation.
        documents: A list of retrieved documents.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    documents: Annotated[list[dict], operator.add]

# 2. Define the tools
# We'll start with just the retriever tool.
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
def agent_node(state):
    """
    The primary node that decides what to do. It can either call a tool or respond to the user.
    """
    print("--- Agent Node ---")
    messages = state['messages']
    last_message = messages[-1]
    
    # This is a simplified agent. We are manually creating the tool call.
    # A real agent would use an LLM with tool-calling capabilities to generate this.
    
    # We only want to trigger the tool if it hasn't been called yet.
    # Check if the last message is from Human.
    if isinstance(last_message, HumanMessage):
        tool_call = {
            "name": "retrieve_articles_tool",
            "args": {"query": last_message.content},
            "id": "1", # A unique ID for the tool call
        }
        return {
            "messages": [
                AIMessage(content="", tool_calls=[tool_call])
            ]
        }
    
    # If we are here, it means we probably have tool outputs or other things.
    # But in this simple graph, we go Agent -> Tools -> Generator.
    # So Agent only needs to output the tool call.
    return {"messages": []}

def generation_node(state):
    """
    Generates a final answer to the user based on the retrieved documents.
    """
    print("--- Generation Node ---")
    messages = state['messages']
    
    # Find tool messages
    tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
    
    new_documents = []
    for msg in tool_messages:
        try:
            # content is a JSON string
            docs = json.loads(msg.content)
            if isinstance(docs, list):
                new_documents.extend(docs)
        except:
            pass

    # Construct a prompt for the generation model
    # Find the original human question
    original_question = next(msg.content for msg in messages if isinstance(msg, HumanMessage))
    
    document_str = "\n\n".join(
        [f"Citation: {doc['metadata'].get('link', 'N/A')}\nContent: {doc['metadata'].get('content', 'N/A')}" for doc in new_documents]
    )

    prompt = (
        f"You are a legal assistant. Your task is to answer the user's question based *only* on the provided legal documents. "
        f"For every statement you make, you MUST cite the source document.\n\n"
        f"**User Question:**\n{original_question}\n\n"
        f"**Legal Documents:**\n{document_str}\n\n"
        f"**Answer (with citations):**"
    )

    try:
        response_text = llm.generate_response(prompt)
        return {"messages": [AIMessage(content=response_text)]}
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(f"!! {error_msg}")
        return {"messages": [AIMessage(content="I apologize, but I encountered an error while communicating with the AI model (likely due to rate limits). Please try again later.")]}

# 5. Create the graph
# The tool node is created using a langgraph helper.
tool_node = ToolNode([retrieve_articles_tool])

workflow = StateGraph(AgentState)

# Add the nodes
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
workflow.add_node("generator", generation_node)

# Define the edges
workflow.set_entry_point("agent")
workflow.add_edge("agent", "tools")
workflow.add_edge("tools", "generator") # For now, we go directly to generation
workflow.add_edge("generator", END)

# Compile the graph
app = workflow.compile()

def main():
    """
    Entry point for running the agent.
    """
    print("Agentic RAG system starting...")

    # Define the initial state for the conversation
    initial_state = {
        "messages": [HumanMessage(content="What are the requirements for a valid will in Germany?")],
        "documents": []
    }

    # Run the graph
    final_state = app.invoke(initial_state)

    # Print the final response
    print("\n--- Final Response ---")
    print(final_state['messages'][-1].content)

if __name__ == "__main__":
    main()