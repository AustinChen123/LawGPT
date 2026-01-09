# LawGPT - Agentic Legal Assistant

LawGPT is a sophisticated, **Agentic RAG (Retrieval-Augmented Generation)** system designed for German Statutory Law (BGB). Unlike simple Q&A bots, LawGPT employs a graph-based architecture to reason about user intent, expand queries for higher recall, and strictly ground its answers in legal texts.

Built with **LangGraph**, **Google Gemini 2.0 Flash**, and **Pinecone Serverless**.

## 🚀 Key Features (Engineering Highlights)

### 🧠 1. Agentic Reasoning & Routing
*   **Hybrid Intent Router**: Uses a "Rule-based + LLM" hybrid approach. Critical keywords (e.g., "§", "contract") trigger immediate retrieval, while ambiguous queries are analyzed by the LLM with a "safety-first" bias.
*   **LangGraph Orchestration**: Replaces linear chains with a stateful graph (Router -> Decision -> Retrieval -> Generation), allowing for conditional logic and future multi-step reasoning loops.

### 🔍 2. Advanced Retrieval (RAG)
*   **Multi-Query Expansion (COT)**: The agent uses Chain-of-Thought reasoning to decompose a user's question into multiple distinct German search queries (Synonyms, Legal Terms, Statute Numbers), significantly improving recall.
*   **Structural Chunking**: Instead of arbitrary character splitting, the preprocessor respects the legal hierarchy, chunking text by **Sections (Paragraphs)** to preserve the integrity of rules and exceptions.
*   **Deduplicated Retrieval**: Aggregates results from multiple sub-queries to ensure a comprehensive context window.
*   **LLM Reranking**: Applies a second-pass relevance filter using the LLM to discard irrelevant documents before generation.

### 🛡️ 3. Robustness & Compliance
*   **Citation-First Generation**: Every legal claim is strictly grounded in retrieved documents.
*   **Hallucination Guardrails**: If the retrieved context is insufficient, the agent explicitly refuses to answer rather than fabricating laws.
*   **Native 768-Dimension**: Optimized for cost and performance using Google's `text-embedding-004` and Pinecone's serverless infrastructure.

### 💬 4. Modern UX (Streamlit)
*   **Multi-Session Chat**: Supports creating, switching, and deleting multiple independent conversation sessions.
*   **Multimodal Input**: Users can upload images (e.g., contracts) for analysis.
*   **Source Preview**: "Trust but Verify" — users can expand citations to read the original German legal text directly in the UI.
*   **Graph Visualization**: Real-time visualization of the agent's decision path (LangGraph).

## 🛠️ Tech Stack

*   **Framework**: [LangGraph](https://langchain-ai.github.io/langgraph/) (Agent Logic)
*   **LLM**: Google Gemini 2.0 Flash / Flash-Latest (via `google-genai` SDK)
*   **Vector DB**: Pinecone Serverless (AWS us-east-1)
*   **UI**: Streamlit
*   **Dependency Management**: `uv` (Fast Python package installer)
*   **Testing**: `behave` (BDD Framework) & LLM-as-a-Judge Evaluation

## 🏗️ Architecture & Branching

*   **`main`**: Production-ready code.
*   **`test/benchmark`**: **RAGAS Evaluation**. Contains synthetic data generators (`dataset_generator.py`) and LLM-as-a-Judge logic (`judge.py`). This branch calculates metrics like **Context Recall** and **Faithfulness**.
*   **`test/bdd-framework`**: **Behavior Tests**. Contains `behave` features and steps for end-to-end scenario verification.

## 📦 Installation & Usage

1.  **Clone & Install Dependencies**
    ```bash
    git clone https://github.com/yourname/LawGPT.git
    cd LawGPT
    uv pip install -r requirements.txt
    ```

2.  **Environment Setup**
    Create a `.env` file:
    ```env
    GOOGLE_API_KEY=your_key
    PINECONE_API_KEY=your_key
    PINECONE_HOST=your_host_url
    ```

3.  **Run the Application**
    ```bash
    uv run streamlit run main_streamlit.py
    ```

4.  **Data Ingestion (Optional)**
    To crawl and index new data:
    ```bash
    uv run python main.py --crawl --embedding
    ```

## 🧪 Testing & Evaluation

*   **Run BDD Scenarios (Behavior)**:
    ```bash
    uv run behave bdd/features/legal_query.feature
    ```
*   **Run Quantitative Evaluation** (Switch to `test/benchmark` branch):
    ```bash
    git checkout test/benchmark
    uv run python -m evaluation.run_benchmark
    ```

## 📄 License

MIT License.
