import os
import pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
from langchain.schema import Document
from dotenv import load_dotenv
load_dotenv()

# Read environment variables for Pinecone configuration
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT", "us-east1-gcp")
PINECONE_INDEX = os.environ.get("PINECONE_INDEX")
assert PINECONE_API_KEY is not None
assert PINECONE_ENVIRONMENT is not None
assert PINECONE_INDEX is not None

pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)

embeddings = OpenAIEmbeddings()

def upload_docs_to_pinecone(docs: list[Document], namespace: str = ''):
    index_name = PINECONE_INDEX

    # Creates new index
    indexes = pinecone.list_indexes()
    if index_name not in indexes:
        print(f'Index not found, creating index: {index_name}')
        pinecone.create_index(index_name, dimension=1536)

    docsearch = Pinecone.from_documents(
        docs, 
        embeddings, 
        index_name=index_name, 
        namespace=namespace,
    )
    return docsearch


def query_embeddings(query: str, filter: dict = None, namespace: str = '', top_k: int = 5):
    """Queries embeddings using the content in the specified namespace and returns results."""
    index_name = PINECONE_INDEX
    index = Pinecone.from_existing_index(index_name, embeddings)
    results = index.similarity_search(query, k=top_k, namespace=namespace, filter=filter)
    return results