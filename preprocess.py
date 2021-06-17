import re
from typing import List, Set, Tuple, TypedDict
import string


PUNCTUATIONS = ''.join([x for x in string.punctuation if x != '?']) + '‘’“…–—\xa0' + string.ascii_letters + string.digits
SUFFIXES_FILE = 'suffixes.txt'

digits = "१२३४५६७८९०"
to_remove = "।?"


class SuffixesMap(TypedDict):
    remove: Set[str]
    split: Set[str]
    exception: Set[str]
    exception_end: Set[str]
    replace: Set[Tuple[str, str]]


def remove_punctuation(text: str) -> str:
    transtable = str.maketrans('', '', PUNCTUATIONS+digits+to_remove)
    return text.translate(transtable)


def get_suffixes() -> SuffixesMap:
    """
    Reads SUFFIXES_FILE and gets suffixes that either need to be removed or
    splitted with the word.
    The file has items in the format: "[r|s] <space> <suffix>" in each line
    where r stands for remove the suffix and s for split the suffix
    """
    suffixes: SuffixesMap = {
        'remove': set(),
        'split': set(),
        'replace': set(),
        'exception': set(),
        'exception_end': set()
    }
    actions = suffixes.keys()

    with open(SUFFIXES_FILE, 'r') as suff_file:
        for line in suff_file.readlines():
            if not line.strip():
                continue
            [action, suffix, *other] = line.split()

            if action not in actions:
                print(f"Invalid action {action}. Ignoring...")
                continue

            if action == 'replace':
                suffixes[action].add((suffix, other[0]))
            else:
                suffixes[action].add(suffix)
    return suffixes


def process_word_suffix(suffixes: SuffixesMap, word: str) -> List[str]:
    """
    Processeses the suffixes like haru, lai, harulai, dekhi, ko, ka, ki, etc.
    Returns a list of words. Because, suffixes like lai, dekhi, etc are splitted
    from the original word
    """
    for src, tgt in suffixes['replace']:
        if word.endswith(src):
            word = re.sub(rf'{src}', tgt, word)
            break

    changes = True
    while changes:
        # Loop until no changes are done
        changes = False

        if word in suffixes['exception']:
            continue

        if any(word.endswith(suff) for suff in suffixes['exception_end']):
            continue

        for suff in suffixes['remove']:
            if word.endswith(suff):
                changes = True
                word = re.sub(rf'{suff}$', '', word)
                break

        for suff in suffixes['split']:
            if word.endswith(suff):
                splitted = word.split(suff)
                subject = suff.join(splitted[:-1])
                # We again need to process the subject because we can have something like:
                #   dal-haru-bata in which case we split bata, but need to process dal-haru
                #   to remove haru
                return [*process_word_suffix(suffixes, subject), suff]
    return [word] if word else []  # Just in case word is empty string
