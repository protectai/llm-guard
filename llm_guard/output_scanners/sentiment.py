from llm_guard.input_scanners.sentiment import Sentiment as InputSentiment, _lexicon

from .base import Scanner


class Sentiment(Scanner):
    """
    A sentiment scanner based on the NLTK's SentimentIntensityAnalyzer. It is used to detect if a model output
    has a sentiment score lower than the threshold, indicating a negative sentiment.
    """

    def __init__(self, *, threshold: float = -0.1, lexicon: str = _lexicon) -> None:
        """
        Initializes Sentiment with a threshold and a chosen lexicon.

        Parameters:
           threshold (float): Threshold for the sentiment score (from -1 to 1). Default is -0.1.
           lexicon (str): Lexicon for the SentimentIntensityAnalyzer. Default is 'vader_lexicon'.

        Raises:
           None.
        """

        self._scanner = InputSentiment(threshold=threshold, lexicon=lexicon)

    def scan(self, prompt: str, output: str) -> tuple[str, bool, float]:
        return self._scanner.scan(output)
