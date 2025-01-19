import nltk
import pyLDAvis.gensim_models
from gensim import corpora, models
from gensim.models import CoherenceModel
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

# Download NLTK resources if not already present
nltk.download("punkt_tab")
nltk.download("stopwords")

# Sample documents (replace with your own data)
documents = [
    "This is the first document.",
    "This document is the second document.",
    "And this is the third one.",
    "Is this the first document?",
]

# Text Preprocessing
tokenized_docs = [
    [word for word in nltk.word_tokenize(doc.lower())] for doc in documents
]
stop_words = set(stopwords.words("english"))
tokenized_docs = [
    [word for word in doc if word not in stop_words] for doc in tokenized_docs
]

# Optional: Stemming
stemmer = PorterStemmer()
tokenized_docs = [
    [stemmer.stem(word) for word in doc] for doc in tokenized_docs
]

# Create Dictionary and Corpus
dictionary = corpora.Dictionary(tokenized_docs)
corpus = [dictionary.doc2bow(doc) for doc in tokenized_docs]

# Build LDA Model
lda_model = models.LdaMulticore(
    corpus=corpus,
    id2word=dictionary,
    num_topics=2,  # Choose the number of topics
    passes=10,
    workers=2,
)

# Print Topics
for idx, topic in lda_model.print_topics(-1):
    print(f"Topic: {idx} \nWords: {topic}")

# Visualize Topics
vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary)
pyLDAvis.display(vis)

# Evaluate Model (Optional)
coherence_model_lda = CoherenceModel(
    model=lda_model,
    texts=tokenized_docs,
    dictionary=dictionary,
    coherence="c_v",
)
coherence_lda = coherence_model_lda.get_coherence()
print(f"Coherence Score: {coherence_lda}")

# Assign Documents to Topics
for i, doc in enumerate(corpus):
    topic_dist = lda_model.get_document_topics(doc)
    dominant_topic = max(topic_dist, key=lambda x: x[1])
    print(f"Document {i}: Dominant Topic - {dominant_topic[0]}")
