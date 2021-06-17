import sys
from collections import Counter

from preprocess import get_suffixes, remove_punctuation, process_word_suffix

SUFFIXES = get_suffixes()


def process_word(word):
    word = remove_punctuation(word)
    word_suffixes = process_word_suffix(SUFFIXES, word)
    if not word_suffixes:
        return ''
    return word_suffixes[0]


def process_file(filename):
    c = Counter()
    with open(filename) as f:
        # The first line is just the url, omit it
        f.readline()
        words = f.read().split()
        processed = [pw for word in words if (pw := process_word(word))]
        c.update(processed)
    return c


def main():
    c = Counter()
    for fname in sys.stdin:
        c.update(process_file(fname.strip()))

    for k, v in c.items():
        print(f'{k},{v}')


if __name__ == '__main__':
    main()
