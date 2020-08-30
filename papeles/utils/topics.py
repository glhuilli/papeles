from typing import List

from gensim import corpora
from gensim import models

from papeles.utils import text as text_utils


class Topics:

    def __init__(self, corpus: List[str], keywords: List[str], n_grams: int = 3, n_topics: int = 100):
        self.keywords = keywords
        self.n_grams = n_grams
        self.n_topics = n_topics
        self.corpus = corpus
        self.topics = self._get_topics()

    @staticmethod
    def _match_doc(doc_n_grams, keywords):
        """
        Very simple strategy for matching keywords to a document

        TODO: this can be refactored into a much robust version.
        """
        return list(set(doc_n_grams).intersection(set(keywords)))

    @staticmethod
    def _extract_topics(model):
        """
        Given a gensim model, extract all topics
        """
        unique_topics = []
        for i in range(0, model.num_topics - 1):
            t = [x[0] for x in model.show_topic(i)]
            if t in unique_topics:
                continue
            unique_topics.append(t)
        final_topics = {}
        for idx, t in enumerate(unique_topics):
            final_topics[f'topic_{idx}'] = t
        return final_topics

    def _get_topics(self):
        """
        Given a corpus and it's set of keywords, get high quality topics.

        As this is extended into new options and use cases, it could be refactored into a class.

        Default is 100 topics with 10 terms per topic.
        """
        text_list = []
        for document in self.corpus:
            new_document = self._match_doc(text_utils.generate_ngram_text(document, self.n_grams), self.keywords)
            if len(new_document) > 1:
                text_list.append(new_document)

        dictionary = corpora.Dictionary(text_list)
        corpus = [dictionary.doc2bow(text) for text in text_list]
        return self._extract_topics(
            models.LdaModel(corpus, id2word=dictionary, num_topics=self.n_topics, decay=0.5, passes=10))

    def predict_topics(self, document: str):
        """
        Given a collection of topics, predict which ones are found in a given document
        """
        n_grams_doc = text_utils.generate_ngram_text(document, self.n_grams)
        predictions = {}
        if len(n_grams_doc) > 0:
            for topic, terms in self.topics.items():
                predictions[topic] = len(set(n_grams_doc).intersection(set(terms)))/len(n_grams_doc)
        return predictions
