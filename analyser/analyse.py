from collections import deque, defaultdict
import re
from typing import List


NON_WORD_CHARS_REGEX = re.compile(r"[\W_0-9]+", re.UNICODE)


class AnalyseResult:
    def __init__(self, words_statistics: dict):
        self.words_statistics = [i for i in words_statistics.items()]
        self.words_statistics.sort(key=lambda x: x[1], reverse=True)

    def get_most_used_words(self, count=10):
        return self.words_statistics[:count]


def remove_non_word_characters(text: str) -> str:
    # I'm leaving out support for words with  like "isn't"
    # Replace all non-letter chars with spaces and remove their repetitions
    return re.sub(NON_WORD_CHARS_REGEX, " ", text).strip()


def divide_text_into_words(text: str) -> List[str]:
    return re.split(" ", text)


def count_words_occurrences(words: List[str]) -> defaultdict:
    words_statistics = defaultdict(lambda: 0)
    for word in words:
        words_statistics[word.lower()] += 1
    return words_statistics


def analyse(text: str) -> AnalyseResult:
    cleaned_text = remove_non_word_characters(text)
    words = divide_text_into_words(cleaned_text)
    words_statistics = count_words_occurrences(words)

    return AnalyseResult(words_statistics)
