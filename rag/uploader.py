import pinecone
import json
import os
import time
import re


def sanitize_topic(topic):
    """
    將非 ASCII 字符替換為 "_"
    :param topic: 要處理的主題名稱字符串
    :return: 處理後的字符串，非 ASCII 字符替換為 "_"
    """
    topic = replace_german_chars(topic)  # 先處理德文特殊字符
    # 將非 ASCII 字符替換為 "_"
    topic = re.sub(r'[^\x00-\x7F]', '"', topic)
    return topic


def replace_german_chars(text):
    replacements = {
        'Ä': 'Ae',
        'Ö': 'Oe',
        'Ü': 'Ue',
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss',
        '§': '#'
    }
    for german_char, ascii_equiv in replacements.items():
        text = text.replace(german_char, ascii_equiv)
    return text[:500]


def generate_ascii_id(topic, index):
    """
    根據主題名稱和索引生成唯一 ID，確保全 ASCII 字符
    :param topic: 主題名稱
    :param index: 索引
    :return: ASCII 安全的 ID
    """
    topic_ascii = sanitize_topic(replace_german_chars(topic))
    return f"{topic_ascii}_{index}"


class Uploader:
    """
    上傳模組：負責將向量與對應的 metadata 上傳至向量資料庫
    """

    def __init__(self, index_name: str, api_key: str, progress_file: str = "../progress.json"):
        """
        初始化上傳模組
        :param index_name: Pinecone 索引名稱
        :param api_key: Pinecone API 密鑰
        :param environment: Pinecone 環境名稱
        :param progress_file: 本地記錄上傳進度的檔案
        """
        PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

        # 指定存放檔案的目錄
        PROGRESS_PATH = os.path.abspath(
            os.path.join(PROJECT_ROOT, progress_file))
        pc = pinecone.Pinecone(api_key=api_key)
        self.index = pc.Index(index_name)
        self.progress_file = PROGRESS_PATH

        # 初始化進度檔案
        if not os.path.exists(self.progress_file):
            with open(self.progress_file, "w") as f:
                json.dump({}, f)

    def load_progress(self):
        """載入上傳進度"""
        with open(self.progress_file, "r") as f:
            return json.load(f)

    def save_progress(self, current_count):
        """保存上傳進度"""
        progress = self.load_progress()
        progress["current_count"] = current_count
        time.sleep(0.01)
        with open(self.progress_file, "w") as f:
            json.dump(progress, f)

    def upload_section(self, main_topic: str, section: dict, vector: list, index: int):
        """
        上傳單個 section 到 Pinecone
        :param main_topic: 主題名稱
        :param section: 要上傳的 section 資料
        :param vector: 嵌入向量
        :param index: section 的序號
        """
        # 構建上傳資料
        ID = generate_ascii_id(main_topic, index)
        item = {
            "id": ID,  # 使用主題名稱和序號作為唯一 ID
            "values": vector,
            "metadata": {
                "main_topic": main_topic,
                "section_title": section["section"] if section["section"] else "",
                "content": section["content"] if section["content"] else "",
                "link": section["link"] if section["link"] else ""
            }
        }
        # 執行上傳
        self.index.upsert(vectors=[item])

    # def upload_all(self, main_topic: str, sections: list, vectors: list):
    #     """
    #     上傳所有 sections 和向量
    #     :param main_topic: 主題名稱
    #     :param sections: 所有 sections 的資料列表
    #     :param vectors: 嵌入向量列表
    #     """
    #     # 載入進度
    #     progress = self.load_progress()
    #     current_count = progress.get("current_count", 0)

    #     for i, (section, vector) in enumerate(zip(sections, vectors)):
    #         # 如果已上傳，跳過
    #         if i < current_count:
    #             print(
    #                 f"Skipping section {i+1}/{len(sections)} for '{main_topic}' (already uploaded).")
    #             continue

    #         # 上傳當前 section
    #         print(
    #             f"Uploading section {i+1}/{len(sections)} for '{main_topic}'...")
    #         self.upload_section(main_topic, section, vector, i)

    #         # 更新進度
    #         self.save_progress(i + 1)
