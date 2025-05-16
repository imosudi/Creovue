

"""
Initialise required NLTK resources.
Run this script once to prepare your environment.
"""

import nltk
from nltk.data import find
import os

# Optional: Force NLTK data path (can be local to your project)
NLTK_DATA_DIR = os.path.join(os.path.dirname(__file__), "nltk_data")
if NLTK_DATA_DIR not in nltk.data.path:
    nltk.data.path.append(NLTK_DATA_DIR)

REQUIRED_CORPORA = ['stopwords']

def download_if_missing(resource):
    try:
        find(f'corpora/{resource}')
        print(f"✓ '{resource}' already downloaded.")
    except LookupError:
        print(f"↓ Downloading '{resource}' to {NLTK_DATA_DIR}...")
        nltk.download(resource, download_dir=NLTK_DATA_DIR)

if __name__ == "__main__":
    for corpus in REQUIRED_CORPORA:
        download_if_missing(corpus)

    print("✅ NLTK setup complete.")

from nltk.corpus import stopwords
print(stopwords.words("english")[:10])

print(stopwords.words("english"))
