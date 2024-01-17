from unittest import TestCase

from .analyse import (
    AnalyseResult,
    remove_non_word_characters,
    divide_text_into_words,
    count_words_occurrences,
)


class TextAnalysisTestCase(TestCase):
    def test_removing_non_word_characters(self):
        output = remove_non_word_characters("Thi$ i$ just @ s@mp!3 te><t!")
        self.assertEqual(output, "Thi i just s mp te t")

    def test_divide_text_to_words(self):
        output = divide_text_into_words("This is just a simple test")
        self.assertEqual(output, ["This", "is", "just", "a", "simple", "test"])

    def test_count_words_occurrences(self):
        input_ = [
            "This",
            "test",
            "is",
            "just",
            "a",
            "simple",
            "test",
        ]
        output = count_words_occurrences(input_)
        self.assertEqual(len(input_) - 1, len(output))
        for word in input_:
            if word == "test":
                self.assertEqual(output[word], 2)
            else:
                self.assertEqual(output[word.lower()], 1, msg=f"Error for word: {word}")

    def test_get_most_frequent_words(self):
        input_ = {
            "a": 11,
            "b": 10,
            "c": 9,
            "d": 9,
            "e": 8,
            "f": 7,
            "g": 6,
            "h": 5,
            "i": 4,
            "j": 3,
            "k": 2,
            "l": 1,
        }
        analyse = AnalyseResult(input_)
        analyse.get_most_used_words(10)
