import argparse
import json
from datetime import datetime
from pathlib import Path

import requests

from analyser import analyse
from html_parser import parse_html


_CURRENT_DIR = Path(__file__).parent


def save_to_file(most_used_words):
    filename = _CURRENT_DIR / str(datetime.now())
    with open(filename, "w") as f:
        json.dump([i for i in most_used_words], f, indent=4)


def main(url):
    response = requests.get(url)
    response.raise_for_status()

    text = parse_html(str(response.text)).get_text()

    stats = analyse(text)
    most_used_words = stats.get_most_used_words(10)

    print(
        f"Most used words on {url} are:\n\t"
        + "\n\t".join(f"{w}: {c}" for w, c in most_used_words)
    )

    save_to_file(most_used_words)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args()

    main(args.url)
