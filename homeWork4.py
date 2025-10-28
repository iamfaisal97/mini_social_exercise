import sqlite3
import pandas as pd
import gensim
import nltk
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download required NLTK data
nltk.download('wordnet')
nltk.download('vader_lexicon')

# ----------------------------
# Task 4.1: Topic Modeling (LDA)
# ----------------------------

# Connect to the database
conn = sqlite3.connect('database.sqlite')

# Load posts
posts_df = pd.read_sql_query("SELECT content FROM posts", conn)

# Text preprocessing function
lemmatizer = WordNetLemmatizer()
def preprocess(text):
    tokens = simple_preprocess(text, deacc=True)
    tokens = [lemmatizer.lemmatize(t) for t in tokens if t not in STOPWORDS]
    return tokens

posts_df['tokens'] = posts_df['content'].apply(preprocess)

# Create dictionary and corpus
dictionary = gensim.corpora.Dictionary(posts_df['tokens'])
dictionary.filter_extremes(no_below=1, no_above=0.5)
corpus = [dictionary.doc2bow(text) for text in posts_df['tokens']]

# Train LDA model
lda_model = gensim.models.LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=10,
    random_state=42,
    passes=10,
    alpha='auto',
    per_word_topics=True
)

# Print topics without weights
print("=== LDA Topics ===")
for i, topic in lda_model.show_topics(formatted=False, num_topics=10, num_words=10):
    words = [word for word, _ in topic]
    print(f"Topic {i}: {', '.join(words)}")

# Function to get dominant topic
def get_dominant_topic(bow):
    topics = lda_model.get_document_topics(bow)
    if topics:
        return max(topics, key=lambda x: x[1])[0]
    else:
        return None

posts_df['topic'] = [get_dominant_topic(bow) for bow in corpus]

# ----------------------------
# Task 4.2: Sentiment Analysis
# ----------------------------

# Load comments
comments_df = pd.read_sql_query("SELECT content FROM comments", conn)

# Initialize VADER
sia = SentimentIntensityAnalyzer()

# Function to compute compound sentiment
def get_sentiment(text):
    return sia.polarity_scores(str(text))['compound']

posts_df['sentiment'] = posts_df['content'].apply(get_sentiment)
comments_df['sentiment'] = comments_df['content'].apply(get_sentiment)

# Classify sentiment
def get_sentiment_label(score):
    if score >= 0.05:
        return 'positive'
    elif score <= -0.05:
        return 'negative'
    else:
        return 'neutral'

posts_df['sentiment_label'] = posts_df['sentiment'].apply(get_sentiment_label)
comments_df['sentiment_label'] = comments_df['sentiment'].apply(get_sentiment_label)

# Calculate percentages
post_percent = posts_df['sentiment_label'].value_counts(normalize=True) * 100
comment_percent = comments_df['sentiment_label'].value_counts(normalize=True) * 100

print("\n=== Sentiment Percentages ===")
print("Posts sentiment %:\n", post_percent)
print("Comments sentiment %:\n", comment_percent)

# Overall sentiment scores
overall_posts_sentiment = posts_df['sentiment'].mean()
overall_comments_sentiment = comments_df['sentiment'].mean()

print("\n=== Overall Sentiment ===")
print("Overall posts sentiment:", overall_posts_sentiment)
print("Overall comments sentiment:", overall_comments_sentiment)

# Average sentiment per topic
sentiment_by_topic = posts_df.groupby('topic')['sentiment'].mean()
print("\n=== Average Sentiment by Topic ===")
print(sentiment_by_topic)
