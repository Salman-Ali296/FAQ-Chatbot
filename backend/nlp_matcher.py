"""
nlp_matcher.py

Core NLP engine for the FAQ chatbot.

Pipeline:
1. Preprocess text with NLTK — lowercase, tokenize, strip punctuation/stopwords,
   lemmatize each token back to its root form.
2. Vectorize every FAQ question with TF-IDF (fit once at startup).
3. On each user query: preprocess it the same way, vectorize it, and compute
   cosine similarity against every FAQ question vector.
4. Return the best-matching FAQ's answer, or a fallback message if nothing
   clears the similarity threshold.
"""

"""
nlp_matcher.py - Core NLP engine for the FAQ chatbot
"""

import json
import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def ensure_nltk_data():
    """Download required NLTK corpora if they aren't already present."""
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


class FAQMatcher:
    """Loads FAQ dataset and matches user queries to it."""

    SIMILARITY_THRESHOLD = 0.20

    # Greeting patterns to detect
    GREETING_PATTERNS = [
        r'\b(hi|hello|hey|howdy|greetings|sup|yo|hola|namaste|salam|assalamualaikum|good morning|good afternoon|good evening)\b',
        r'^h(i|ello|ey)$',
        r'^hey there$',
        r'^what\'?s up$',
        r'^how are you$',
        r'^how\'?s it going$',
        r'^nice to meet you$',
        r'^good to see you$',
    ]

    # Help/confusion patterns
    HELP_PATTERNS = [
        r'\b(help|confused|don\'?t understand|not sure|lost|stuck)\b',
        r'\b(what should i|what do i|how do i|i need help)\b',
        r'^\?$',
        r'^i don\'?t know$',
        r'^not sure$',
    ]

    # Thank you patterns
    THANK_YOU_PATTERNS = [
        r'\b(thank|thanks|thank you|thx|ty|appreciate|grateful)\b',
        r'^thanks$',
        r'^thank you$',
    ]

    # Goodbye patterns
    GOODBYE_PATTERNS = [
        r'\b(bye|goodbye|see you|cya|later|peace|take care|farewell)\b',
        r'^bye$',
        r'^goodbye$',
    ]

    def __init__(self, faqs_path):
        ensure_nltk_data()

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words("english"))
        self.punctuation_table = str.maketrans("", "", string.punctuation)

        with open(faqs_path, "r", encoding="utf-8") as f:
            self.faqs = json.load(f)

        self.questions = [faq["question"] for faq in self.faqs]
        self.preprocessed_questions = [self._preprocess(q) for q in self.questions]

        self.vectorizer = TfidfVectorizer()
        self.question_vectors = self.vectorizer.fit_transform(self.preprocessed_questions)

    def _preprocess(self, text):
        """Clean + tokenize + remove stopwords + lemmatize text."""
        text = text.lower().translate(self.punctuation_table)
        tokens = word_tokenize(text)
        cleaned = [
            self.lemmatizer.lemmatize(tok)
            for tok in tokens
            if tok not in self.stop_words and tok.isalpha()
        ]
        return " ".join(cleaned)

    def _detect_intent(self, text):
        """Detect if the user is greeting, thanking, saying goodbye, or asking for help."""
        text_lower = text.lower().strip()
        
        # Check for greetings
        for pattern in self.GREETING_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "greeting"
        
        # Check for thank you
        for pattern in self.THANK_YOU_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "thankyou"
        
        # Check for goodbye
        for pattern in self.GOODBYE_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "goodbye"
        
        # Check for help
        for pattern in self.HELP_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "help"
        
        return "question"

    def _get_greeting_response(self):
        """Return a friendly greeting response."""
        greetings = [
            "Hello! 👋 Welcome to Tech Deal Store! How can I help you today?",
            "Hi there! 😊 Great to see you! What can I assist you with?",
            "Hey! 🌟 Welcome! Feel free to ask me anything about our products, shipping, returns, or payments.",
            "Assalamualaikum! 👋 Welcome to Tech Deal Store! How may I help you?",
            "Hello! 🎉 I'm here to help! You can ask me about orders, shipping, returns, payments, or your account.",
            "Hi! 😄 Thanks for reaching out! What brings you here today?",
        ]
        import random
        return random.choice(greetings)

    def _get_thankyou_response(self):
        """Return a response for thank you messages."""
        responses = [
            "You're welcome! 😊 Happy to help! Is there anything else I can assist you with?",
            "My pleasure! 🌟 If you need anything else, just let me know!",
            "Anytime! 🎉 Feel free to ask if you have more questions!",
            "Glad I could help! 😄 Have a great day!",
            "You're welcome! 💫 Don't hesitate to reach out if you need more help!",
        ]
        import random
        return random.choice(responses)

    def _get_goodbye_response(self):
        """Return a response for goodbye messages."""
        responses = [
            "Goodbye! 👋 Thanks for visiting Tech Deal Store! Have a great day!",
            "See you later! 🌟 Come back anytime if you have more questions!",
            "Take care! 😊 We hope to see you again soon!",
            "Bye! 🎉 Happy shopping! Feel free to reach out anytime!",
            "Farewell! 👋 Don't forget to check out our latest deals!",
        ]
        import random
        return random.choice(responses)

    def _get_help_response(self):
        """Return a helpful response for confused users."""
        responses = [
            "I'm here to help! 😊 You can ask me about:\n• Orders & Shipping\n• Returns & Refunds\n• Payment Methods\n• Account Issues\n• Product Warranty\n• Tech Support\n\nJust type your question and I'll do my best to help!",
            "No worries! 🌟 I can help you with:\n• Tracking your order\n• Returning a product\n• Resetting your password\n• Finding the right product\n• Payment options\n\nWhat would you like to know?",
            "I understand! 🎉 Let me help you. Here are some things I can assist with:\n• Order status and tracking\n• Return policy\n• Payment methods\n• Account management\n• Product questions\n\nJust ask me anything!",
        ]
        import random
        return random.choice(responses)

    def _get_fallback_response(self):
        """Return a friendly fallback response when no match is found."""
        fallbacks = [
            "I'm not quite sure I understand. 🤔 Could you try rephrasing your question? I can help with orders, shipping, returns, payments, and account issues.",
            "Hmm, I didn't quite catch that. 😊 Let me try to help! Feel free to ask about:\n• Order tracking\n• Returns and refunds\n• Payment methods\n• Account help\n• Product questions",
            "I'm not sure I understood that. 🤗 Here are some common topics I can help with:\n• Shipping & Delivery\n• Returns & Exchanges\n• Payment Options\n• Warranty Information\n• Account Support\n\nWhat would you like to know more about?",
            "Let me try to help! 🌟 I'm best at answering questions about orders, shipping, returns, payments, and your account. Could you please rephrase your question?",
        ]
        import random
        return random.choice(fallbacks)

    def find_best_match(self, user_query):
        """
        Returns dict with matched question, answer, and confidence score,
        or fallback response if no FAQ clears the similarity threshold.
        """
        user_query = user_query.strip()
        
        if not user_query:
            return {
                "matched": False,
                "answer": "Could you please type your question? 😊 I'm here to help!",
                "matched_question": None,
                "score": 0.0,
            }

        # Detect intent first
        intent = self._detect_intent(user_query)
        
        # Handle greetings
        if intent == "greeting":
            return {
                "matched": False,
                "answer": self._get_greeting_response(),
                "matched_question": None,
                "score": 1.0,
                "intent": "greeting"
            }
        
        # Handle thank you
        if intent == "thankyou":
            return {
                "matched": False,
                "answer": self._get_thankyou_response(),
                "matched_question": None,
                "score": 1.0,
                "intent": "thankyou"
            }
        
        # Handle goodbye
        if intent == "goodbye":
            return {
                "matched": False,
                "answer": self._get_goodbye_response(),
                "matched_question": None,
                "score": 1.0,
                "intent": "goodbye"
            }
        
        # Handle help requests
        if intent == "help":
            return {
                "matched": False,
                "answer": self._get_help_response(),
                "matched_question": None,
                "score": 0.8,
                "intent": "help"
            }

        # Process as a question using NLP
        cleaned_query = self._preprocess(user_query)

        if not cleaned_query.strip():
            return {
                "matched": False,
                "answer": "Could you rephrase that? I didn't catch a clear question. 😊",
                "matched_question": None,
                "score": 0.0,
            }

        query_vector = self.vectorizer.transform([cleaned_query])
        scores = cosine_similarity(query_vector, self.question_vectors)[0]

        best_index = scores.argmax()
        best_score = float(scores[best_index])

        if best_score < self.SIMILARITY_THRESHOLD:
            return {
                "matched": False,
                "answer": self._get_fallback_response(),
                "matched_question": None,
                "score": round(best_score, 3),
                "intent": "fallback"
            }

        matched_faq = self.faqs[best_index]
        return {
            "matched": True,
            "answer": matched_faq["answer"],
            "matched_question": matched_faq["question"],
            "score": round(best_score, 3),
            "intent": "faq"
        }

    def list_faqs(self):
        return self.faqs