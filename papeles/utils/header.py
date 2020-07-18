from typing import List


def clean_word(w: str) -> str:
    """
    Remove specific characters from word in a paper header
    """
    return ''.join([c for c in w if c not in ['.', ',', ':', '´', '*', '∗', '†',
                                              '‡', '¨', '`', '§', '⇤', '£', '0',
                                              '1', '2', '3', '4', '5', '6']])


def match_keywords(line) -> List[str]:
    """
    Match keywords strategy for a paper header
    """
    return [clean_word(w) for w in line.lower().split(' ')]
