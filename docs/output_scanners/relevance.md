# Relevance Scanner

It is designed to ensure that the output of a language model stays pertinent and aligned with the provided input prompt. By comparing the similarity between the prompt and the output, the scanner offers a measure of confidence that the response from the model is contextually relevant.

## How it works

The scanner harnesses the power of `SentenceTransformer`, specifically the [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) model. It works as follows:

- **Encoding**: Both the prompt and the model's output are transformed into vector embeddings using the `SentenceTransformer`.
- **Cosine Similarity**: The cosine similarity between the vector embeddings of the prompt and the output is computed. This value represents the degree of similarity between the two, ranging between -1 and 1, where 1 indicates maximum similarity.
- **Relevance Determination**: If the computed cosine similarity is below a predefined threshold, the output is deemed not relevant to the initial prompt.

### Example

- **Prompt**: What is the primary function of the mitochondria in a cell?
- **Output**: The Eiffel Tower is a renowned landmark in Paris, France
- **Valid**: False

## Usage

```python
from llm_guard.output_scanners import Relevance

scanner = Relevance(threshold=0)
sanitized_output, is_valid, risk_score = scanner.scan(prompt, model_output)
```
