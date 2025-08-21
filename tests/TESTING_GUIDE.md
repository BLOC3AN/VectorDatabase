# 🧪 vLLM Testing Guide

## Quick Start

### 1. Run Tests
```bash
# Quick health check (recommended for daily use)
./test.sh quick

# Full comprehensive test
./test.sh full

# Detailed verbose output
./test.sh verbose
```

### 2. Alternative Python Usage
```bash
# Direct Python execution
python3 test_all_endpoints_complete.py --quick
python3 test_all_endpoints_complete.py --verbose
python3 test_all_endpoints_complete.py
```

## 📋 Test Categories

### 🔍 Health Checks
- Service availability and connectivity
- Basic endpoint responses
- Version information

### 🚀 Functionality Tests
- **Chat Completion**: Text generation with Qwen3-1.7B
- **Text Completion**: Prompt completion
- **Embeddings**: Vector generation (1024 dimensions)
- **Rerank**: Document ranking and scoring
- **Vector Database**: Weaviate integration

### ⚡ Performance Benchmarks
- **Embedding Throughput**: ~66+ docs/second
- **Rerank Performance**: ~300+ docs/second
- **Response Times**: Sub-second for most operations

## 📊 Expected Results

### ✅ Successful Test Output
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

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. Service Offline
```bash
# Check container status
docker-compose ps

# Restart services
docker-compose restart

# View logs
docker-compose logs [service-name]
```

#### 2. GPU Issues
```bash
# Check GPU availability
nvidia-smi

# Verify GPU access in containers
docker-compose exec vllm-server nvidia-smi
```

#### 3. Port Conflicts
```bash
# Check port usage
netstat -tulpn | grep :3310
netstat -tulpn | grep :3390
netstat -tulpn | grep :3340
```

#### 4. Memory Issues
- Reduce `gpu-memory-utilization` in docker-compose.yml
- Restart services after changes

### Test Failures

#### Embedding Test Fails
```bash
# Test directly
curl -X POST http://localhost:3390/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen/Qwen3-Embedding-0.6B", "input": "test"}'
```

#### Rerank Test Fails
```bash
# Test directly
curl -X POST http://localhost:3390/v1/rerank \
  -H "Content-Type: application/json" \
  -d '{"model": "Qwen/Qwen3-Embedding-0.6B", "query": "test", "documents": ["doc1", "doc2"]}'
```

#### Weaviate Integration Issues
```bash
# Check Weaviate logs
docker-compose logs vllm-weaviate

# Test Weaviate health
curl http://localhost:3340/v1/meta
```

## 📈 Performance Monitoring

### Regular Health Checks
```bash
# Daily quick check
./test.sh quick

# Weekly comprehensive test
./test.sh full

# Performance monitoring
./test.sh verbose
```

### Benchmarking
The test suite includes automatic performance benchmarks:
- **Embedding Generation**: Measures throughput for batch embeddings
- **Document Reranking**: Tests ranking speed for multiple documents
- **Response Times**: Tracks API response latency

### Expected Performance
- **Embedding**: 50-100+ docs/second
- **Rerank**: 200-500+ docs/second
- **Chat**: 1-3 seconds for typical responses
- **Health Checks**: <100ms

## 🎯 Test Customization

### Modify Test Parameters
Edit `test_all_endpoints_complete.py`:

```python
# Adjust timeouts
timeout=30  # seconds

# Change test data size
documents = [f"Document {i}" for i in range(10)]  # 10 docs instead of 20

# Modify models
model = "your-custom-model"
```

### Add Custom Tests
```python
def test_custom_endpoint(self):
    """Add your custom test"""
    result = self.test_request(
        "http://localhost:3310/your-endpoint",
        "POST",
        {"your": "payload"},
        description="Custom Test"
    )
    return [result]
```

## 📝 Test Reports

### Automated Reporting
The test suite generates:
- **Console Output**: Real-time test results
- **Success/Failure Counts**: Per-service statistics
- **Performance Metrics**: Throughput and timing data
- **Recommendations**: Actionable next steps

### Log Analysis
```bash
# Save test output
./test.sh full > test_results.log 2>&1

# Extract only failures
./test.sh full 2>&1 | grep "❌"

# Monitor performance over time
./test.sh verbose | grep "docs/s"
```

## 🔄 Continuous Testing

### Automated Monitoring
```bash
# Add to crontab for hourly checks
0 * * * * cd /path/to/deployment-vllm && ./test.sh quick

# Daily comprehensive test
0 6 * * * cd /path/to/deployment-vllm && ./test.sh full > /var/log/vllm-test.log
```

### CI/CD Integration
```yaml
# Example GitHub Actions
- name: Test vLLM Deployment
  run: |
    cd deployment-vllm
    python3 test_all_endpoints_complete.py --quick
```

---

**💡 Pro Tips:**
- Run `./test.sh quick` after any configuration changes
- Use `./test.sh verbose` for debugging issues
- Monitor performance trends over time
- Set up automated daily health checks

**🆘 Need Help?**
1. Check the main [README.md](README.md) for detailed setup
2. Review Docker logs: `docker-compose logs`
3. Verify GPU access: `nvidia-smi`
4. Test individual endpoints manually with curl
