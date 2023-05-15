from langchain.schema import Document
from vectorstore import query_embeddings

# Custom Tools
def search_apis(query: str, limit: int = 3) -> list[Document]:
    """Searches for APIs and their summaries for a query. You can specify a limit on the number of results returned."""
    return query_embeddings(
        query, 
        namespace='api_summaries', 
        top_k=limit
    )

def search_api_endpoints(query: str, limit: int = 5) -> list[Document]:
    """Searches for API endpoints and their information for a given query. You can specify a limit on the number of results returned."""
    return query_embeddings(
        query, 
        namespace='api_endpoints', top_k=limit
    )
