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
        uploader = Uploader(settings.INDEX_NAME, settings.PINECONE_API_KEY)
        
        # State Manager for Incremental Embedding
        from crawler.state_manager import StateManager
        embed_state_manager = StateManager(os.path.join(settings.DATA_FOLDER, "embedding_state.json"))
        
        # progress = uploader.load_progress() # Deprecated by state manager
        # current_count = progress.get("current_count", 0) 
        i = 0
        
        # 遍歷資料夾處理 JSON 檔案
        for root, dirs, files in os.walk(settings.DATA_FOLDER):
            for filename in files:
                if filename.endswith('.json') and "state" not in filename: # Ignore state files
                    file_path = os.path.join(root, filename)
                    
                    # 讀取 JSON 檔案
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content_str = f.read()
                        data = json.loads(content_str)

                    # Check if file has changed (Transaction Start)
                    if embed_state_manager.check_hash_match(filename, content_str):
                        print(f"[INFO] Skipping {filename} (No changes detected).")
                        continue

                    print(f"[INFO] Processing file: {file_path}")

                    # Clean up old vectors for this file before re-uploading
                    # This prevents zombie chunks if the new content is shorter than the old content
                    uploader.delete_file_vectors(filename)

                    # 逐筆處理每個 section
                    main_topic = data.get('main_topic', 'Unknown')
                    prev_index = 0
                    batch_vectors = []
                    
                    for sec_id, section_data in enumerate(data.get('sections', [])):
                        section = section_data.get('section', '')
                        content = section_data.get('content', '')
                        link = section_data.get('link', '')

                        # 嵌入並分塊
                        processed_data = preprocessor.process_text(content)
                        for chunk_index, item in enumerate(processed_data):
                            # 生成符合 Pinecone 格式的物件
                            from rag.uploader import generate_ascii_id
                            vector_id = generate_ascii_id(main_topic, prev_index)
                            
                            vector_item = {
                                "id": vector_id,
                                "values": item["embedding"],
                                "metadata": {
                                    "main_topic": main_topic if main_topic else "Unknown",
                                    "section_title": section if section else "",
                                    "content": item["chunk"] if item["chunk"] else "",
                                    "link": link if link else "",
                                    "filename": filename
                                }
                            }
                            batch_vectors.append(vector_item)
                            
                            # 當 Batch 滿 100 就上傳
                            if len(batch_vectors) >= 100:
                                uploader.upload_batch(batch_vectors)
                                print(f"[INFO] Batch upload complete ({len(batch_vectors)} vectors)")
                                batch_vectors = []
                                
                            prev_index += 1
                        
                        time.sleep(0.01) # Small delay to avoid API burst limits
                    
                    # 上傳該檔案剩餘的向量
                    if batch_vectors:
                        uploader.upload_batch(batch_vectors)
                        print(f"[INFO] Final batch for {filename} uploaded.")
                        
                    # Commit State (Transaction End)
                    embed_state_manager.update_state(filename, content_str)

    # **3. RAG 流程**
    if args.rag or not (args.crawl or args.embedding):
        # if args.rag or not (args.crawl or args.embedding):
        print("[INFO] Running RAG...")
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(
            host=settings.PINECONE_HOST)

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
                "Please enter your question ('lang' for language setting or 'exit' to quit): ")
            if user_input.lower() == 'exit':
                break
            if user_input.lower() == 'lang':
                user_language = input(
                    "Enter which language you want to use for the answer (en, zh, zh-tw etc.) :")
                continue
            if user_language == "":
                user_language = "de"
            # (a) 翻譯使用者問題到目標語言
            translation_prompt = (
                f"Translate the following text to de:\n\n"
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
