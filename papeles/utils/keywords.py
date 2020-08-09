from typing import List

from collections import Counter
import math


def count_word(word: str, word_list: List[str]):
    """
    Counts how many times a word is present in a document
    """
    return sum(1 for w in word_list if w == word)


def tf(word: str, word_list: List[str]):
    """
    Frequency of a word in a document normalized by length of document
    """
    return count_word(word, word_list) / len(word_list)


def n_containing(word: str, text_list: List[List[str]]):
    return sum(1 for text in text_list if word in text)


def idf(word: str, text_list: List[List[str]]):
    """
    Inverse document frequency of word in a collection of documents
    """
    return math.log(len(text_list) / (1 + n_containing(word, text_list)))


def tfidf(word: str, text: List[str], text_list: List[List[str]]):
    """
    Computes the TF-IDF value for a word in a particular text, using a collection of
    documents.

    Formula considered in this implementation is the following

        TF-IDF = (word freq in doc) / (len of doc) * log(total docs / (1 + docs with word))
    """
    return tf(word, text) * idf(word, text_list)


def get_keywords(text_list: List[List[str]], top_doc_keywords: int = 20):
    """
    Only using top 20 keywords per document, ranked by TF-IDF.

    Note that text in text_list is a list of words.
    """
    keywords_counter = Counter()
    for text in text_list:
        scores = {word: tfidf(word, text, text_list) for word in text}
        sorted_words = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        keywords_counter.update([x[0] for x in sorted_words[:top_doc_keywords]])
    return keywords_counter
