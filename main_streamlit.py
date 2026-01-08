import streamlit as st
import os
from config.settings import Settings
from rag.gemini_api import GeminiLLMAPI
from rag.retriever import Retriever
from PIL import Image
from agent.graph_agent import app # Import the compiled LangGraph
from langchain_core.messages import HumanMessage, AIMessage

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
                    # Construct input for the graph
                    # Note: Our current simple graph only uses the text query in the first message
                    # For multimodal, we need to pass the image to the LLM.
                    # However, our current 'agent/graph_agent.py' LLM call logic inside 'generation_node' 
                    # doesn't yet extract images from the state. 
                    # For this iteration, we will focus on the text flow + Graph Visualization.
                    # Multimodal in LangGraph requires passing the image in the state.
                    
                    # Hack: Since we want to use the LangGraph structure, we pass the text query.
                    # The prompt construction in graph_agent needs to know about user_language too.
                    # But graph_agent is hardcoded. 
                    # To make it dynamic, we should really pass configuration to the graph.
                    
                    # For now, let's inject the language instruction into the prompt
                    enhanced_prompt = f"STRICT INSTRUCTION: Respond only in {user_language}.\n\n{prompt}"
                    
                    initial_state = {
                        "messages": [HumanMessage(content=enhanced_prompt)],
                        "documents": [] 
                    }
                    
                    # Invoke the graph!
                    final_state = app.invoke(initial_state)
                    response_text = final_state['messages'][-1].content
                    
                    st.markdown(response_text)
                    
                    # Disclaimer
                    st.warning(DISCLAIMERS.get(user_language, DISCLAIMERS["en"])), icon="⚠️")
                    
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

                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)

if __name__ == "__main__":
    main()
