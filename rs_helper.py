import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from underthesea import word_tokenize, pos_tag, sent_tokenize
from gensim import corpora, models, similarities
import re
from tqdm import tqdm
import streamlit as st

import warnings
warnings.filterwarnings('ignore')

STOP_WORD_FILE = 'data/vietnamese-stopwords.txt'

def getStopWords():
    stop_words = []
    with open(STOP_WORD_FILE, 'r', encoding='utf-8') as file:
        stop_words = file.read()

    stop_words = stop_words.split('\n')
    return stop_words


# Load all saved models
def load_all_models(dict_path='models/gensim_dictionary.dict',
                   corpus_path='models/gensim_corpus.mm',
                   tfidf_path='models/gensim_tfidf.model',
                   sim_matrix_path='models/gensim_similarity.matrix'):
    # Load dictionary
    dictionary = corpora.Dictionary.load(dict_path)
    
    # Load corpus
    corpus = corpora.MmCorpus(corpus_path)
    
    # Load TF-IDF model
    tfidf = models.TfidfModel.load(tfidf_path)
    
    # Load similarity matrix
    similarity_matrix = similarities.SparseMatrixSimilarity.load(sim_matrix_path)
    
    return dictionary, corpus, tfidf, similarity_matrix


def get_similarity_scores(sims, top_k, exclude_idx=None):
    sim_scores = list(enumerate(sims))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    if exclude_idx is not None:
        sim_scores = [s for s in sim_scores if s[0] != exclude_idx]
    
    return sim_scores[:top_k]

def format_recommendations(df, sim_scores):
    product_indices = [i[0] for i in sim_scores]
    recommendations = df.iloc[product_indices][['product_id', 'product_name', 'category', 'sub_category', 'Content_wt']]
    recommendations['similarity_score'] = [i[1] for i in sim_scores]
    return recommendations

def process_keyword_query(query, dictionary, stop_words):
    query = query.lower().strip()
    query_tokens = word_tokenize(query)
    
    query_tokens = [token for token in query_tokens 
                   if token not in stop_words 
                   and len(token) > 1]
    
    if len(query_tokens) == 0:
        raise ValueError("Query too short or contains only stop words")
    
    if len(query_tokens) > 10:
        print("Warning: Long queries may reduce accuracy. Consider using fewer terms.")
    
    query_bow = dictionary.doc2bow(query_tokens)
    if len(query_bow) == 0:
        raise ValueError("No valid keywords found after processing")
        
    return query_bow

def get_content_based_recommendations(query, similarity_matrix, tfidf, corpus, df, dictionary, top_k=5, by_keyword=False):
    if by_keyword:
        query_bow = process_keyword_query(query, dictionary, getStopWords())
        sims = similarity_matrix[tfidf[query_bow]]
        sim_scores = get_similarity_scores(sims, top_k)
    else:
        product_idx = df[df['product_id'] == query].index[0]
        doc_vector = corpus[product_idx]
        sims = similarity_matrix[tfidf[doc_vector]]
        sim_scores = get_similarity_scores(sims, top_k, exclude_idx=product_idx)
    
    return format_recommendations(df, sim_scores)