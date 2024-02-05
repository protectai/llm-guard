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

## Enabling Low CPU/Memory Usage

When available, the transformers_kwargs parameter can be configured to minimize CPU and memory usage:

```python
scanner = Code(languages=["PHP"], transformers_kwargs={"low_cpu_mem_usage": True})
```

For an in-depth understanding of this feature and its impact on large model handling, refer to the detailed [Large Model Loading Documentation](https://huggingface.co/docs/transformers/main_classes/model#large-model-loading).

## Use smaller models

For certain scanners, smaller model variants are available. These models are designed for enhanced performance, offering reduced latency without significantly compromising accuracy or effectiveness.
