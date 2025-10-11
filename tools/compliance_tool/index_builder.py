from llama_index.core import SimpleDirectoryReader


print("Loading file")
file_reader = SimpleDirectoryReader("./data")
file= file_reader.load_data()

from llama_index.core.schema import Document

def clean_text(text):
    return text.encode("utf-8", "replace").decode("utf-8")

def clean_documents(documents):
    cleaned_docs = []
    for doc in documents:
        if hasattr(doc, "text"):
            cleaned_text = clean_text(doc.text)
            # Create a new Document with the cleaned text and preserve metadata
            cleaned_docs.append(Document(text=cleaned_text, metadata=getattr(doc, "metadata", {})))
        else:
            cleaned_docs.append(doc)
    return cleaned_docs


final_documents = clean_documents(documents=file)

import os
from llama_index.core import  Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.ingestion import IngestionPipeline

from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding


Settings.embed_model = OllamaEmbedding(
    model_name="mxbai-embed-large",  # or another supported model
    base_url="http://localhost:11434"  # default Ollama endpoint
)
Settings.llm = Ollama(
    model="mistral",
    request_timeout=60.0,
    context_window=8000,
)

pipeline = IngestionPipeline(
    transformations=[
        SentenceSplitter(chunk_size=1024 , chunk_overlap=20),
        Settings.embed_model 
    ]
)

file_node = pipeline.run(documents = final_documents)
    
import chromadb
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext

#intilaize client , setting path to save data
file_db = chromadb.PersistentClient(path="./storage_file")

# create collection
file_collection = file_db.get_or_create_collection("file")

# assign chroma as vector store

file_vector_store = ChromaVectorStore(chroma_collection=file_collection)
FileStorageContext = StorageContext.from_defaults(vector_store=file_vector_store)


file_index = VectorStoreIndex(
    nodes=file_node , storage_context=FileStorageContext
)

