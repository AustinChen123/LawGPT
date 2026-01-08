import streamlit as st
import os
import uuid
import json
from config.settings import Settings
from rag.gemini_api import GeminiLLMAPI
from rag.retriever import Retriever
from PIL import Image
from agent.graph_agent import app # Import the compiled LangGraph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from utils.storage import load_sessions, save_sessions

# Disclaimer Dictionary
DISCLAIMERS = {
    "en": "Disclaimer: This AI assistant provides information for educational purposes only and does not constitute legal advice. Please consult a qualified lawyer for specific legal issues.",
    "de": "Haftungsausschluss: Dieser KI-Assistent dient nur zu Informationszwecken und stellt keine Rechtsberatung dar. Bitte konsultieren Sie bei konkreten Rechtsfragen einen qualifizierten Anwalt.",
    "zh-tw": "免責聲明：本 AI 助手僅供參考，不構成法律建議。如有具體法律問題，請諮詢合格律師。"
}

# Page Config
st.set_page_config(page_title="LawGPT - Agentic Legal Assistant", page_icon="⚖️", layout="wide")

def init_session():
    """Initialize session state for chat history"""
    if "sessions" not in st.session_state:
        # Try loading from disk
        loaded = load_sessions()
        if loaded:
            st.session_state.sessions = loaded
            # Default to the first session key found
            st.session_state.current_session_id = list(loaded.keys())[0]
        else:
            # Default initialization
            initial_id = str(uuid.uuid4())
            st.session_state.sessions = {
                initial_id: {
                    "title": "New Chat", 
                    "messages": [{"role": "assistant", "content": "Hello! I am LawGPT. Ask me about German Law (BGB)."}]
                }
            }
            st.session_state.current_session_id = initial_id
            save_sessions(st.session_state.sessions)

def create_new_chat():
    """Callback to create a new chat session"""
    new_id = str(uuid.uuid4())
    st.session_state.sessions[new_id] = {
        "title": "New Chat", 
        "messages": [{"role": "assistant", "content": "Hello! I am LawGPT. Ask me about German Law (BGB)."}]
    }
    st.session_state.current_session_id = new_id
    save_sessions(st.session_state.sessions)

def delete_chat(session_id):
    """Callback to delete a chat session"""
    if len(st.session_state.sessions) > 1:
        del st.session_state.sessions[session_id]
        # Switch to the first available session
        st.session_state.current_session_id = list(st.session_state.sessions.keys())[0]
    else:
        # If it's the last one, just reset it
        st.session_state.sessions[session_id] = {
            "title": "New Chat", 
            "messages": [{"role": "assistant", "content": "Hello! I am LawGPT. Ask me about German Law (BGB)."}]
        }
    save_sessions(st.session_state.sessions)

def main():
    settings = Settings()
    init_session()

    # --- Sidebar Configuration ---
    with st.sidebar:
        st.title("⚖️ LawGPT")
        
        # 1. New Chat Button
        if st.button("➕ New Chat", use_container_width=True):
            create_new_chat()
            st.rerun() # Force rerun to update UI immediately

        st.divider()

        # 2. History / Session Selector
        st.markdown("**Chat History**")
        
        session_ids = list(st.session_state.sessions.keys())
        session_titles = [st.session_state.sessions[sid]["title"] for sid in session_ids]
        
        # Find index of current session
        current_index = 0
        try:
            current_index = session_ids.index(st.session_state.current_session_id)
        except ValueError:
            current_index = 0
            st.session_state.current_session_id = session_ids[0]

        selected_title = st.radio(
            "Select Chat", 
            session_titles, 
            index=current_index, 
            label_visibility="collapsed"
        )
        
        selected_index = session_titles.index(selected_title)
        st.session_state.current_session_id = session_ids[selected_index]

        st.divider()
        
        # 3. Settings
        st.markdown("### Settings")
        user_language = st.selectbox(
            "Response Language", 
            ["zh-tw", "en", "de"],
            index=0,
            help="Choose the language you want the assistant to reply in."
        )
        show_graph = st.toggle("Show Reasoning Graph", value=False)
        
        st.markdown("---")
        # Delete Button for current chat
        if st.button("🗑️ Delete Current Chat"):
            delete_chat(st.session_state.current_session_id)
            st.rerun()

    # --- Main Interface ---
    
    # Get current session data
    current_session = st.session_state.sessions[st.session_state.current_session_id]
    messages = current_session["messages"]

    st.caption(f"Current Chat: {current_session['title']}")

    # Initialize components (Cached)
    if "retriever" not in st.session_state:
        st.session_state.retriever = Retriever()
    if "llm" not in st.session_state:
        st.session_state.llm = GeminiLLMAPI(
            api_key=settings.GOOGLE_API_KEY,
            model="gemini-flash-latest",
            system_instruction=(
                "You are an expert German legal advisor. "
                "Your primary knowledge source is the German Civil Code (BGB). "
                "Regardless of the input language, you MUST respond in the language specified by the user in the prompt."
            )
        )

    # Display Chat History for *Current Session*
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.image(msg["image"], caption="Uploaded Image", use_column_width=True)

    # Input Area
    prompt = st.chat_input("Ask a legal question...")
    uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if prompt:
        # 1. Update Title (if first user message)
        if current_session["title"] == "New Chat":
            new_title = prompt[:20] + "..." if len(prompt) > 20 else prompt
            current_session["title"] = new_title
            # Save title update
            save_sessions(st.session_state.sessions)

        # 2. Handle User Input
        user_image = None
        if uploaded_file:
            user_image = Image.open(uploaded_file)
            messages.append({"role": "user", "content": prompt, "image": user_image})
            save_sessions(st.session_state.sessions) # Save input
            with st.chat_message("user"):
                st.markdown(prompt)
                st.image(user_image, caption="Uploaded Image", use_column_width=True)
        else:
            messages.append({"role": "user", "content": prompt})
            save_sessions(st.session_state.sessions) # Save input
            with st.chat_message("user"):
                st.markdown(prompt)

        # 3. Run Agent (LangGraph)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing legal context..."):
                try:
                    # History Conversion
                    history_messages = []
                    for msg in messages:
                        if msg["role"] == "user":
                            history_messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            history_messages.append(AIMessage(content=msg["content"]))
                    
                    # Prepare Input
                    enhanced_prompt = f"STRICT INSTRUCTION: Respond only in {user_language}.\n\n{prompt}"
                    input_messages = history_messages[:-1] 
                    input_messages.append(HumanMessage(content=enhanced_prompt))
                    
                    initial_state = {
                        "messages": input_messages,
                        "documents": [] 
                    }
                    
                    # Invoke Graph
                    final_state = app.invoke(initial_state)
                    
                    # Extract Response
                    new_messages = final_state['messages'][len(input_messages):] 
                    response_text = "I'm sorry, I couldn't generate a response."
                    for m in reversed(new_messages):
                        if isinstance(m, AIMessage):
                            response_text = m.content
                            break
                    
                    st.markdown(response_text)
                    
                    # Source Preview
                    unique_sources = {}
                    for msg in new_messages:
                        if isinstance(msg, ToolMessage):
                            try:
                                docs = json.loads(msg.content)
                                if isinstance(docs, list):
                                    for doc in docs:
                                        meta = doc.get('metadata', {})
                                        link = meta.get('link', 'Unknown')
                                        if link not in unique_sources:
                                            unique_sources[link] = meta
                            except:
                                pass
                    
                    if unique_sources:
                        with st.expander("📚 Source Preview (查看法條原文)"):
                            for link, meta in unique_sources.items():
                                title = meta.get('section_title', 'Legal Document')
                                content = meta.get('content', 'No content available.')
                                st.markdown(f"**{title}**")
                                st.caption(f"Source: {link}")
                                st.text(content)
                                st.divider()

                    # Disclaimer
                    st.warning(DISCLAIMERS.get(user_language, DISCLAIMERS["en"]))
                    
                    # Graph Visualization
                    if show_graph:
                        with st.expander("Show Reasoning Graph"):
                            try:
                                graph_image = app.get_graph().draw_mermaid_png()
                                st.image(graph_image, caption="Agent Execution Path")
                            except:
                                st.info("Graph visualization unavailable.")

                    # Save to Session
                    messages.append({"role": "assistant", "content": response_text})
                    save_sessions(st.session_state.sessions) # Save response
                    
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)

if __name__ == "__main__":
    main()