import json
import string
import re


class TextCleaner:
    """
    Basic text preprocessing
    """

    def clean_text(self, text):
        output = self._remove_html(text)
        # output = self._remove_punctuation(output)
        # output = self._remove_non_english_alphabet(output)
        # output = self._to_lowercase(output)
        return " ".join(output.split())

    def _remove_html(self, text: str) -> str:
        return re.sub("<.*?>", " ", text)

    def _remove_punctuation(self, text: str) -> str:
        return text.translate(str.maketrans(' ', ' ', string.punctuation))

    def _remove_non_english_alphabet(self, text: str) -> str:
        return re.sub("[^a-zA-Z]", " ", text)

    def _to_lowercase(self, text: str) -> str:
        return text.lower()
    

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)