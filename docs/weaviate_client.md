# WeaviateClient

WeaviateClient là một wrapper class để tương tác với Weaviate vector database. Class này cung cấp các phương thức để quản lý collections, vectorize documents và thực hiện các thao tác CRUD cơ bản.

## Khởi tạo

```python
from src.weaviate.weaviate_client import WeaviateClient

# Khởi tạo client
weaviate_client = WeaviateClient()
```

### Yêu cầu Environment Variables

- `WEAVIATE_HTTP_HOST`: Host của Weaviate HTTP server
- `WEAVIATE_HTTP_PORT`: Port của Weaviate HTTP server
- `WEAVIATE_GRPC_HOST`: Host của Weaviate gRPC server
- `WEAVIATE_GRPC_PORT`: Port của Weaviate gRPC server
- `EMBEDDING_URL`: URL của embedding service

## Phương thức

### `_client()`

Tạo kết nối đến Weaviate server.

**Returns:**
- `weaviate.Client`: Weaviate client instance

### `_ensure_connection()`

Kiểm tra xem Weaviate server có sẵn sàng không.

**Returns:**
- `bool`: True nếu kết nối thành công

**Raises:**
- `Exception`: Nếu Weaviate không sẵn sàng

### `_custom_vectorizer(doc, embed_url=None)`

Vectorize một document sử dụng embedding service tùy chỉnh.

**Args:**
- `doc` (str): Document cần được vectorize
- `embed_url` (str, optional): URL của embedding service. Nếu None, sử dụng giá trị từ environment variable

**Returns:**
- `list[float]`: Vector embedding của document
- `None`: Nếu có lỗi xảy ra

**Examples:**
```python
# Sử dụng embedding URL mặc định
vector = weaviate_client._custom_vectorizer("Hello world")
print(vector)  # [0.1, 0.2, 0.3, ...]

# Sử dụng embedding URL tùy chỉnh
vector = weaviate_client._custom_vectorizer(
    "Hello world",
    "http://localhost:3390/v1/embeddings"
)
```

### `list_collections()`

Liệt kê tất cả collections trong Weaviate.

**Returns:**
- `dict[str]`: Dictionary chứa thông tin các collections
- `None`: Nếu có lỗi xảy ra

**Examples:**
```python
collections = weaviate_client.list_collections()
print(collections)
```

### `create_collection(collection_name, model_name="Qwen3-Embedding-0.6B", distance_metric="cosine")`

Tạo một collection mới trong Weaviate.

**Args:**
- `collection_name` (str): Tên của collection
- `model_name` (str, optional): Tên model embedding. Mặc định là "Qwen3-Embedding-0.6B"
- `distance_metric` (str, optional): Metric đo khoảng cách. Có thể là "cosine" hoặc "dot". Mặc định là "cosine"

**Returns:**
- `bool`: True nếu tạo thành công
- `None`: Nếu có lỗi xảy ra

**Examples:**
```python
# Tạo collection với cấu hình mặc định
success = weaviate_client.create_collection("my_documents")

# Tạo collection với cấu hình tùy chỉnh
success = weaviate_client.create_collection(
    collection_name="custom_docs",
    model_name="custom-model",
    distance_metric="dot"
)
```

### `delete_collection(collection_name)`

Xóa một collection khỏi Weaviate.

**Args:**
- `collection_name` (str): Tên collection cần xóa

**Returns:**
- `bool`: True nếu xóa thành công
- `None`: Nếu có lỗi xảy ra

**Examples:**
```python
success = weaviate_client.delete_collection("my_documents")
```

### `delete_object_in_collection(collection_name, where)`

Xóa các objects trong collection theo điều kiện.

**Args:**
- `collection_name` (str): Tên collection
- `where` (dict): Điều kiện để xóa objects

**Returns:**
- `bool`: True nếu xóa thành công
- `None`: Nếu có lỗi xảy ra

**Examples:**
```python
# Xóa objects theo điều kiện
where_condition = {
    "path": ["title"],
    "operator": "Equal",
    "valueText": "Document to delete"
}
success = weaviate_client.delete_object_in_collection("my_documents", where_condition)
```

## Lưu ý

- Tất cả các phương thức đều kiểm tra kết nối trước khi thực hiện thao tác
- Phương thức `_custom_vectorizer` là private method, chỉ nên sử dụng nội bộ
- Khi tạo collection, nếu collection đã tồn tại, phương thức sẽ trả về None
- Logging được thực hiện thông qua `src.utils.logger.Logger`

## Dependencies

- `weaviate`: Weaviate Python client
- `requests`: Để gọi embedding service
- `os`: Để đọc environment variables
- `src.utils.logger`: Custom logger module