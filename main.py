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
from pinecone import ServerlessSpec

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
    if False:
        # if args.rag or not (args.crawl or args.embedding):
        print("[INFO] Running RAG...")
        # 模擬數據
        context = "The quick brown fox jumps over the lazy dog."
        question = "What is jumping over the lazy dog?"

        # 初始化 LLM 模組
        llm_api = GeminiLLMAPI(
            model="models/gemini-1.5-flash",
            system_instruction="You are a helpful assistant."
        )

        # 查詢向量資料庫（模擬）
        query_results = [
            {
                "section": "Section 1",
                "content": "The quick brown fox jumps over the lazy dog.",
                "link": "https://example.com/section1"
            },
            {
                "section": "Section 2",
                "content": "This is another example section.",
                "link": "https://example.com/section2"
            }
        ]

        # **執行 Rerank（如果啟用）**
        if args.rerank:
            print("[INFO] 執行 Rerank 過程...")
            # 模擬 Rerank 的結果處理（未實現詳細邏輯）
            query_results = sorted(
                query_results, key=lambda x: len(x["content"]), reverse=True)

        # 整理查詢結果作為上下文
        context = "\n".join([result["content"] for result in query_results])

        # 向 LLM 提問
        response = llm_api.generate_response(context, question)
        print(f"[RAG Response]: {response}")


if __name__ == "__main__":
    main()
