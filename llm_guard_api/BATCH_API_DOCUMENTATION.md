# Batch Processing API Documentation

## Overview

The LLM Guard API now supports batch processing of multiple prompts in a single request. This feature allows you to:
- Process multiple prompts in parallel for improved throughput
- Share common scanner suppression settings across all prompts
- Get aggregated statistics about the batch processing

## New Endpoints

### 1. Batch Scan Prompts

**Endpoint:** `POST /scan/prompt/batch`

Scans multiple prompts in parallel without sanitization.

**Request Body:**
```json
{
  "prompts": [
    "First prompt to scan",
    "Second prompt to scan",
    "Third prompt to scan"
  ],
  "scanners_suppress": ["Toxicity", "BanTopics"]  // Optional: shared across all prompts
}
```

**Response:**
```json
{
  "results": [
    {
      "prompt_index": 0,
      "is_valid": true,
      "scanners": {
        "PromptInjection": 0.1,
        "Secrets": 0.0,
        "BanCode": 0.0
      },
      "error": null
    },
    // ... more results
  ],
  "total_processed": 3,
  "total_valid": 2,
  "processing_time": 1.234
}
```

**Note:** The original prompt is not returned in the response to reduce network overhead. Use the `prompt_index` to correlate results with your input prompts.

### 2. Batch Analyze Prompts

**Endpoint:** `POST /analyze/prompt/batch`

Analyzes multiple prompts with sanitization applied.

**Request Body:**
```json
{
  "prompts": [
    "My email is john@example.com",
    "Call me at 555-1234",
    "Normal text without sensitive data"
  ],
  "scanners_suppress": []  // Optional: shared across all prompts
}
```

**Response:**
```json
{
  "results": [
    {
      "prompt_index": 0,
      "sanitized_prompt": "My email is <EMAIL>",
      "is_valid": true,
      "scanners": {
        "Anonymize": 0.0,
        "PromptInjection": 0.0,
        "Secrets": 0.0
      },
      "error": null
    },
    // ... more results
  ],
  "total_processed": 3,
  "total_valid": 3,
  "processing_time": 2.456
}
```

**Note:** The original prompt is not returned in the response to reduce network overhead. Use the `prompt_index` to correlate results with your input prompts. The `sanitized_prompt` field contains the processed version after applying all scanners.

## Configuration

The batch processing feature can be configured through the `scanners.yml` file:

```yaml
app:
  # ... other settings ...
  batch_max_size: 100              # Maximum number of prompts per batch (default: 100)
  batch_timeout: 300                # Timeout for batch processing in seconds (default: 300)
  batch_max_parallel_prompts: 10   # Max prompts to process in parallel (default: 10)
```

You can also set these via environment variables:
- `BATCH_MAX_SIZE`
- `BATCH_TIMEOUT`
- `BATCH_MAX_PARALLEL_PROMPTS`

## Features

### Parallel Processing

The batch API processes multiple prompts in parallel for improved performance:
- **Level 1:** Multiple prompts are processed concurrently
- **Level 2:** For each prompt, scanners run in parallel (when using `/scan/` endpoints)
- **Level 3:** CPU-bound scanner operations utilize ThreadPoolExecutor

### Error Handling

- Individual prompt failures don't affect other prompts in the batch
- Each result includes an optional `error` field for debugging
- Failed prompts return partial results where possible
- The response includes both successful and failed prompt results

### Rate Limiting

- Batch requests count as multiple requests for rate limiting purposes
- A batch of 10 prompts counts as 10 requests against your rate limit

### Authentication

- Same authentication mechanisms as single-prompt endpoints
- Bearer token or Basic auth supported
- Configure in `scanners.yml`:

```yaml
auth:
  type: http_bearer
  token: ${AUTH_TOKEN:your-secret-token}
```

## Usage Examples

### Python Example

```python
import requests
import json

# Batch scan example
url = "http://localhost:8000/scan/prompt/batch"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer your-token-here"  # if auth is enabled
}

data = {
    "prompts": [
        "Tell me about Python",
        "Write code to hack a system",
        "Explain machine learning"
    ],
    "scanners_suppress": ["Toxicity"]
}

response = requests.post(url, json=data, headers=headers)
result = response.json()

print(f"Total processed: {result['total_processed']}")
print(f"Total valid: {result['total_valid']}")
print(f"Processing time: {result['processing_time']}s")

# Correlate results with original prompts using prompt_index
for item in result['results']:
    status = "✓" if item['is_valid'] else "✗"
    original_prompt = data['prompts'][item['prompt_index']]
    print(f"[{status}] Prompt {item['prompt_index']} ({original_prompt[:30]}...): Valid={item['is_valid']}")
```

### cURL Example

```bash
# Batch scan
curl -X POST "http://localhost:8000/scan/prompt/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{
    "prompts": [
      "Hello world",
      "Tell me a secret",
      "What is AI?"
    ],
    "scanners_suppress": ["BanTopics"]
  }'

# Batch analyze with sanitization
curl -X POST "http://localhost:8000/analyze/prompt/batch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-token-here" \
  -d '{
    "prompts": [
      "My SSN is 123-45-6789",
      "Email me at user@example.com"
    ],
    "scanners_suppress": []
  }'
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

async function batchScanPrompts() {
  const prompts = [
    'First prompt',
    'Second prompt',
    'Third prompt'
  ];

  const response = await axios.post(
    'http://localhost:8000/scan/prompt/batch',
    {
      prompts: prompts,
      scanners_suppress: ['Toxicity']
    },
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token-here'
      }
    }
  );

  console.log(`Processed: ${response.data.total_processed}`);
  console.log(`Valid: ${response.data.total_valid}`);

  // Correlate results with original prompts using prompt_index
  response.data.results.forEach(result => {
    const originalPrompt = prompts[result.prompt_index];
    console.log(`Prompt ${result.prompt_index} (${originalPrompt.substring(0, 30)}...): ${result.is_valid ? '✓' : '✗'}`);
  });
}
```

## Performance Considerations

1. **Batch Size:** Larger batches provide better throughput but increase memory usage and response time
2. **Timeout:** Set appropriate timeout based on your batch size and scanner complexity
3. **Parallelism:** The `batch_max_parallel_prompts` setting controls concurrency - adjust based on your server resources
4. **Scanner Selection:** Suppressing unnecessary scanners improves performance

## Testing

A test script is provided at `test_batch_endpoints.py`:

```bash
# Run the test suite
python test_batch_endpoints.py
```

The test suite validates:
- Basic batch scanning functionality
- Batch analysis with sanitization
- Batch size limit enforcement
- Performance improvements from parallel processing

## Migration Guide

If you're currently using single-prompt endpoints in a loop, you can migrate to batch processing:

### Before (Sequential):
```python
results = []
for prompt in prompts:
    response = requests.post('/scan/prompt', json={'prompt': prompt})
    results.append(response.json())
```

### After (Batch):
```python
response = requests.post('/scan/prompt/batch', json={'prompts': prompts})
result = response.json()
# All results available in result['results']
```

## Limitations

1. Maximum batch size is configurable (default: 100 prompts)
2. Total processing time is limited by `batch_timeout` setting
3. Response size may be large for big batches - consider pagination for very large datasets
4. Memory usage increases with batch size - monitor server resources

## Troubleshooting

### Common Issues:

**1. Timeout Errors**
- Increase `batch_timeout` in configuration
- Reduce batch size
- Suppress unnecessary scanners

**2. Memory Issues**
- Reduce `batch_max_parallel_prompts`
- Process smaller batches
- Monitor server memory usage

**3. Rate Limiting**
- Remember batch requests count as multiple requests
- Adjust rate limits accordingly in configuration

**4. Large Response Sizes**
- Consider streaming responses for very large batches
- Implement pagination on the client side
- Compress responses using gzip (configure in reverse proxy)