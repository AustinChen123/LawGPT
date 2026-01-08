import streamlit as st
import os
from config.settings import Settings
from rag.gemini_api import GeminiLLMAPI
from rag.retriever import Retriever
from PIL import Image

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
        st.divider()
        st.markdown("### Multimodal Capabilities")
        st.write("You can upload images of legal documents for analysis.")
        st.divider()
        st.markdown("Powered by **LawGPT**")

    # Main Interface
    st.title("⚖️ LawGPT: German Law Assistant")
    st.caption("Ask anything about German Statutory Law. Input can be in any language.")

    # Initialize components (Cached to avoid reloading)
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

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I am LawGPT. I can help you with German legal questions (BGB). You can also upload a document image for me to analyze."}
        ]

    # Display Chat History
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg:
                st.image(msg["image"], caption="Uploaded Image", use_column_width=True)

    # Input Area
    prompt = st.chat_input("Ask a legal question...")
    uploaded_file = st.file_uploader("Upload an image (optional)", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

    if prompt:
        # 1. Handle User Input
        user_msg_content = prompt
        user_image = None
        
        if uploaded_file:
            user_image = Image.open(uploaded_file)
            st.session_state.messages.append({"role": "user", "content": prompt, "image": user_image})
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
        with st.chat_message("user"):
            st.markdown(prompt)
            if user_image:
                st.image(user_image, caption="Uploaded Image", use_column_width=True)

        # 2. RAG Retrieval (Text only)
        # We retrieve context based on the text prompt
        with st.spinner("Searching legal database..."):
            retrieved_docs = st.session_state.retriever.query(prompt, top_k=5)
            
        # Format context
        context_str = ""
        citation_links = []
        for doc in retrieved_docs:
            meta = doc.get("metadata", {})
            content = meta.get("content", "")
            link = meta.get("link", "")
            context_str += f"Source ({link}):\n{content}\n\n"
            if link not in citation_links:
                citation_links.append(link)

        # 3. Generate Answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                full_prompt = (
                    f"STRICT INSTRUCTION: Respond only in the following language: {user_language}\n\n"
                    f"User Question: {prompt}\n\n"
                    f"Retrieved Legal Context (German Statutes):\n{context_str}\n\n"
                    f"Task: Analyze the user's question and any provided image based on the legal context. "
                    f"Provide a detailed answer strictly in {user_language}. "
                    "Cite relevant paragraphs (e.g., § 123 BGB) clearly."
                )
                
                try:
                    # Call LLM with text + image (if any)
                    response_text = st.session_state.llm.generate_response(
                        prompt=full_prompt,
                        images=[user_image] if user_image else None
                    )
                    
                    st.markdown(response_text)
                    
                    # Display Sources
                    if citation_links:
                        st.markdown("---")
                        st.markdown("**References:**")
                        for link in citation_links:
                            st.markdown(f"- [{link}]({link})")
                            
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error: {str(e)}"
                    st.error(error_msg)

if __name__ == "__main__":
    main()