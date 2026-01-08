import streamlit as st
import os
from config.settings import Settings
from rag.gemini_api import GeminiLLMAPI
from rag.retriever import Retriever
from PIL import Image
from agent.graph_agent import app # Import the compiled LangGraph
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import json

# Disclaimer Dictionary
DISCLAIMERS = {
    "en": "Disclaimer: This AI assistant provides information for educational purposes only and does not constitute legal advice. Please consult a qualified lawyer for specific legal issues.",
    "de": "Haftungsausschluss: Dieser KI-Assistent dient nur zu Informationszwecken und stellt keine Rechtsberatung dar. Bitte konsultieren Sie bei konkreten Rechtsfragen einen qualifizierten Anwalt.",
    "zh-tw": "免責聲明：本 AI 助手僅供參考，不構成法律建議。如有具體法律問題，請諮詢合格律師。"
}

# Page Config
st.set_page_config(page_title="LawGPT - Agentic Legal Assistant", page_icon="⚖️", layout="wide")

def main():
    settings = Settings()

    # Sidebar Configuration
    with st.sidebar:
        st.title("⚙️ Settings")
        user_language = st.selectbox(
            "Response Language (回覆語言)", 
            ["zh-tw", "en", "de"],
            index=0,
            help="Choose the language you want the assistant to reply in."
        )
        show_graph = st.toggle("Show Reasoning Graph (顯示思考路徑)", value=False)
        st.divider()
        st.markdown("### Multimodal Capabilities")
        st.write("You can upload images of legal documents for analysis.")
        st.divider()
        st.markdown("Powered by **LawGPT**")

    # Main Interface
    st.title("⚖️ LawGPT: German Law Assistant")
    st.caption("Ask anything about German Statutory Law. Input can be in any language.")

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am LawGPT. I can help you with German legal questions (BGB)."}
        ]

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.image(msg["image"], caption="Uploaded Image", use_column_width=True)
            # Show disclaimer for past assistant messages if it's the last one? 
            # Ideally, disclaimer is shown after every assistant response.
            # We can simplify by just showing it for the NEW response.

    # Input Area
    prompt = st.chat_input("Ask a legal question...")
    uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if prompt:
        # 1. Handle User Input
        user_msg_content = prompt
        user_image = None
        
        # Display User Message
        if uploaded_file:
            user_image = Image.open(uploaded_file)
            st.session_state.messages.append({"role": "user", "content": prompt, "image": user_image})
            with st.chat_message("user"):
                st.markdown(prompt)
                st.image(user_image, caption="Uploaded Image", use_column_width=True)
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

        # 2. Run Agent (LangGraph)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing legal context..."):
                try:
                    # Construct input for the graph with Full History
                    # Hack: Since we want to use the LangGraph structure, we pass the text query.
                    # The prompt construction in graph_agent needs to know about user_language too.
                    
                    # 1. Convert session history to LangChain messages
                    history_messages = []
                    for msg in st.session_state.messages:
                        if msg["role"] == "user":
                            # We might want to include the image in the history if we supported multimodal history fully
                            # For now, text history is the priority for reasoning
                            history_messages.append(HumanMessage(content=msg["content"]))
                        elif msg["role"] == "assistant":
                            history_messages.append(AIMessage(content=msg["content"]))
                    
                    # 2. Append the current enhanced prompt (System Instruction Injection)
                    # Ideally, system instruction should be a SystemMessage at the start.
                    # But our graph agent might not expect it. Let's stick to the current pattern 
                    # but append the history BEFORE the new prompt.
                    
                    # Current Prompt with Strict Instruction
                    enhanced_prompt = f"STRICT INSTRUCTION: Respond only in {user_language}.\n\n{prompt}"
                    
                    # Note: We don't append enhanced_prompt to history_messages directly because 
                    # we want the history to represent the actual conversation, and the new message 
                    # triggers the agent. The Agent's state will start with history + new message.
                    
                    # Actually, for the Agent to "see" the history, we just pass the list.
                    # But we need to make sure we don't duplicate the last user message which we just added to session_state.
                    # Let's rebuild the input state cleanly.
                    
                    input_messages = history_messages[:-1] # All except the last one (which is the raw prompt)
                    input_messages.append(HumanMessage(content=enhanced_prompt)) # Add the instruction-enhanced prompt
                    
                    initial_state = {
                        "messages": input_messages,
                        "documents": [] 
                    }
                    
                    # Invoke the graph!
                    final_state = app.invoke(initial_state)
                    
                    # Extract the *last* AIMessage from the result (the new response)
                    # The graph returns the full history. We only want the new part.
                    new_messages = final_state['messages'][len(input_messages):] 
                    
                    # Find the AI response text
                    response_text = "I'm sorry, I couldn't generate a response."
                    for m in reversed(new_messages):
                        if isinstance(m, AIMessage):
                            response_text = m.content
                            break
                    
                    st.markdown(response_text)
                    
                    # Source Preview (New Feature)
                    unique_sources = {}
                    for msg in new_messages: # Only look for sources in the NEW execution
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
                    st.warning(DISCLAIMERS.get(user_language, DISCLAIMERS["en"]), icon="⚠️")
                    
                    # Graph Visualization
                    if show_graph:
                        with st.expander("Show Reasoning Graph (思考決策圖)"):
                            try:
                                # Provide a default mermaid png
                                graph_image = app.get_graph().draw_mermaid_png()
                                st.image(graph_image, caption="Agent Execution Path")
                            except Exception as e:
                                st.error(f"Could not generate graph: {e}")
                                st.info("Graph visualization requires 'graphviz' or internet access for Mermaid.")

                    # Save to history (Only the AI response)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)

if __name__ == "__main__":
    main()
