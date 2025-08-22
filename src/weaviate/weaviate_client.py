from weaviate.classes.config import( #type: ignore
    Configure, 
    VectorDistances
    ) 
import weaviate
import requests
import os
from src.utils.logger import Logger
logger= Logger(__name__)

class WeaviateClient:
    def __init__(self):
        self.client = self._client()
        self.embed_url = os.getenv("EMBEDDING_URL")

    def _client(self):
        """Connect to Weaviate"""
        client = weaviate.connect_to_custom(
            http_host=os.getenv("WEAVIATE_HTTP_HOST"),
            http_port=os.getenv("WEAVIATE_HTTP_PORT"),
            http_secure=False,
            grpc_host=os.getenv("WEAVIATE_GRPC_HOST"),
            grpc_port=os.getenv("WEAVIATE_GRPC_PORT"),
            grpc_secure=False,
        )       
        return client
    
    def _ensure_connection(self):
        """Check if Weaviate is ready"""
        if not self.client.is_ready():
            raise Exception("Weaviate is not ready")
        return True
    
    def _custom_vectorizer(self, doc: str, embed_url: str= None) -> list[float]:
        """
        Custom vectorizer
        Args:
            doc (str): document to be vectorized
        Returns:
            list[float]: vectorized document
        Examples:
            >>> weaviate_client._custom_vectorizer("test")
            [0.1, 0.2, 0.3, ...]
            >>> weaviate_client._custom_vectorizer("test", "http://localhost:3390/v1/embeddings")
            [0.1, 0.2, 0.3, ...]
        """
        embed_payload = {
            "input": doc
        }
        if embed_url is None:
            embed_url = self.embed_url
            logger.info(f"Using default embed_url: {embed_url}")
        try:
            response = requests.post(
                f"{embed_url}", 
                json=embed_payload,
                timeout=10
                )
            response.raise_for_status()
            if response.status_code == 200:
                vector_embeded = response.json()["data"][0]["embedding"]
                return vector_embeded
        except Exception as e:
            logger.info(f"Lỗi khi vector hóa: {e}")
        return None
    
    def list_collections(self) -> dict[str]:
        """List all collections in Weaviate"""
        if not self._ensure_connection():
            logger.error("Weaviate is not ready")
            return None
        return self.client.collections.list_all()
    
    def create_collection(
        self, 
        collection_name: str, 
        model_name: str = "Qwen3-Embedding-0.6B",
        distance_metric: str = "cosine",
        )-> bool:
        """
        Create a new collection in Weaviate
        Args:
            collection_name (str): name of the collection
            model_name (str): name of the model
            distance_metric (str): distance metric, can be "cosine" or "dot"
        Returns:
            bool: True if success, False otherwise
        Examples:
            >>> weaviate_client.create_collection("test_collection")
            True
        """
        if not self._ensure_connection():
            logger.error("Weaviate is not ready")
            raise Exception("Weaviate is not ready")
        
        if not self.client.collections.exists("collection_name"):
            logger.error(f"Collection {collection_name} already exists")
            return None
        
        if distance_metric == "cosine":
            distance_metric = VectorDistances.COSINE
        else:
            distance_metric = VectorDistances.DOT
        
        self.client.collections.create(
            collection_name,
            vector_config=[
                Configure.Vectors.self_provided(
                    name=model_name,
                    vector_index_config=Configure.VectorIndex.hnsw(
                        distance_metric=distance_metric
                    ),
                ),
            ]
        )
        logger.info(f"""\n
                    Collection {collection_name} created\n 
                    Distance metric: {distance_metric}\n
                    Model: Qwen3-Embedding-0.6B\n
                    """)
        return True
    
    def delete_collection(self, collection_name: str) -> bool:
        if not self._ensure_connection():
            logger.error("Weaviate is not ready")
            return None
        
        if not self.client.collections.exists(collection_name):
            logger.error(f"Collection {collection_name} does not exist")
            return None
        
        self.client.collections.delete(collection_name)
        logger.info(f"Collection {collection_name} deleted")
        return True
    
    def delete_object_in_collection(self, collection_name: str, where: dict) -> bool:
        if not self._ensure_connection():
            logger.error("Weaviate is not ready")
            return None
        
        if not self.client.collections.exists(collection_name):
            logger.error(f"Collection {collection_name} does not exist")
            return None
        
        self.client.collections.get(collection_name).data.delete_many(
            where=where,
            dry_run=True,
            verbose=True
        )
        return True