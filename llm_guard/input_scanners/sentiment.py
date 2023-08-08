import logging

import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

from .base import Scanner

_lexicon = "vader_lexicon"

log = logging.getLogger(__name__)


class Sentiment(Scanner):
    """
    A sentiment scanner based on the NLTK's SentimentIntensityAnalyzer. It is used to detect if a prompt
    has a sentiment score lower than the threshold, indicating a negative sentiment.
    """

    def __init__(self, threshold: float = -0.1, lexicon: str = _lexicon):
        """
        Initializes Sentiment with a threshold and a chosen lexicon.

        Parameters:
           threshold (float): Threshold for the sentiment score (from -1 to 1). Default is -0.1.
           lexicon (str): Lexicon for the SentimentIntensityAnalyzer. Default is 'vader_lexicon'.

        Raises:
           None.
        """

        nltk.download(lexicon)
        self._sentiment_analyzer = SentimentIntensityAnalyzer()
        self._threshold = threshold

    def scan(self, prompt: str) -> (str, bool):
        sentiment_score = self._sentiment_analyzer.polarity_scores(prompt)
        if sentiment_score["compound"] > self._threshold:
            log.debug(f"Sentiment score: {sentiment_score}, threshold: {self._threshold}")

            return prompt, True

        log.warning(
            f"Sentiment score is over threshold: {sentiment_score}, threshold: {self._threshold}"
        )

        return prompt, False
