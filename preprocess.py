import re
from typing import List, Set, Tuple, TypedDict
import string


PUNCTUATIONS = ''.join([x for x in string.punctuation if x != '?']) + '‘‘‘’“…–—\xa0' + string.ascii_letters + string.digits


def remove_punctuation(text: str) -> str:
    transtable = str.maketrans('', '', PUNCTUATIONS)
    return text.translate(transtable)


def clean_word(word: str) -> str:
    """
    for example aakar + ekar and okar look the same but are no the same
    Also replace devnagari numerals by N
    """
    word = word.replace('ाे', 'ो')
    word = word.replace('ाै', 'ाै')
    word = re.sub(r'[१२३४५६७८९०]+', 'N', word)
    return word


def split_sentences(text: str) -> List[str]:
    return re.split('[!।?]', text)
