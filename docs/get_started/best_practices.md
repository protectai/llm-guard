# Best Practices

## Performance Optimization

1. **Benchmark Analysis**: Before choosing the scanners, it's crucial to understand their performance on different instances. Review the benchmarks for each scanner to make an informed decision based on your specific requirements.

2. **Model Size Trade-off**: Opting for smaller models will expedite processing, reducing latency. However, this comes at the cost of accuracy. We are actively working on providing compact versions with minimal accuracy trade-offs.

3. **Use ONNX Runtime for CPU inference**: [ONNX Runtime](https://onnxruntime.ai/) is a high-performance inference engine for machine learning models. When possible, we recommend using ONNX Runtime for serving the models.

4. **Tune Transformers kwargs**: Transformers have a variety of parameters that can be tuned to optimize performance. For example, `low_cpu_mem_usage`, which helps to [use less memory](https://huggingface.co/docs/transformers/main_classes/model#large-model-loading) by utilizing Accelerate library.

[Read more about optimization strategies](../tutorials/optimization.md)

## Serving Configurations

1. **Fast Failure Mode**: Enable the `fail_fast` mode while serving to ensure early exits, preventing the wait for all scanners to complete, thus optimizing the response time.

2. **Scanner Selection**: Assess the relevance of different scanners for your use-case. Instead of employing all scanners synchronously, which might overwhelm the system, consider using them asynchronously. This approach enhances observability, aiding in precise debugging and performance monitoring.

3. **Request Sampling**: Run slower scanners on a sample of requests to reduce the overall latency. This approach is especially useful when the system is under heavy load.

## Observability and Debugging

1. **Logging and Metrics**: Implement robust logging and metric collection to monitor the system's performance and health.

## Continuous Improvement

1. **Feedback Loops**: Establish feedback loops with your system's users to understand how the library is performing in real-world scenarios, and to gather suggestions for improvements.

2. **Regular Updates and Testing**: Stay updated with the latest versions of `llm-guard`, and ensure thorough testing in a staging environment before rolling out updates in a production setup.
