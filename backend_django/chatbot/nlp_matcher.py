"""
nlp_matcher.py

Same NLP pipeline as the standalone Flask version, adapted to read live data
from the database instead of a static JSON file, and cached in memory so we
don't re-fit TF-IDF on every single chat request.

The cache is invalidated (see admin.py) whenever a FAQ is added, edited,
toggled inactive, or deleted -- so the bot never answers from stale data.
"""

import string

import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SIMILARITY_THRESHOLD = 0.25

_matcher_cache = None  # holds a fitted _FAQMatcher instance, or None


def ensure_nltk_data():
    required = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]
    for path, package in required:
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(package, quiet=True)


class _FAQMatcher:
    """Fitted TF-IDF matcher over the currently active FAQs."""

    def __init__(self, faq_rows):
        ensure_nltk_data()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))
        self.punctuation_table = str.maketrans("", "", string.punctuation)

        # faq_rows: list of dicts {id, question, answer}
        self.faqs = faq_rows
        self.preprocessed_questions = [self._preprocess(f["question"]) for f in self.faqs]

        self.vectorizer = TfidfVectorizer()
        if self.preprocessed_questions:
            self.question_vectors = self.vectorizer.fit_transform(self.preprocessed_questions)
        else:
            self.question_vectors = None

    def _preprocess(self, text):
        text = text.lower().translate(self.punctuation_table)
        tokens = word_tokenize(text)
        cleaned = [
            self.lemmatizer.lemmatize(tok)
            for tok in tokens
            if tok not in self.stop_words and tok.isalpha()
        ]
        return " ".join(cleaned)

    def find_best_match(self, user_query):
        if not self.faqs:
            return {
                "matched": False,
                "answer": "No FAQs are configured yet. Please check back soon.",
                "matched_question": None,
                "score": 0.0,
            }

        cleaned_query = self._preprocess(user_query)
        if not cleaned_query.strip():
            return {
                "matched": False,
                "answer": "Could you rephrase that? I didn't catch a clear question.",
                "matched_question": None,
                "score": 0.0,
            }

        query_vector = self.vectorizer.transform([cleaned_query])
        scores = cosine_similarity(query_vector, self.question_vectors)[0]

        best_index = scores.argmax()
        best_score = float(scores[best_index])

        if best_score < SIMILARITY_THRESHOLD:
            return {
                "matched": False,
                "answer": (
                    "I'm not sure I understand. Could you try rephrasing, "
                    "or ask about orders, shipping, returns, payments, or your account?"
                ),
                "matched_question": None,
                "score": round(best_score, 3),
            }

        matched_faq = self.faqs[best_index]
        return {
            "matched": True,
            "answer": matched_faq["answer"],
            "matched_question": matched_faq["question"],
            "score": round(best_score, 3),
        }


def get_matcher():
    """Return the cached matcher, building it from the DB if needed."""
    global _matcher_cache
    if _matcher_cache is None:
        from .models import FAQ

        rows = list(
            FAQ.objects.filter(is_active=True).values("id", "question", "answer")
        )
        _matcher_cache = _FAQMatcher(rows)
    return _matcher_cache


def invalidate_matcher_cache():
    """Force the next chat request to rebuild the matcher from fresh DB data."""
    global _matcher_cache
    _matcher_cache = None
