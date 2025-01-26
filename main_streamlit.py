import sys
import os
import argparse
import json
import time
from config.settings import Settings
from crawler.crawler import Crawler
from rag.preprocessor import Preprocessor
from rag.uploader import Uploader
from rag.gemini_api import GeminiEmbeddingAPI, GeminiLLMAPI
from pinecone import Pinecone
from langdetect import detect, detect_langs
from rich.console import Console
from rich.panel import Panel
import streamlit as st

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    # 定義命令列參數
    parser = argparse.ArgumentParser(description="RAG Workflow Manager")
    parser.add_argument("--crawl", action="store_true",
                        help="Activate crawler")
    parser.add_argument("--embedding", action="store_true",
                        help="Activate embedding and upload to vector database")
    parser.add_argument("--rerank", action="store_true",
                        help="Activate rerank for RAG")
    parser.add_argument("--rag", action="store_true",
                        help="Run RAG process")

    args = parser.parse_args()

    settings = Settings()
    # **1. 爬蟲過程**
    if args.crawl:
        print("[INFO] Running crawling process...")

        # 初始化並運行爬蟲
        crawler = Crawler(settings.TARGET_LIST, settings.ENDPOINT,
                          data_folder=settings.DATA_FOLDER)
        crawler.run()

    # **2. 嵌入與上傳過程**
    # **Embedding rate: 1500RPM**
    if args.embedding:
        print("[INFO] Executing embedding and uploading vectors...")

        # 初始化嵌入與上傳模組
        embedding_api = GeminiEmbeddingAPI(settings.GOOGLE_API_KEY)
        preprocessor = Preprocessor(embedding_api)
        uploader = Uploader("lawgpt", settings.PINECONE_API_KEY)
        progress = uploader.load_progress()
        current_count = progress.get("current_count", 0)
        i = 0
        # 遍歷資料夾處理 JSON 檔案
        for root, dirs, files in os.walk(settings.DATA_FOLDER):
            for filename in files:
                if filename.endswith('.json'):
                    file_path = os.path.join(root, filename)
                    print(f"[INFO] Processing file: {file_path}")

                    # 讀取 JSON 檔案
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 逐筆處理每個 section
                    main_topic = data.get('main_topic', 'Unknown')
                    prev_index = 0
                    for sec_id, section_data in enumerate(data.get('sections', [])):
                        section = section_data.get('section', '')
                        content = section_data.get('content', '')
                        link = section_data.get('link', '')

                        if i < current_count:
                            print(
                                f"Skipping section {i+1} for '{main_topic}' (already uploaded).")
                            i += 1
                            continue

                        # 嵌入並逐筆上傳
                        processed_data = preprocessor.process_text(content)
                        for chunk_index, item in enumerate(processed_data):
                            uploader.upload_section(
                                main_topic=main_topic,
                                section={
                                    "section": section,
                                    "link": link,
                                    "content": item["chunk"],
                                    "filename": filename
                                },
                                vector=item["embedding"],
                                index=prev_index
                            )
                            print(
                                f"[INFO] -- Finished upload: {filename} -> Section: {section} -> Chunk: {chunk_index+1}")
                            prev_index += 1
                        i += 1
                        uploader.save_progress(i)
                        time.sleep(60/1500)

    # **3. RAG 流程**
    if args.rag or not (args.crawl or args.embedding):
        # if args.rag or not (args.crawl or args.embedding):
        st.title("LawGPT RAG Demo with Streamlit")

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
