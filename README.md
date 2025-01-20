# LawGPT

This is a simple practice project demonstrating how to build an RAG (Retrieval-Augmented Generation) service by utilizing various free resources, including a vector database and LLM API.

## Features

1. **Crawler**

   - Fetches legal texts from [Gesetze im Internet](https://www.gesetze-im-internet.de).
   - Stores raw data in JSON format (or other structured formats).

2. **Embedding & Vector Database**

   - Converts textual data into vector embeddings.
   - Uploads and manages these embeddings in a vector database (e.g., Pinecone).
   - Simple progress tracking (counting by sections).

3. **RAG Flow**

   - Uses vector similarity searches to find relevant context.
   - Combines retrieved context with a Large Language Model (LLM) for enhanced responses.
   - (To do) Rerank results before final answer generation.

4. **LLM Integration**

   - Demonstrates how to call LLM APIs (e.g., Google Generative AI, or other providers).
   - Supports multi-language prompts, translations, or system instructions.

5. **Configurations**
   - Loads environment variables (like API keys) from `.env` or system environment (using `python-dotenv` or similar).

## Requirements

- Python 3.9+ (recommended)
- [pip](https://pip.pypa.io/en/stable/installation/) or [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/) for installing dependencies

### Key Python Packages

- **Crawler**: `requests`, `beautifulsoup4` (for web scraping)
- **LLM**: `google-generativeai` (or other libraries for embedding/LLM calls)
- **Vector DB**: `pinecone` (or `pinecone.grpc` if using gRPC approach)
- **python-dotenv** (optional but recommended) for loading environment variables
- **rich** (optional) for better terminal UI

## Installation

1. **Clone Repo & Enter Folder**

   ```bash
   git clone https://github.com/yourname/LawGPT.git
   cd LawGPT
   ```

2. **Create Virtual Environment** (recommended)

   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   - Copy `.env.example` to `.env` (if provided), fill in your `API_KEY`s, etc.
   - Or set environment variables directly (e.g., `PINECONE_API_KEY`, `GOOGLE_API_KEY`).

## Usage

- **Crawl**

  ```bash
  python main.py --crawl
  ```

  Fetches legal texts and stores them under `data/` or specified directory.

- **Embedding & Upload**

  ```bash
  python main.py --embedding
  ```

  Converts scraped text into vectors and upserts them to Pinecone (or another vector DB).

- **RAG (Query)**
  ```bash
  python main.py --rag
  ```
  Prompts the LLM with a user question. The system retrieves relevant context from the vector DB and combines it with an LLM to generate an answer.  
  _Add `--rerank` if you want to enable rerank logic._

## Project Structure

```
.
├── crawler/
│   ├── crawler.py         # Web scraping logic
│   └── storage.py         # Data storage (JSON, etc.)
├── rag/
│   ├── preprocessor.py    # Converts text into embeddings
│   ├── uploader.py        # Uploads vectors + metadata to Pinecone
│   ├── gemini_api.py      # Example LLM integration (Google Generative AI)
│   ├── llm_connector.py   # Another approach for LLM calls
│   └── retriever.py       # Example for searching the vector DB
├── config/
│   └── settings.py        # Global config or environment loading
├── data/                  # Stored crawled data
├── venv/                  # (optional) virtual environment
├── main.py                # CLI workflow entry point
└── README.md
```

## Notes

- By default, the project uses Pinecone as its vector database. You can switch to another vector store (e.g., Weaviate, Milvus) if desired, but you’ll need corresponding client libraries and minor code changes.
- If you plan to store large amounts of text, be mindful of potential API usage limits or cost.

## License

[MIT License](./LICENSE).

---

_Enjoy building your RAG service with LawGPT!_
