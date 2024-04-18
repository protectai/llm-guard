# Optimization Strategies

## ONNX Runtime

ONNX (Open Neural Network Exchange) provides a high-performance inference engine for machine learning models, allowing for faster and more efficient model execution. If an ONNX version of a model is available, it can serve as a substantial optimization for the scanner.

To leverage ONNX Runtime, you must first install the appropriate package:

```sh
pip install llm-guard[onnxruntime] # for CPU instances
pip install llm-guard[onnxruntime-gpu] # for GPU instances
```

Activate ONNX by initializing your scanner with the use_onnx parameter set to True:

```python
scanner = Code(languages=["PHP"], use_onnx=True)
```

In case you have issues installing the ONNX Runtime package, you can check the [official documentation](https://onnxruntime.ai/docs/install/).

## ONNX Runtime with Quantization

Although not built-in in the library, you can use quantized or optimized versions of the models.
However, that doesn't always lead to better latency but can reduce the model size.

## Enabling Low CPU/Memory Usage

To minimize CPU and memory usage:

```python
from llm_guard.input_scanners.code import Code, DEFAULT_MODEL

DEFAULT_MODEL.kwargs["low_cpu_mem_usage"] = True
scanner = Code(languages=["PHP"], model=DEFAULT_MODEL)
```

For an in-depth understanding of this feature and its impact on large model handling, refer to the detailed [Large Model Loading Documentation](https://huggingface.co/docs/transformers/main_classes/model#large-model-loading).

Alternatively, quantization can be used to reduce the model size and memory usage.

## Use smaller models

For certain scanners, smaller model variants are available e.g. distilbert, bert-small, bert-tiny versions.
These models are designed for enhanced performance, offering reduced latency without significantly compromising accuracy or effectiveness.

## PyTorch hacks

To speed up warm compile times:

```python
import torch
torch.set_float32_matmul_precision('high')

import torch._inductor.config
torch._inductor.config.fx_graph_cache = True
```

## Streaming mode

To optimize the output scanning, you can analyze the output in chunks. In [OpenAI](./openai.md) guide, we demonstrate how to use LLM Guard to protect OpenAI client with streaming.
