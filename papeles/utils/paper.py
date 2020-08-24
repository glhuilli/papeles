from typing import Iterable, List

from papeles.utils.text import keep_word
from papeles.types import ACM_TYPE


def flatten(paper: List[List[str]]) -> Iterable[str]:
    """
    Receives a paper structure (paragraph -> lines) and returns an iterable of lines
    """
    for paragraph in paper:
        for line in paragraph:
            yield line


def get_sentences(sentences: List[str]) -> List[str]:
    """
    Given the nature of the input is very messy and unreliable (from PDF parser), I decided not to use
    a more sophisticated package for this (e.g. SpaCy) and build the sentences "manually".

    1. tokenize by simple space
    2. keep any word with alphanumeric + stops (.!?)
    3. concatenate all sentences
    4. create new sentences based in stops kept from step 2
    5. exclude anything before the abstract
    6. exclude anything after the references or acknowledgements
    7. skip sentences with length 1

    FIXME: Improve speed of this method as it's painfully slow at this moment.
    """
    include = False
    full_paper = []
    for s in sentences:
        s = s.strip()
        if s.lower() == 'introduction' or s.split(' ')[-1].lower() == 'introduction':
            include = True
            continue
        if s.lower() == 'references' or s.lower() == 'acknowledgments':
            include = False
        if len(s.split(' ')) == 1:
            continue
        if include:
            for t in s.split(' '):
                if keep_word(t):
                    full_paper.append(t)
    sentences = []
    s = ''
    for c in ' '.join(full_paper):
        if c not in '.!?':
            s += c
        else:
            s += c
            sentences.append(s.strip())
            s = ''
    return sentences


def get_header(sentences: List[str]) -> List[str]:
    """
    Header is defined as anything that comes before the abstract
    """
    header = []
    for s in sentences:
        s = s.strip()
        if s.lower() == 'abstract':
            break
        header.append(s)
    return header


def get_abstract_sentences(sentences: List[str], document_type: str = None) -> List[str]:
    """
    Extract abstract from paper (anything between "abstract" and "introduction")

    Given the nature of the input is very messy and unreliable (from PDF parser), I decided not to use
    a more sophisticated package for this (e.g. SpaCy) and build the sentences "manually".

    1. tokenize by simple space
    2. keep any word with alphanumeric + stops (.!?)
    3. concatenate all sentences
    4. create new sentences based in stops kept from step 2
    5. include anything after "abstract"
    6. exclude anything before "introduction"
        6.1. FIXME: Depending on the type of document, there might be a better rule for this (e.g. ACM)
    7. skip sentences with length 1
    """
    abstract = []
    include = False
    for s in sentences:
        s = s.strip()
        if s.lower() == 'abstract':
            include = True
            continue
        if _verify_abstract_stop(s, document_type):  # TODO: refactor
            include = False
        if len(s.split(' ')) == 1:
            continue
        if include:
            for t in s.split(' '):
                if keep_word(t):
                    abstract.append(t)
    return _build_sentences(abstract)


def get_references(sentences: List[str]) -> List[str]:
    """
    TODO:
     - get references structure (title, authors, etc.)
    """
    pass


def _verify_abstract_stop(sentence: str, document_type: str = None) -> bool:
    main_rule = sentence.lower() == 'introduction' or sentence.split(' ')[-1].lower() == 'introduction'
    if document_type == ACM_TYPE:
        return 'ccs concepts' in sentence.lower() or sentence.lower() == 'keywords' or main_rule
    return main_rule


def _build_sentences(lines: List[str]) -> List[str]:
    sentences = []
    s = ''
    for c in ' '.join(lines):
        if c not in '.!?':
            s += c
        else:
            s += c
            sentences.append(s.strip())
            s = ''
    return sentences
