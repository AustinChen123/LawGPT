from .url_handler import generate_target_urls, get_doc_url
from .extractor import html_extraction_de
from .storage import save_to_json
from .state_manager import StateManager
import os
import json
import pandas as pd
from tqdm import tqdm


class Crawler:
    def __init__(self, target_list, endpoint, data_folder="data"):
        self.target_list = target_list
        self.endpoint = endpoint
        self.data_folder = data_folder
        self.state_manager = StateManager(os.path.join(data_folder, "crawler_state.json"))
        os.makedirs(self.data_folder, exist_ok=True)

    def run(self):
        for letter in self.target_list:
            target_url = f"{self.endpoint}/Teilliste_{letter}.html"
            print(f"Processing subset {letter}...")

            # 取得 URL 清單與描述
            try:
                print("Preparing urls")
                links = generate_target_urls(target_url, self.endpoint)
            except Exception as e:
                print(f"Failed to fetch list for {letter}: {e}")
                continue

            for _, row in tqdm(links.iterrows(), total=links.shape[0], leave=True, desc="Processing"):
                title = row["anchor_tags"].get_text().replace("/", "_")
                base_url = row["full_link"]
                main_topic = row["description"]
                json_path = f"{self.data_folder}/{title}.json"

                try:
                    # 提取資料
                    sections = html_extraction_de(base_url)
                    if not sections:
                        continue
                    
                    # Incremental Update Check
                    # Serialize sections to check for content changes
                    sections_str = json.dumps(sections, sort_keys=True)
                    has_changed = self.state_manager.update_state(base_url, sections_str)
                    
                    # Save only if changed OR file is missing
                    if has_changed or not os.path.exists(json_path):
                        # 儲存資料
                        save_to_json({
                            "main_topic": main_topic,
                            "sections": sections
                        }, json_path)
                        action = "Updated" if has_changed else "Restored"
                        tqdm.write(f"{action}: {title}")
                    else:
                        # Skipped
                        pass
                        
                except Exception as e:
                    tqdm.write(f"Error processing {base_url}: {e}")
                    continue
