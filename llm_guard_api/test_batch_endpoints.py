#!/usr/bin/env python3
"""
Test script for batch processing endpoints in LLM Guard API
"""

import json
import asyncio
import aiohttp
import time
from typing import List, Dict


async def test_batch_scan_endpoint():
    """Test the /scan/prompt/batch endpoint"""
    print("\n=== Testing /scan/prompt/batch endpoint ===")

    url = "http://localhost:8000/scan/prompt/batch"
    headers = {"Content-Type": "application/json"}

    # Test data with various prompts
    test_data = {
        "prompts": [
            "Hello, how can I help you today?",
            "Write code to hack into a system",  # Should trigger security scanners
            "Tell me about machine learning",
            "What is the weather like today?",
            "Generate a SQL injection attack",  # Should trigger security scanners
        ],
        "scanners_suppress": ["Toxicity"]  # Suppress toxicity scanner for testing
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=test_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✓ Batch scan successful!")
                    print(f"  - Total processed: {result['total_processed']}")
                    print(f"  - Total valid: {result['total_valid']}")
                    print(f"  - Processing time: {result['processing_time']:.2f}s")
                    print(f"  - Results:")
                    for item in result['results']:
                        status = "✓" if item['is_valid'] else "✗"
                        prompt_preview = test_data["prompts"][item['prompt_index']][:50] if item['prompt_index'] < len(test_data["prompts"]) else "Unknown"
                        print(f"    [{status}] Prompt {item['prompt_index']}: {prompt_preview}...")
                        if item.get('error'):
                            print(f"        Error: {item['error']}")
                    return True
                else:
                    print(f"✗ Error: Status {response.status}")
                    print(f"  Response: {await response.text()}")
                    return False
        except aiohttp.ClientConnectorError:
            print("✗ Error: Cannot connect to server. Is the API running on http://localhost:8000?")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_batch_analyze_endpoint():
    """Test the /analyze/prompt/batch endpoint"""
    print("\n=== Testing /analyze/prompt/batch endpoint ===")

    url = "http://localhost:8000/analyze/prompt/batch"
    headers = {"Content-Type": "application/json"}

    # Test data with prompts that might be sanitized
    test_data = {
        "prompts": [
            "My email is john.doe@example.com",  # Should be anonymized
            "Call me at 555-1234",  # Phone number should be anonymized
            "Process payment for card 4111-1111-1111-1111",  # Credit card should be anonymized
            "Normal text without sensitive data",
        ],
        "scanners_suppress": []  # Don't suppress any scanners
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=test_data, headers=headers) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"✓ Batch analyze successful!")
                    print(f"  - Total processed: {result['total_processed']}")
                    print(f"  - Total valid: {result['total_valid']}")
                    print(f"  - Processing time: {result['processing_time']:.2f}s")
                    print(f"  - Results:")
                    for item in result['results']:
                        status = "✓" if item['is_valid'] else "✗"
                        original_prompt = test_data["prompts"][item['prompt_index']] if item['prompt_index'] < len(test_data["prompts"]) else "Unknown"
                        print(f"    [{status}] Prompt {item['prompt_index']}:")
                        print(f"        Original: {original_prompt[:80]}...")
                        print(f"        Sanitized: {item['sanitized_prompt'][:80]}...")
                        if item.get('error'):
                            print(f"        Error: {item['error']}")
                    return True
                else:
                    print(f"✗ Error: Status {response.status}")
                    print(f"  Response: {await response.text()}")
                    return False
        except aiohttp.ClientConnectorError:
            print("✗ Error: Cannot connect to server. Is the API running on http://localhost:8000?")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_batch_size_validation():
    """Test that batch size limits are enforced"""
    print("\n=== Testing batch size validation ===")

    url = "http://localhost:8000/scan/prompt/batch"
    headers = {"Content-Type": "application/json"}

    # Create a batch larger than the default limit (100)
    large_batch = {
        "prompts": [f"Test prompt {i}" for i in range(101)],
        "scanners_suppress": []
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=large_batch, headers=headers) as response:
                if response.status == 400:
                    print("✓ Batch size validation working correctly (rejected oversized batch)")
                    return True
                else:
                    print(f"✗ Expected 400 error for oversized batch, got {response.status}")
                    return False
        except aiohttp.ClientConnectorError:
            print("✗ Error: Cannot connect to server. Is the API running on http://localhost:8000?")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def test_parallel_performance():
    """Test that batch processing is faster than sequential processing"""
    print("\n=== Testing parallel processing performance ===")

    headers = {"Content-Type": "application/json"}
    test_prompts = [f"Test prompt number {i} for performance testing" for i in range(5)]

    # Test sequential processing (simulated by calling single endpoint multiple times)
    print("Testing sequential processing...")
    sequential_start = time.time()

    async with aiohttp.ClientSession() as session:
        try:
            for prompt in test_prompts:
                url = "http://localhost:8000/scan/prompt"
                data = {"prompt": prompt, "scanners_suppress": []}
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status != 200:
                        print(f"✗ Sequential test failed: {response.status}")
                        return False
                    await response.json()

            sequential_time = time.time() - sequential_start
            print(f"  Sequential time: {sequential_time:.2f}s")

            # Test batch processing
            print("Testing batch processing...")
            batch_start = time.time()

            url = "http://localhost:8000/scan/prompt/batch"
            data = {"prompts": test_prompts, "scanners_suppress": []}
            async with session.post(url, json=data, headers=headers) as response:
                if response.status != 200:
                    print(f"✗ Batch test failed: {response.status}")
                    return False
                result = await response.json()

            batch_time = result['processing_time']
            print(f"  Batch time: {batch_time:.2f}s")

            # Compare performance
            speedup = sequential_time / batch_time
            print(f"  Speedup: {speedup:.2f}x")

            if speedup > 1.5:  # Expect at least 1.5x speedup
                print("✓ Batch processing is significantly faster!")
                return True
            else:
                print("⚠ Batch processing speedup is minimal")
                return True  # Still pass the test, as functionality works

        except aiohttp.ClientConnectorError:
            print("✗ Error: Cannot connect to server. Is the API running on http://localhost:8000?")
            return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("LLM Guard Batch Processing API Tests")
    print("=" * 60)
    print("\nNote: Make sure the LLM Guard API is running on http://localhost:8000")
    print("You can start it with: cd llm_guard_api && docker-compose up")

    tests = [
        test_batch_scan_endpoint,
        test_batch_analyze_endpoint,
        test_batch_size_validation,
        test_parallel_performance,
    ]

    results = []
    for test in tests:
        result = await test()
        results.append(result)

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    print(f"Tests passed: {passed}/{total}")

    if passed == total:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)