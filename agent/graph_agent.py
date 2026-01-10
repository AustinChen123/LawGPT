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
    Tool to retrieve relevant legal articles.
    Accepts a JSON string representing a list of queries (Multi-Query).
    Returns a JSON string of deduplicated results.
    """
    print(f"--- Calling Retriever Tool ---")
    try:
        queries = json.loads(query)
        if not isinstance(queries, list):
            queries = [query]
    except:
        queries = [query]
        
    all_results = {}
    
    for q in queries:
        print(f"  > Searching for: {q}")
        results = retriever.query(query_text=q, top_k=3) # Reduce k per query to avoid noise
        for doc in results:
            # Use link or content hash as unique key
            doc_id = doc.get('metadata', {}).get('link', doc.get('id'))
            if doc_id and doc_id not in all_results:
                all_results[doc_id] = doc
            else:
                # Optional: Reciprocal Rank Fusion could go here.
                # For now, we just keep the first occurrence (highest score usually).
                pass
                
    final_results = list(all_results.values())
    print(f"  > Total unique documents found: {len(final_results)}")
    return json.dumps(final_results)

# 3. Create the LLM
settings = Settings()
llm = GeminiLLMAPI(api_key=settings.GOOGLE_API_KEY, model="gemini-flash-latest")

# 4. Define the nodes

def router_node(state: AgentState):
    """
    Classifies the user's intent using a Hybrid Strategy (Keywords + LLM).
    Bias: High Recall for legal queries (Safety First).
    """
    print("--- Router Node ---")
    messages = state['messages']
    last_message = messages[-1]
    content = last_message.content.lower()
    
    # 1. Hard Rule: Keyword Guardrails
    # If these exist, we force a search to avoid LLM missing obvious legal references.
    legal_keywords = [
        "§", "bgb", "law", "legal", "contract", "agreement", "sue", "court", 
        "judge", "lawyer", "attorney", "recht", "gesetz", "vertrag", "anwalt",
        "paragraf", "article", "regulation", "statute", "rule", "complaint"
    ]
    
    if any(k in content for k in legal_keywords):
        print("--- Intent Detected: legal_query (Keyword Trigger) ---")
        return {"intent": "legal_query"}
    
    # 2. LLM Check (Conservative Classification)
    prompt = (
        f"You are a sophisticated intent classifier for a legal assistant.\n"
        f"Classify the User Query into 'legal_query' or 'general_chat'.\n\n"
        f"**Guidelines:**\n"
        f"- **legal_query**: ANY question about rights, obligations, rules, regulations, crimes, debts, family issues, work disputes, or definitions of terms. \n"
        f"  *CRITICAL*: If you are unsure, or if the query vaguely touches on a real-world conflict (e.g., 'neighbor issue', 'broken item'), classify as 'legal_query'. **Err on the side of searching.**\n"
        f"- **general_chat**: Pure greetings ('hi', 'hello'), thanks, or questions about completely non-legal topics (e.g., 'weather', 'recipe', 'poem').\n\n"
        f"User Query: {last_message.content}\n\n"
        f"Output ONLY the category name."
    )
    
    try:
        intent = llm.generate_response(prompt).strip().lower()
        # Clean up response
        if "legal" in intent:
            intent = "legal_query"
        else:
            intent = "general_chat"
    except:
        # Failsafe: If LLM fails, assume it's a query to be safe
        intent = "legal_query" 
        
    print(f"--- Intent Detected: {intent} (LLM Decision) ---")
    return {"intent": intent}

def tool_decision_node(state: AgentState):
    """
    Analyzes the user's query and generates optimized German search queries.
    Uses Chain-of-Thought (COT) and Multi-Query Expansion.
    """
    print("--- Tool Decision Node (Query Expansion) ---")
    messages = state['messages']
    last_message = messages[-1]
    
    # COT + Multi-Query Prompt
    prompt = (
        f"You are an expert German legal researcher. Your goal is to retrieve the most relevant sections from the BGB (German Civil Code) for the user's query.\n"
        f"User Query: {last_message.content}\n\n"
        f"**Task:**\n"
        f"1. **Analyze**: Briefly think step-by-step about the legal concepts. **Crucial**: If the user uses English legal terms (e.g., 'Holographic Will', 'Tort', 'Damages'), you MUST translate them to their precise German equivalents (e.g., 'Eigenhändiges Testament', 'Unerlaubte Handlung', 'Schadensersatz') for the search.\n"
        f"2. **Generate Queries**: Create 3 distinct search queries in **German**.\n"
        f"   - Query 1: Specific legal keywords or statute numbers (e.g., 'Testament Formvorschriften BGB').\n"
        f"   - Query 2: Natural language description of the legal issue in German.\n"
        f"   - Query 3: Broad conceptual terms or synonyms.\n\n"
        f"**Output Format:**\n"
        f"Provide ONLY a JSON list of strings. Do not output the analysis text, just the JSON.\n"
        f"Example: [\"Query 1\", \"Query 2\", \"Query 3\"]"
    )
    
    try:
        response = llm.generate_response(prompt).strip()
        # Clean up potential markdown code blocks
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
            
        queries = json.loads(response)
        if not isinstance(queries, list):
            raise ValueError("Output is not a list")
    except Exception as e:
        print(f"!! Query Expansion Failed: {e}. Fallback to original query.")
        queries = [last_message.content]

    print(f"--- Generated Queries: {queries} ---")

    # Pass the list of queries as a JSON string to the tool
    tool_call = {
        "name": "retrieve_articles_tool",
        "args": {"query": json.dumps(queries)}, # Passing list as JSON string
        "id": "1",
    }
    return {
        "messages": [AIMessage(content="", tool_calls=[tool_call])]
    }

def reranker_node(state: AgentState):
    """
    Evaluates retrieved documents and filters out irrelevant ones.
    Ensures high-quality context for the generator.
    """
    print("--- Reranker Node ---")
    messages = state['messages']
    # Find tool messages to extract docs
    tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
    
    docs = []
    for msg in tool_messages:
        try:
            d = json.loads(msg.content)
            if isinstance(d, list):
                docs.extend(d)
        except:
            pass
            
    if not docs:
        print("--- No documents to rerank ---")
        return {"documents": []}

    original_question = next(msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage))
    
    # Prompt for LLM-based Reranking/Filtering
    doc_previews = "\n".join([f"ID: {i} | Title: {d['metadata'].get('section_title')} | Content: {d['metadata'].get('content')[:200]}..." for i, d in enumerate(docs)])
    
    prompt = (
        f"You are a legal expert judge. Your task is to evaluate the relevance of the following retrieved BGB sections to the user's question.\n\n"
        f"**User Question:** {original_question}\n\n"
        f"**Retrieved Documents:**\n{doc_previews}\n\n"
        f"**Task:**\n"
        f"1. For each document ID, determine if it is 'RELEVANT' or 'IRRELEVANT' to answering the question.\n"
        f"2. Keep only documents that provide useful legal rules, definitions, or context for this specific case.\n\n"
        f"**Output Format:**\n"
        f"Provide a JSON list of IDs that are RELEVANT. Example: [0, 2]\n"
        f"Output ONLY the JSON list."
    )
    
    try:
        response = llm.generate_response(prompt).strip()
        # Clean JSON
        if "[" in response and "]" in response:
            response = "[" + response.split("[")[1].split("]")[0] + "]"
        
        relevant_ids = json.loads(response)
        filtered_docs = [docs[i] for i in relevant_ids if i < len(docs)]
        print(f"--- Reranker: Kept {len(filtered_docs)} out of {len(docs)} documents ---")
        return {"documents": filtered_docs}
    except Exception as e:
        print(f"!! Reranker failed: {e}. Keeping all docs.")
        return {"documents": docs}

def generation_node(state: AgentState):
    """
    Generates a final answer. 
    Uses the filtered documents from the 'documents' state field.
    """
    print("--- Generation Node ---")
    messages = state['messages']
    intent = state.get('intent', 'general_chat')
    
    # Use the docs from state['documents'] (populated by reranker)
    # instead of re-parsing tool messages
    new_documents = state.get('documents', [])

    # Construct Prompt
    original_question = next(msg.content for msg in reversed(messages) if isinstance(msg, HumanMessage))
    
    if intent == "legal_query":
        if not new_documents:
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
        f"1. Answer the question using ONLY the information above.\n"
        f"2. Cite the source for every claim. **CRITICAL**: You MUST explicitly mention the statute name and section number in your text (e.g., 'According to BGB § 123...' or '...as stated in § 2247 BGB'). Do not rely solely on links.\n"
        f"3. If the provided documents are NOT relevant to the user's question (e.g., a recipe question vs a legal document), "
        f"state clearly that you cannot answer based on the available legal texts. "
        f"Do NOT summarize the irrelevant document and do NOT cite it in this case.\n"
        f"4. Do NOT include a disclaimer at the end. The user interface will handle the legal disclaimer automatically.\n\n"
        f"**Answer (with explicit citations):**"
    )
        )
    else:
        # (General chat logic stays same...)
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
workflow.add_node("tool_decision", tool_decision_node)
workflow.add_node("tool_execution", tool_node)
workflow.add_node("reranker", reranker_node)
workflow.add_node("generator", generation_node)

# Edges
workflow.set_entry_point("router")

workflow.add_conditional_edges(
    "router",
    route_step,
    {
        "tools": "tool_decision",
        "generator": "generator"
    }
)

workflow.add_edge("tool_decision", "tool_execution")
workflow.add_edge("tool_execution", "reranker")
workflow.add_edge("reranker", "generator")

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
