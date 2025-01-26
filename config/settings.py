import os
from dotenv import load_dotenv

load_dotenv()


class Settings:

    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    CONFIG_FOLDER = os.path.dirname(os.path.abspath(__file__))
    DATA_FOLDER = os.path.join(CONFIG_FOLDER, "..\data\de")
    INDEX_NAME = "lawgpt"
    ENDPOINT = "https://www.gesetze-im-internet.de"
    PINECONE_HOST = os.getenv("PINECONE_HOST")
    TARGET_LIST = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                   "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X",
                   "Y", "Z", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
