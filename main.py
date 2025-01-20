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
        print("[INFO] Running RAG...")
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(
            host="https://lawgpt-qitbai1.svc.aped-4627-b74a.pinecone.io")

        target_lang = "de"

        llm = GeminiLLMAPI(
            api_key=settings.GOOGLE_API_KEY,
            model="models/gemini-2.0-flash-exp",
            system_instruction="You are a law advisor. We will provide relevant material to the questions,\
                                please answer based on the documents and following the instructions.\
                                Don't do extra inference if the documents don't specify.\
                                Don't talk too much about how you search the documents, but saying 'consult professional lawyers'\
                                Don't say 'from documents' but directly answer the question with the information provided.\
                                Extra information could be provided if they are mentioned in the documents. \
                                Also specify which law you are referencing"
        )
        embedding_api = GeminiEmbeddingAPI(settings.GOOGLE_API_KEY)

        console = Console()
        # **執行 Rerank（如果啟用）**
        while True:
            user_input = input(
                "Please enter your question (or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break

            # (a) 翻譯使用者問題到目標語言
            translation_prompt = (
                f"Translate the following text to {target_lang}:\n\n"
                f"{user_input}\n\n"
                "Only provide the translated text in de."
            )
            translated_input = llm.generate_response(translation_prompt)
            vector = embedding_api.embed_text(translated_input)
            # (b) Query Engine 查詢
            response = index.query(
                vector=vector,
                top_k=10,
                include_values=True,
                include_metadata=True
            )

            # (d) 整理結果
            matches = response["matches"]

            # 假設我們把所有相似節點的內容都串起來
            retrieved_text = ""
            links = []
            for match in matches:
                meta = match.get("metadata", {})
                # 如果你在 metadata 裏存了原始文本
                chunk_content = meta.get("content", "")
                links.append(meta.get("link", ""))
                retrieved_text += chunk_content + "\n"

            # (e) 將回答翻譯回使用者原始語言
            user_language = "zh-tw"
            answer_translation_prompt = (
                f"Translate the following text to the same language as the user's original question.\n\n"
                f"User's Original Question:\n{user_input}\n\n"
                f"Supporting documents:\n{retrieved_text}\n\n"
                f"Only provide the answer related to the question in {user_language}."
            )
            translated_answer = llm.generate_response(
                answer_translation_prompt)
            # ------------------------------------------------------------
            # 4. 輸出結果
            # ------------------------------------------------------------
            output_data = {
                "Original Question": user_input,
                "Translated Question": translated_input,
                "Translated Answer": translated_answer
            }
            for key, value in output_data.items():
                panel = Panel(value, title=key, expand=False)
                console.print(panel)


if __name__ == "__main__":
    main()
