#!/usr/bin/env python3
"""
Complete vLLM Endpoint Testing Suite
====================================

This script provides comprehensive testing for all vLLM services including:
- vLLM Server (Chat/Completion)
- vLLM Embedding (with integrated Rerank)
- Weaviate Vector Database
- Service connectivity and health checks

Usage:
    python3 test_all_endpoints_complete.py [--quick] [--verbose]
    
Options:
    --quick     Run only basic health checks
    --verbose   Show detailed response data
"""

import requests
import json
import time
import sys
import argparse
from typing import Dict, List, Any, Optional

# Service Configuration
SERVICES = {
    "vllm_server": {
        "base_url": "http://localhost:3310",
        "model": "Qwen/Qwen3-1.7B",
        "description": "🤖 vLLM Server (Chat/Completion)"
    },
    "vllm_embedding": {
        "base_url": "http://localhost:3390", 
        "model": "Qwen/Qwen3-Embedding-0.6B",
        "description": "🔢 vLLM Embedding (with Rerank)"
    },
    "weaviate": {
        "base_url": "http://localhost:3340",
        "description": "🗄️ Weaviate Vector Database"
    },
    "redis": {
        "base_url": "http://localhost:3330",
        "description": "📦 Redis Memory Store"
    }
}

class EndpointTester:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_request(self, url: str, method: str = "GET", payload: Optional[Dict] = None, 
                    timeout: int = 30, description: str = "") -> Dict[str, Any]:
        """Generic HTTP request tester"""
        try:
            headers = {"Content-Type": "application/json"} if payload else {}
            
            if method == "GET":
                response = requests.get(url, timeout=timeout, headers=headers)
            elif method == "POST":
                response = requests.post(url, json=payload, timeout=timeout, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            result = {
                "success": response.status_code in [200, 201, 422],
                "status_code": response.status_code,
                "description": description,
                "url": url,
                "method": method
            }
            
            # Parse response
            try:
                result["response"] = response.json()
            except:
                result["response"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
                
            return result
            
        except Exception as e:
            return {
                "success": False,
                "status_code": 0,
                "description": description,
                "url": url,
                "method": method,
                "error": str(e)
            }
    
    def test_vllm_server(self, quick: bool = False) -> List[Dict]:
        """Test vLLM Server endpoints"""
        self.log("Testing vLLM Server endpoints...")
        base_url = SERVICES["vllm_server"]["base_url"]
        model = SERVICES["vllm_server"]["model"]
        
        tests = [
            # Basic endpoints
            (f"{base_url}/health", "GET", None, "Health Check"),
            (f"{base_url}/version", "GET", None, "Version Info"),
            (f"{base_url}/v1/models", "GET", None, "Models List"),
        ]
        
        if not quick:
            # Advanced tests
            tests.extend([
                (f"{base_url}/ping", "GET", None, "Ping (GET)"),
                (f"{base_url}/ping", "POST", {}, "Ping (POST)"),
                (f"{base_url}/metrics", "GET", None, "Metrics"),
                (f"{base_url}/v1/chat/completions", "POST", {
                    "model": model,
                    "messages": [{"role": "user", "content": "What is 2+2?"}],
                    "max_tokens": 50,
                    "temperature": 0.1
                }, "Chat Completion"),
                (f"{base_url}/v1/completions", "POST", {
                    "model": model,
                    "prompt": "The capital of France is",
                    "max_tokens": 20,
                    "temperature": 0.1
                }, "Text Completion"),
                (f"{base_url}/tokenize", "POST", {
                    "model": model,
                    "text": "Hello world, this is a test."
                }, "Tokenization"),
            ])
        
        results = []
        for url, method, payload, desc in tests:
            result = self.test_request(url, method, payload, description=desc)
            results.append(result)
            
            status = "✅" if result["success"] else "❌"
            self.log(f"  {status} {desc}: {result['status_code']}")
            
            if self.verbose and result["success"] and "completion" in desc.lower():
                response_data = result.get("response", {})
                if isinstance(response_data, dict) and "choices" in response_data:
                    choices = response_data["choices"]
                    if choices:
                        content = choices[0].get("message", {}).get("content") or choices[0].get("text", "")
                        self.log(f"    Response: {content[:100]}...")
        
        return results

    def test_vllm_embedding(self, quick: bool = False) -> List[Dict]:
        """Test vLLM Embedding endpoints (includes rerank)"""
        self.log("Testing vLLM Embedding endpoints...")
        base_url = SERVICES["vllm_embedding"]["base_url"]
        model = SERVICES["vllm_embedding"]["model"]

        tests = [
            # Basic endpoints
            (f"{base_url}/health", "GET", None, "Health Check"),
            (f"{base_url}/v1/models", "GET", None, "Models List"),
            (f"{base_url}/v1/embeddings", "POST", {
                "model": model,
                "input": "This is a test sentence for embedding generation."
            }, "Text Embeddings"),
        ]

        if not quick:
            # Rerank tests
            tests.extend([
                (f"{base_url}/ping", "GET", None, "Ping (GET)"),
                (f"{base_url}/metrics", "GET", None, "Metrics"),
                (f"{base_url}/v1/rerank", "POST", {
                    "model": model,
                    "query": "What is machine learning?",
                    "documents": [
                        "Machine learning is a subset of artificial intelligence.",
                        "Python is a programming language.",
                        "Machine learning algorithms learn from data.",
                        "The weather is nice today."
                    ]
                }, "Rerank Documents"),
                (f"{base_url}/rerank", "POST", {
                    "model": model,
                    "query": "artificial intelligence",
                    "documents": [
                        "AI is transforming industries",
                        "Weather forecast for tomorrow",
                        "Machine learning algorithms"
                    ]
                }, "Rerank (Base Endpoint)"),
            ])

        results = []
        for url, method, payload, desc in tests:
            result = self.test_request(url, method, payload, description=desc)
            results.append(result)

            status = "✅" if result["success"] else "❌"
            self.log(f"  {status} {desc}: {result['status_code']}")

            if self.verbose and result["success"]:
                response_data = result.get("response", {})
                if isinstance(response_data, dict):
                    if "embedding" in desc.lower() and "data" in response_data:
                        embedding = response_data["data"][0].get("embedding", [])
                        self.log(f"    Embedding dimension: {len(embedding)}")
                    elif "rerank" in desc.lower() and "results" in response_data:
                        results_count = len(response_data["results"])
                        top_score = response_data["results"][0].get("relevance_score", 0) if response_data["results"] else 0
                        self.log(f"    Ranked {results_count} documents, top score: {top_score:.4f}")

        return results

    def test_weaviate(self, quick: bool = False) -> List[Dict]:
        """Test Weaviate endpoints"""
        self.log("Testing Weaviate endpoints...")
        base_url = SERVICES["weaviate"]["base_url"]

        tests = [
            (f"{base_url}/v1/meta", "GET", None, "Health Check"),
            (f"{base_url}/v1/schema", "GET", None, "Schema Info"),
        ]

        if not quick:
            tests.extend([
                (f"{base_url}/v1/.well-known/ready", "GET", None, "Ready Check"),
                (f"{base_url}/v1/.well-known/live", "GET", None, "Live Check"),
            ])

        results = []
        for url, method, payload, desc in tests:
            result = self.test_request(url, method, payload, description=desc)
            results.append(result)

            status = "✅" if result["success"] else "❌"
            self.log(f"  {status} {desc}: {result['status_code']}")

            if self.verbose and result["success"]:
                response_data = result.get("response", {})
                if isinstance(response_data, dict):
                    if "meta" in url:
                        version = response_data.get("version", "Unknown")
                        modules = list(response_data.get("modules", {}).keys())
                        self.log(f"    Version: {version}, Modules: {modules}")
                    elif "schema" in url:
                        classes = response_data.get("classes", [])
                        self.log(f"    Classes: {len(classes)}")

        return results

    def test_connectivity(self) -> List[Dict]:
        """Test basic connectivity to all services"""
        self.log("Testing service connectivity...")

        connectivity_tests = [
            ("vLLM Server", "http://localhost:3310/health"),
            ("vLLM Embedding", "http://localhost:3390/health"),
            ("Weaviate", "http://localhost:3340/v1/meta"),
            ("GUI", "http://localhost:3320"),
            ("Redis", "http://localhost:3330"),
            ("Customer Service", "http://localhost:3333"),
        ]

        results = []
        for service_name, url in connectivity_tests:
            try:
                if "redis" in url.lower():
                    # Redis doesn't have HTTP endpoint, test TCP connection
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(5)
                    result_code = sock.connect_ex(('localhost', 3330))
                    sock.close()
                    success = result_code == 0
                    status_code = 200 if success else 0
                else:
                    response = requests.get(url, timeout=10)
                    success = response.status_code == 200
                    status_code = response.status_code

                result = {
                    "success": success,
                    "status_code": status_code,
                    "description": f"{service_name} Connectivity",
                    "url": url
                }
                results.append(result)

                status = "✅" if success else "❌"
                self.log(f"  {status} {service_name}: {'Online' if success else 'Offline'}")

            except Exception as e:
                result = {
                    "success": False,
                    "status_code": 0,
                    "description": f"{service_name} Connectivity",
                    "url": url,
                    "error": str(e)
                }
                results.append(result)
                self.log(f"  ❌ {service_name}: Offline ({str(e)[:50]})")

        return results

    def run_performance_benchmark(self) -> Dict[str, Any]:
        """Run performance benchmark for embedding and rerank"""
        self.log("Running performance benchmark...")

        base_url = SERVICES["vllm_embedding"]["base_url"]
        model = SERVICES["vllm_embedding"]["model"]

        # Embedding benchmark
        embedding_start = time.time()
        embedding_payload = {
            "model": model,
            "input": ["Test sentence " + str(i) for i in range(10)]
        }

        try:
            response = requests.post(f"{base_url}/v1/embeddings",
                                   json=embedding_payload, timeout=60)
            embedding_time = time.time() - embedding_start
            embedding_success = response.status_code == 200
        except:
            embedding_time = 0
            embedding_success = False

        # Rerank benchmark
        rerank_start = time.time()
        rerank_payload = {
            "model": model,
            "query": "machine learning algorithms",
            "documents": [f"Document {i}: This is about ML topic {i}" for i in range(20)]
        }

        try:
            response = requests.post(f"{base_url}/v1/rerank",
                                   json=rerank_payload, timeout=60)
            rerank_time = time.time() - rerank_start
            rerank_success = response.status_code == 200
        except:
            rerank_time = 0
            rerank_success = False

        benchmark_results = {
            "embedding": {
                "success": embedding_success,
                "time": embedding_time,
                "throughput": 10 / embedding_time if embedding_time > 0 else 0
            },
            "rerank": {
                "success": rerank_success,
                "time": rerank_time,
                "throughput": 20 / rerank_time if rerank_time > 0 else 0
            }
        }

        if embedding_success:
            self.log(f"  ✅ Embedding: {embedding_time:.2f}s, {benchmark_results['embedding']['throughput']:.1f} docs/s")
        else:
            self.log(f"  ❌ Embedding benchmark failed")

        if rerank_success:
            self.log(f"  ✅ Rerank: {rerank_time:.2f}s, {benchmark_results['rerank']['throughput']:.1f} docs/s")
        else:
            self.log(f"  ❌ Rerank benchmark failed")

        return benchmark_results

    def generate_report(self, all_results: List[Dict], benchmark_results: Dict = None) -> None:
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE vLLM ENDPOINT TEST REPORT")
        print("="*80)

        # Group results by service
        service_groups = {
            "vLLM Server": [r for r in all_results if "server" in r.get("url", "").lower() or "3310" in r.get("url", "")],
            "vLLM Embedding": [r for r in all_results if "embedding" in r.get("url", "").lower() or "3390" in r.get("url", "")],
            "Weaviate": [r for r in all_results if "weaviate" in r.get("url", "").lower() or "3340" in r.get("url", "")],
            "Connectivity": [r for r in all_results if "Connectivity" in r.get("description", "")]
        }

        total_passed = 0
        total_tests = 0

        for service_name, results in service_groups.items():
            if not results:
                continue

            passed = sum(1 for r in results if r["success"])
            total = len(results)
            total_passed += passed
            total_tests += total

            success_rate = (passed / total * 100) if total > 0 else 0

            print(f"\n{service_name}:")
            print(f"  Tests: {passed}/{total} passed ({success_rate:.1f}%)")

            # Show failed tests
            failed = [r for r in results if not r["success"]]
            if failed:
                print("  Failed tests:")
                for f in failed:
                    error_msg = f.get("error", f"Status {f['status_code']}")
                    print(f"    ❌ {f['description']}: {error_msg}")

            # Show successful tests in verbose mode
            if self.verbose:
                successful = [r for r in results if r["success"]]
                if successful:
                    print("  Successful tests:")
                    for s in successful:
                        print(f"    ✅ {s['description']}: {s['status_code']}")

        # Performance summary
        if benchmark_results:
            print(f"\n🚀 Performance Benchmark:")
            for test_type, results in benchmark_results.items():
                if results["success"]:
                    print(f"  ✅ {test_type.title()}: {results['time']:.2f}s, {results['throughput']:.1f} docs/s")
                else:
                    print(f"  ❌ {test_type.title()}: Failed")

        # Overall summary
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_tests - total_passed}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")

        if total_passed == total_tests:
            print("\n🎉 ALL TESTS PASSED! Your vLLM deployment is fully functional!")
        elif overall_success_rate >= 80:
            print("\n✅ Most tests passed! Your deployment is mostly working.")
        else:
            print("\n⚠️  Many tests failed. Please check your service configuration.")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if total_passed == total_tests:
            print("   - Your deployment is ready for production use")
            print("   - Consider setting up monitoring for continued health checks")
        else:
            print("   - Check failed services and their logs")
            print("   - Ensure all containers are running: docker-compose ps")
            print("   - Check network connectivity between services")

    def run_all_tests(self, quick: bool = False) -> None:
        """Run all tests and generate report"""
        start_time = time.time()

        print("🚀 Starting Comprehensive vLLM Endpoint Testing")
        print("="*60)

        all_results = []

        try:
            # Test each service
            all_results.extend(self.test_connectivity())
            all_results.extend(self.test_vllm_server(quick))
            all_results.extend(self.test_vllm_embedding(quick))
            all_results.extend(self.test_weaviate(quick))

            # Run benchmark if not quick mode
            benchmark_results = None
            if not quick:
                benchmark_results = self.run_performance_benchmark()

            # Generate report
            self.generate_report(all_results, benchmark_results)

            # Execution time
            total_time = time.time() - start_time
            print(f"\n⏱️  Total execution time: {total_time:.2f} seconds")

            # Exit code
            failed_tests = sum(1 for r in all_results if not r["success"])
            sys.exit(0 if failed_tests == 0 else 1)

        except KeyboardInterrupt:
            print("\n\n⏹️  Testing interrupted by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Testing failed with error: {e}")
            sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Comprehensive vLLM Endpoint Testing")
    parser.add_argument("--quick", action="store_true", help="Run only basic health checks")
    parser.add_argument("--verbose", action="store_true", help="Show detailed response data")

    args = parser.parse_args()

    tester = EndpointTester(verbose=args.verbose)
    tester.run_all_tests(quick=args.quick)

if __name__ == "__main__":
    main()
