from .url_handler import generate_target_urls, get_doc_url
from .extractor import html_extraction_de
from .storage import save_to_json
import os
import pandas as pd
from tqdm import tqdm


class Crawler:
    def __init__(self, target_list, endpoint, data_folder="data"):
        self.target_list = target_list
        self.endpoint = endpoint
        self.data_folder = data_folder
        os.makedirs(self.data_folder, exist_ok=True)

    def run(self):
        for letter in self.target_list:
            target_url = f"{self.endpoint}/Teilliste_{letter}.html"
            print(f"Processing subset {letter}...")

            # 取得 URL 清單與描述
            print("Preparing urls")
            links = generate_target_urls(target_url, self.endpoint)

            for _, row in tqdm(links.iterrows(), total=links.shape[0], leave=True, desc="Processing"):
                title = row["anchor_tags"].get_text().replace("/", "_")
                base_url = row["full_link"]
                main_topic = row["description"]

                # 判斷是否已存在檔案
                json_path = f"{self.data_folder}/{title}.json"
                if os.path.exists(json_path):
                    tqdm.write(f"File exists: {title}")
                    continue

                # 提取資料
                sections = html_extraction_de(base_url)
                if not sections:
                    continue

                # 儲存資料
                save_to_json({
                    "main_topic": main_topic,
                    "sections": sections
                }, json_path)
                tqdm.write(f"Saved: {title}")
