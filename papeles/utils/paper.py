from typing import Iterable, List

from papeles.utils.text import keep_word


def flatten(paper: List[List[str]]) -> Iterable[str]:
    """
    Receives a paper structure (paragraph -> lines) and returns an iterable of lines
    """
    for paragraph in paper:
        for line in paragraph:
            yield line


def get_sentences(sentences: List[str]) -> List[str]:
    """
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


def get_abstract(sentences: List[str]) -> List[str]:
    """
    Extract abstract from paper (anything between "abstract" and "introduction")
    """
    abstract = []
    include = False
    for s in sentences:
        s = s.strip()
        if s.lower() == 'abstract':
            include = True
            continue
        if s.lower() == 'introduction' or s.split(' ')[-1].lower() == 'introduction':  # TODO: refactor
            include = False
        if len(s.split(' ')) == 1:
            continue
        if include:
            for t in s.split(' '):
                if keep_word(t):
                    abstract.append(t)
    sentences = []
    s = ''
    for c in ' '.join(abstract):
        if c not in '.!?':
            s += c
        else:
            s += c
            sentences.append(s.strip())
            s = ''
    return sentences


def get_references(sentences: List[str]) -> List[str]:
    """
    TODO:
     - get references structure (title, authors, etc.)
    """
    pass
