import re
from typing import List


def fix_text(text: str) -> str:
    """
    TODO: fix input string encoding issues
    """
    return text


def ngrams(string: str, n: int = 3) -> List[str]:
    """
    Generate n-grams of length n from an input string.
    """
    string = fix_text(string)  # fix text encoding issues
    string = string.encode("ascii", errors="ignore").decode()  # remove non ascii chars
    string = string.lower()  # make lower case
    chars_to_remove = [")", "(", ".", "|", "[", "]", "{", "}", "'"]
    rx = '[' + re.escape(''.join(chars_to_remove)) + ']'
    string = re.sub(rx, '', string)  # remove the list of chars defined above
    string = string.replace('&', 'and')
    string = string.replace(',', ' ')
    string = string.replace('-', ' ')
    string = string.title()  # normalise case - capital at start of each word
    string = re.sub(' +', ' ',
                    string).strip()  # get rid of multiple spaces and replace with a single space
    string = ' ' + string + ' '  # pad names for ngrams...
    string = re.sub(r'[,-./]|\sBD', r'', string)
    ngrams_output = zip(*[string[i:] for i in range(n)])
    return [''.join(ngram) for ngram in ngrams_output]


def keep_word(token: str) -> bool:
    """
    Decide whether a token should be kept by
        1. removing some characters
        2. checking if the remaining characters are alphanumeric
    """
    return ''.join([x for x in token if x not in '.!?']).isalnum()
