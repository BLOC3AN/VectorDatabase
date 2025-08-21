# vLLM Deployment Guide & Testing Suite

## 📋 Overview

This deployment provides a complete vLLM-based AI infrastructure with the following services:

- **🤖 vLLM Server**: Chat completion and text generation (Qwen3-1.7B)
- **🔢 vLLM Embedding**: Text embeddings and document reranking (Qwen3-Embedding-0.6B)
- **🗄️ Weaviate**: Vector database with vLLM integration
- **📦 Redis**: Memory storage for conversations
- **🖥️ GUI**: Streamlit web interface
- **🎯 Customer Service Agent**: CrewAI-powered service

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- NVIDIA GPU with CUDA support
- Python 3.8+ (for testing)

### 1. Start Services
```bash
cd deployment-vllm
docker-compose up -d
```

### 2. Verify Deployment
```bash
# Quick health check
python3 test_all_endpoints_complete.py --quick

# Full comprehensive test
python3 test_all_endpoints_complete.py --verbose

# Performance benchmark
python3 test_all_endpoints_complete.py
```

## 🔧 Service Configuration

### Port Mapping
| Service | Port | Description |
|---------|------|-------------|
| vLLM Server | 3310 | Chat/Completion API |
| vLLM Embedding | 3390 | Embeddings + Rerank API |
| Weaviate | 3340 | Vector Database |
| GUI | 3320 | Web Interface |
| Redis | 3330 | Memory Store |
| Customer Service | 3333 | Agent API |

### Models Used
- **Chat/Completion**: `Qwen/Qwen3-1.7B`
- **Embeddings/Rerank**: `Qwen/Qwen3-Embedding-0.6B`

## 📡 API Endpoints

### vLLM Server (Port 3310)

#### Chat Completion
```bash
curl -X POST http://localhost:3310/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-1.7B",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ],
    "max_tokens": 100,
    "temperature": 0.7
  }'
```

#### Text Completion
```bash
curl -X POST http://localhost:3310/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-1.7B",
    "prompt": "The future of AI is",
    "max_tokens": 50,
    "temperature": 0.7
  }'
```

#### Health Check
```bash
curl http://localhost:3310/health
```

### vLLM Embedding (Port 3390)

#### Generate Embeddings
```bash
curl -X POST http://localhost:3390/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-Embedding-0.6B",
    "input": "This is a sample text for embedding"
  }'
```

#### Rerank Documents
```bash
curl -X POST http://localhost:3390/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{
    "model": "Qwen/Qwen3-Embedding-0.6B",
    "query": "machine learning",
    "documents": [
      "Machine learning is a subset of AI",
      "Python is a programming language",
      "Deep learning uses neural networks"
    ]
  }'
```

### Weaviate (Port 3340)

#### Health Check
```bash
curl http://localhost:3340/v1/meta
```

#### Schema Information
```bash
curl http://localhost:3340/v1/schema
```

#### Add Object (with automatic embedding)
```bash
curl -X POST http://localhost:3340/v1/objects \
  -H "Content-Type: application/json" \
  -d '{
    "class": "Document",
    "properties": {
      "title": "Sample Document",
      "content": "This is sample content that will be automatically embedded"
    }
  }'
```

## 🧪 Testing Suite

### Available Test Scripts

1. **Complete Test Suite** (Recommended)
   ```bash
   python3 test_all_endpoints_complete.py
   ```

2. **Quick Health Check**
   ```bash
   python3 test_all_endpoints_complete.py --quick
   ```

3. **Verbose Output**
   ```bash
   python3 test_all_endpoints_complete.py --verbose
   ```

### Test Categories

#### 🔍 Health Checks
- Service availability
- Basic connectivity
- Version information

#### 🚀 Functionality Tests
- Chat completion
- Text completion
- Embedding generation
- Document reranking
- Vector database operations

#### ⚡ Performance Benchmarks
- Embedding throughput
- Rerank performance
- Response times

### Expected Results

```
📊 COMPREHENSIVE vLLM ENDPOINT TEST REPORT
================================================================================

vLLM Server:
  Tests: 8/8 passed (100.0%)

vLLM Embedding:
  Tests: 6/6 passed (100.0%)

Weaviate:
  Tests: 4/4 passed (100.0%)

Connectivity:
  Tests: 6/6 passed (100.0%)

🚀 Performance Benchmark:
  ✅ Embedding: 0.15s, 66.7 docs/s
  ✅ Rerank: 0.06s, 333.3 docs/s

🎯 OVERALL RESULTS:
   Total Tests: 24
   Passed: 24
   Failed: 0
   Success Rate: 100.0%

🎉 ALL TESTS PASSED! Your vLLM deployment is fully functional!
```

## 🔧 Configuration Details

### Docker Compose Services

#### vLLM Server
- **Image**: `vllm/vllm-openai:v0.8.5`
- **GPU**: Full GPU access
- **Memory**: 60% GPU utilization
- **Model**: Qwen/Qwen3-1.7B

#### vLLM Embedding
- **Image**: `vllm/vllm-openai:v0.8.5`
- **GPU**: 20% GPU utilization
- **Model**: Qwen/Qwen3-Embedding-0.6B
- **Features**: Embeddings + Rerank

#### Weaviate
- **Image**: `semitechnologies/weaviate:1.29.1`
- **Module**: text2vec-openai (configured for vLLM)
- **Integration**: Automatic embedding via vLLM

### Environment Variables

```yaml
# Weaviate Configuration
OPENAI_BASEURL: "http://vllm-embedding:8010"
OPENAI_APIKEY: "dummy-key"
DEFAULT_VECTORIZER_MODULE: "text2vec-openai"
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Service Not Starting
```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs [service-name]

# Restart specific service
docker-compose restart [service-name]
```

#### 2. GPU Not Detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

# Verify GPU access in container
docker-compose exec vllm-server nvidia-smi
```

#### 3. Weaviate Integration Issues
```bash
# Test vLLM embedding directly
curl -X POST http://localhost:3390/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen/Qwen3-Embedding-0.6B", "input": "test"}'

# Check Weaviate logs
docker-compose logs vllm-weaviate
```

#### 4. Performance Issues
- Reduce `gpu-memory-utilization` values
- Adjust `max-model-len` parameters
- Monitor GPU memory usage

### Log Locations
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs vllm-server
docker-compose logs vllm-embedding
docker-compose logs vllm-weaviate
```

## 📊 Performance Tuning

### GPU Memory Optimization
```yaml
# In docker-compose.yml
command:
  - --gpu-memory-utilization
  - "0.6"  # Adjust based on available GPU memory
```

### Model Parameters
```yaml
# Increase context length
- --max-model-len
- "32000"

# Parallel processing
- --tensor-parallel-size
- "1"  # Increase for multi-GPU setups
```

## 🔒 Security Considerations

1. **API Keys**: Use proper authentication in production
2. **Network**: Configure firewall rules for exposed ports
3. **Data**: Ensure sensitive data is properly handled
4. **Updates**: Keep Docker images updated

## 📈 Monitoring

### Health Endpoints
- vLLM Server: `http://localhost:3310/health`
- vLLM Embedding: `http://localhost:3390/health`
- Weaviate: `http://localhost:3340/v1/meta`

### Metrics
- vLLM Metrics: `http://localhost:3310/metrics`
- Performance: Use test suite for regular benchmarks

## 🤝 Support

For issues and questions:
1. Check logs: `docker-compose logs`
2. Run test suite: `python3 test_all_endpoints_complete.py`
3. Verify configuration in `docker-compose.yml`
4. Check GPU availability: `nvidia-smi`

---

**Last Updated**: August 2025  
**Version**: 1.0  
**Compatible with**: vLLM v0.8.5, Weaviate v1.29.1
