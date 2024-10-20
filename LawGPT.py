#!/usr/bin/env python
# coding: utf-8

"""
This script sets up a Retrieval-Augmented Generation (RAG) system using LlamaIndex,
allowing users to select different online LLM models and configure the system via
command-line arguments.
"""
# install all relevant packages(for colab)
# %pip install rich
# %pip install llama-index-readers-file pymupdf
# %pip install llama-index-vector-stores-postgres
# %pip install llama-index-embeddings-huggingface
# %pip install llama-index-llms-llama-cpp
# %pip install llama-index-llms-gemini
# %pip install llama-index
# %pip install 'google-generativeai==0.3.1'
# install openai if you want to use semantic embedding
# %pip install llama-index-embeddings-openai
# %pip install psycopg2-binary asyncpg "sqlalchemy[asyncio]" greenlet

# !git clone https://github.com/pgvector/pgvector.git

# !apt-get install -y postgresql-server-dev-14
# !apt-get install -y make gcc

# %cd pgvector
# !make && make install
# !apt-get update
# !apt-get install -y postgresql postgresql-contrib

# load
from transformers import pipeline
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms import OpenAI, Anthropic
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index import VectorStoreIndex
import os
import sys
import argparse
import getpass
import json
from typing import List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from dotenv import load_dotenv

# load environment var from .env
load_dotenv()

DEFAULT_CHUNK_SIZE = 256
AVAILABLE_LLM_MODELS = {
    "openai_gpt35": {"source": "OpenAI", "model_name": "gpt-3.5-turbo"},
    "openai_gpt4": {"source": "OpenAI", "model_name": "gpt-4"},
    "anthropic_claude_v1": {"source": "Anthropic", "model_name": "claude-v1"},
    # you can add more models here
}
AVAILABLE_VECTOR_STORES = ["postgresql", "pinecone", "weaviate", "qdrant"]


def parse_arguments():
    parser = argparse.ArgumentParser(description="RAG System with LlamaIndex")
    parser.add_argument(
        "--llm_model",
        type=str,
        choices=AVAILABLE_LLM_MODELS.keys(),
        default="openai_gpt35",
        help="Choose the LLM model to use.",
    )
    parser.add_argument(
        "--embedding_model",
        type=str,
        default="HuggingFace",
        choices=["HuggingFace"],
        help="Choose the embedding model to use.",
    )
    parser.add_argument(
        "--chunk_size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help="Set the chunk size for text splitting.",
    )
    parser.add_argument(
        "--folder_path",
        type=str,
        required=True,
        help="Path to the folder containing your JSON documents.",
    )
    parser.add_argument(
        "--vector_store",
        type=str,
        choices=AVAILABLE_VECTOR_STORES,
        default="postgresql",
        help="Choose the vector store to use.",
    )
    parser.add_argument(
        "--db_host",
        type=str,
        default="localhost",
        help="Database host (for local vector stores).",
    )
    parser.add_argument(
        "--db_port",
        type=str,
        default="5432",
        help="Database port (for local vector stores).",
    )
    parser.add_argument(
        "--db_user",
        type=str,
        default="postgres",
        help="Database user (for local vector stores).",
    )
    parser.add_argument(
        "--db_password",
        type=str,
        help="Database password (for local vector stores).",
    )
    parser.add_argument(
        "--db_name",
        type=str,
        default="vector_db",
        help="Database name (for local vector stores).",
    )
    args = parser.parse_args()
    return args


def check_api_keys(llm_model):
    model_info = AVAILABLE_LLM_MODELS[llm_model]
    model_source = model_info["source"]

    if model_source == "OpenAI":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            openai_api_key = getpass.getpass(
                "Please enter your OpenAI API key: ")
            os.environ["OPENAI_API_KEY"] = openai_api_key
            with open(".env", "a") as f:
                f.write(f"\nOPENAI_API_KEY={openai_api_key}")
            print("Your OpenAI API key has been saved.")
    elif model_source == "Anthropic":
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            anthropic_api_key = getpass.getpass(
                "Please enter your Anthropic API key: ")
            os.environ["ANTHROPIC_API_KEY"] = anthropic_api_key
            with open(".env", "a") as f:
                f.write(f"\nANTHROPIC_API_KEY={anthropic_api_key}")
            print("Your Anthropic API key has been saved.")
    else:
        # check api key for other models
        pass


def embed_model_factory(model_source="HuggingFace", model_name=None, **kwargs):
    """
    Specify the model source and model name to get a certain embedding model from various sources.
    """
    if model_source == "HuggingFace":
        if model_name is None:
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
        embed_model = HuggingFaceEmbedding(model_name=model_name)
    else:
        raise ValueError(f"Unsupported embedding model source: {model_source}")
    return embed_model


def llm_model_factory(model_key, **kwargs):
    """
    Specify the model source and model name to get a certain LLM from various sources.
    """
    model_info = AVAILABLE_LLM_MODELS[model_key]
    model_source = model_info["source"]
    model_name = model_info["model_name"]
    if model_source == "OpenAI":
        llm = OpenAI(
            model=model_name,
            api_key=os.getenv("OPENAI_API_KEY"),
            **kwargs,
        )
    elif model_source == "Anthropic":
        llm = Anthropic(
            model=model_name,
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            **kwargs,
        )
    else:
        raise ValueError(f"Unsupported LLM model source: {model_source}")
    return llm


def setup_vector_store(args, embed_dim):
    """
    Set up the vector store.
    """
    if args.vector_store == 'postgresql':
        from llama_index.vector_stores.postgres import PGVectorStore
        vector_store = PGVectorStore.from_params(
            database=args.db_name,
            host=args.db_host,
            password=args.db_password,
            port=args.db_port,
            user=args.db_user,
            table_name="vector_table",
            embed_dim=embed_dim,
        )
    elif args.vector_store == 'pinecone':
        # Placeholder for Pinecone vector store setup
        # from llama_index.vector_stores import PineconeVectorStore
        # vector_store = PineconeVectorStore(...)
        pass
    elif args.vector_store == 'weaviate':
        # Placeholder for Weaviate vector store setup
        # from llama_index.vector_stores import WeaviateVectorStore
        # vector_store = WeaviateVectorStore(...)
        pass
    elif args.vector_store == 'qdrant':
        # Placeholder for Qdrant vector store setup
        # from llama_index.vector_stores import QdrantVectorStore
        # vector_store = QdrantVectorStore(...)
        pass
    else:
        raise ValueError(f"Unsupported vector store: {args.vector_store}")
    return vector_store


def detect_language(text):
    """
    Detect the language of the given text.
    """
    return detect(text)


def get_translation_pipeline(src_lang, tgt_lang):
    """
    Get a translation pipeline to translate texts between languages.
    """
    if src_lang == tgt_lang:
        return None
    model_name = f"Helsinki-NLP/opus-mt-{src_lang}-{tgt_lang}"
    try:
        translator = pipeline("translation", model=model_name)
    except:
        # 如果没有特定的模型，使用通用模型
        translator = pipeline(
            "translation", model=f"Helsinki-NLP/opus-mt-{src_lang}-en")
    return translator


def main():
    args = parse_arguments()
    check_api_keys(args.llm_model)

    # create LLM
    llm = llm_model_factory(args.llm_model)

    # setup embedding
    embed_model = embed_model_factory(model_source=args.embedding_model)
    sample_embedding = embed_model.get_text_embedding("Test")
    embed_dim = len(sample_embedding)

    # vector db
    vector_store = setup_vector_store(args, embed_dim)

    # init nodes
    nodes: List[TextNode] = []

    # processing documents
    for root, dirs, files in os.walk(args.folder_path):
        for filename in files:
            if filename.endswith('.json'):
                file_path = os.path.join(root, filename)
                # get language from the folder
                target_lang = lang = os.path.basename(
                    os.path.dirname(file_path))
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # use proper splitter
                if lang == 'de':
                    text_parser = SentenceSplitter(
                        language='de', chunk_size=args.chunk_size)
                elif lang == 'en':
                    text_parser = SentenceSplitter(
                        language='en', chunk_size=args.chunk_size)
                else:
                    text_parser = SentenceSplitter(chunk_size=args.chunk_size)

                for section_data in data.get('sections', []):
                    section = section_data.get('section', '')
                    content = section_data.get('content', '')
                    link = section_data.get('link', '')

                    text_chunks = text_parser.split_text(content)

                    for idx, text_chunk in enumerate(text_chunks):
                        embedding = embed_model.get_text_embedding(text_chunk)
                        node = TextNode(
                            text=text_chunk,
                            embedding=embedding,
                            metadata={
                                "section": section,
                                "link": link,
                                "filename": filename,
                                "language": lang
                            }
                        )
                        nodes.append(node)

    # create index
    index = VectorStoreIndex(
        nodes=nodes,
        vector_store=vector_store,
        embed_model=embed_model,
    )

    # create query engine
    query_engine = index.as_query_engine(llm=llm)

    # user interaction
    while True:
        user_input = input("Please enter your question (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break

        # translate with llm to target language
        translation_prompt = f"Translate the following text to {target_lang}:\n\n{user_input}\n\nOnly provide the translated text."
        translated_input = llm.complete(translation_prompt).strip()

        # execute query
        response = query_engine.query(translated_input)

        # get original node
        top_k = 1
        retrieved_nodes = index.retrieve(translated_input, top_k=top_k)
        original_text = retrieved_nodes[0].node.text
        metadata = retrieved_nodes[0].node.metadata

        # translate back to user's language
        answer_translation_prompt = (
            f"Translate the following text to the same language as the user's original question.\n\n"
            f"User's Original Question:\n{user_input}\n\n"
            f"Text to Translate:\n{str(response)}\n\n"
            f"Only provide the translated text."
        )
        translated_answer = llm.complete(answer_translation_prompt).strip()

        # preparing output
        output_data = {
            "Original Question": user_input,
            "Translated Question": translated_input,
            "Translated Answer": translated_answer,
            "Original Text": original_text,
            "Metadata": metadata,
        }
        # init rich
        console = Console()
        # output with human readable format with rich
        for key, value in output_data.items():
            panel = Panel(value, title=key, expand=False)
            console.print(panel)

        # using rich Table to desplay metadata
        metadata_table = Table(title="Metadata")
        metadata_table.add_column("Key", style="cyan", no_wrap=True)
        metadata_table.add_column("Value", style="magenta")

        for meta_key, meta_value in metadata.items():
            metadata_table.add_row(meta_key, str(meta_value))

        console.print(metadata_table)


if __name__ == "__main__":
    main()
