import os
from functools import lru_cache
from llama_index.core import  Settings
from llama_index.llms.ollama import Ollama
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.ollama import OllamaEmbedding

Settings.embed_model = OllamaEmbedding(
    model_name="mxbai-embed-large",  # or another supported model
    base_url="http://localhost:11434"  # default Ollama endpoint
)

Settings.llm = Ollama(
    model="llama3.1",
    request_timeout=60.0,
    context_window=8000,
)
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

file_index = VectorStoreIndex.from_vector_store(
    file_vector_store ,storage_context = FileStorageContext
)

from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool

file_query_engine = file_index.as_query_engine(response_mode = "compact")

file_query_tool = QueryEngineTool.from_defaults(
    query_engine=file_query_engine,
    name="file_query_tool",
    description="Tool for querying the file vector store for compliance-related information."
)

tool = [file_query_tool]

from llama_index.core.agent.workflow import AgentWorkflow

agent = AgentWorkflow.from_tools_or_functions(
    tool,
    llm = Settings.llm,
    verbose=False,
)

import asyncio

# Cache for compliance check results to avoid redundant queries
# LRU cache with max 128 entries, should cover most repeated queries
@lru_cache(maxsize=128)
def _get_compliance_response_sync(message: str) -> str:
    """Synchronous cached wrapper for compliance checks."""
    return asyncio.run(_async_check_compliance_uncached(message))

async def _async_check_compliance_uncached(message: str) -> str:
    """Internal uncached async compliance check."""
    try:
        response = await agent.run(
            f"Is this debt collection message compliant with regulations? Message: '{message}'"
        )
        return str(response)
    except Exception as e:
        return f"Error: {e}"

async def async_check_compliance(message: str) -> str:
    """Async compliance check with caching for identical queries."""
    # For async context, we check cache synchronously
    # This is a pragmatic approach - for pure async caching, consider aiocache
    try:
        return _get_compliance_response_sync(message)
    except Exception as e:
        return f"Error: {e}"
    

def check_compliance(message: str) -> str:
    return asyncio.run(async_check_compliance(message))
    
