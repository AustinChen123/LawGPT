import sys
import os
import time
from config.settings import Settings
from rag.gemini_api import GeminiEmbeddingAPI, GeminiLLMAPI
from pinecone import Pinecone
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    settings = Settings()

    st.title("LawGPT with Streamlit")

    # 1. 初始化 Pinecone
    pc = Pinecone(api_key=settings.PINECONE_API_KEY)
    index = pc.Index(
        host=settings.PINECONE_HOST)

    # 2. 初始化 LLM & Embedding
    llm = GeminiLLMAPI(
        api_key=settings.GOOGLE_API_KEY,
        model="models/gemini-2.0-flash-exp",
        system_instruction=(
            "You are a law advisor. We will provide relevant material to the questions, "
            "please answer based on the documents and following the instructions. "
            "Don't do extra inference if the documents don't specify. "
            "Don't talk too much about how you search the documents, but saying 'consult professional lawyers'. "
            "Don't say 'from documents' but directly answer the question with the information provided. "
            "Also specify which law you are referencing."
            "Make sure you mention a disclaimer after each conversation."
        )
    )
    embedding_api = GeminiEmbeddingAPI(settings.GOOGLE_API_KEY)

    # 3. Streamlit互動參數：語言選擇 & 問題輸入
    user_language = st.selectbox("Select answer language:", [
                                    "de", "en", "zh", "zh-tw"], index=0)
    user_input = st.text_input("Please enter your question:")

    # 4. 當使用者按下「Send」按鈕，開始RAG流程
    if st.button("Send"):
        if not user_input.strip():
            st.warning("Please enter your question first.")
            st.stop()

        # (a) 翻譯使用者問題到目標語言 (以de為例，你可換成 user_language )
        translation_prompt = (
            f"Translate the following text to de:\n\n"
            f"{user_input}\n\n"
            "Only provide the translated text in de."
        )
        translated_input = llm.generate_response(translation_prompt)

        time.sleep(0.1)  # 模擬呼叫API延遲

        # 嵌入
        vector = embedding_api.embed_text(translated_input)

        # (b) Query Engine 查詢
        response = index.query(
            vector=vector,
            top_k=10,
            include_values=True,
            include_metadata=True
        )

        # (c) 解析 Pinecone 查詢結果
        matches = response.get("matches", [])
        retrieved_text = ""
        links = []
        for match in matches:
            meta = match.get("metadata", {})
            chunk_content = meta.get("content", "")
            links.append(meta.get("link", ""))
            retrieved_text += chunk_content + "\n"

        # (d) 最終翻譯回答回原語言
        answer_translation_prompt = (
            f"Translate the following text to the same language as the user's original question.\n\n"
            f"User's Original Question:\n{user_input}\n\n"
            f"Supporting documents:\n{retrieved_text}\n\n"
            f"Only provide the answer related to the question in {user_language}."
        )
        translated_answer = llm.generate_response(
            answer_translation_prompt)

        # 5. 在Streamlit介面上輸出結果
        output_data = {
            "Original Question": user_input,
            "Translated Question": translated_input,
            "Translated Answer": translated_answer
        }

        for key, value in output_data.items():
            st.markdown(f"**{key}**: {value}")

        st.markdown("#### Links from metadata:")
        for link in links:
            if link:
                st.write(f"- {link}")


if __name__ == "__main__":
    main()
