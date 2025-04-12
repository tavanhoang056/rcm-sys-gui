import numpy as np
import pandas as pd
from underthesea import word_tokenize, pos_tag, sent_tokenize
from gensim import corpora, models, similarities
import streamlit as st
import pickle

import warnings
warnings.filterwarnings('ignore')

STOP_WORD_FILE = 'data/vietnamese-stopwords.txt'

def getStopWords():
    stop_words = []
    with open(STOP_WORD_FILE, 'r', encoding='utf-8') as file:
        stop_words = file.read()

    stop_words = stop_words.split('\n')
    return stop_words

stop_words = getStopWords()

def load_all_models(dict_path='models/gensim_dictionary.dict',
                   corpus_path='models/gensim_corpus.mm',
                   tfidf_path='models/gensim_tfidf.model',
                   sim_matrix_path='models/gensim_similarity.matrix',
                   svd_path='models/best_svd_model.pkl'):
    # Load dictionary
    dictionary = corpora.Dictionary.load(dict_path)
    
    # Load corpus
    corpus = corpora.MmCorpus(corpus_path)
    
    # Load TF-IDF model
    tfidf = models.TfidfModel.load(tfidf_path)
    
    # Load similarity matrix
    similarity_matrix = similarities.SparseMatrixSimilarity.load(sim_matrix_path)

    # Load SVD model
    with open(svd_path, "rb") as f:
        svd_model = pickle.load(f)
    
    return dictionary, corpus, tfidf, similarity_matrix, svd_model

dictionary, corpus, tfidf, similarity_matrix, svd_model = load_all_models()

def get_similarity_scores(sims, top_k, exclude_idx=None):
    sim_scores = list(enumerate(sims))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    if exclude_idx is not None:
        sim_scores = [s for s in sim_scores if s[0] != exclude_idx]
    
    return sim_scores[:top_k]

def format_recommendations(df, sim_scores):
    product_indices = [i[0] for i in sim_scores]
    recommendations = df.iloc[product_indices][['product_id', 'product_name', 'category', 'sub_category', 'description_clean', 'Content_wt']]
    recommendations['similarity_score'] = [i[1] for i in sim_scores]
    return recommendations

def process_keyword_query(query, dictionary, stop_words):
    query = query.lower().strip()
    query_tokens = word_tokenize(query)
    
    query_tokens = [token for token in query_tokens 
                   if token not in stop_words 
                   and len(token) > 1]
    
    if len(query_tokens) == 0:
        st.write("⚠️ Oops! Your search is too short. Try using more words!")
        return None
    
    if len(query_tokens) > 10:
        st.write("⚠️ Oops! Your search is too long and might not work well. Try using fewer words!")
        return None
    
    query_bow = dictionary.doc2bow(query_tokens)
    if len(query_bow) == 0:
        st.write("⚠️ Oops! We couldn’t find any useful words in your search. Try different words!")
        return None
        
    return query_bow

def get_content_based_recommendations_by_id(id, df, top_k=5):
    product_idx = df[df['product_id'] == id].index[0]
    doc_vector = corpus[product_idx]
    sims = similarity_matrix[tfidf[doc_vector]]
    sim_scores = get_similarity_scores(sims, top_k, exclude_idx=product_idx)
    return format_recommendations(df, sim_scores)

def get_content_based_recommendations_by_keyword(keyword, df, top_k=5):
    query_bow = process_keyword_query(keyword, dictionary, stop_words)
    if query_bow is None:
        return None
    sims = similarity_matrix[tfidf[query_bow]]
    sim_scores = get_similarity_scores(sims, top_k)
    return format_recommendations(df, sim_scores)


def get_collaborative_filtering_recommendations(user_id, df_products, df_users, top_k=5):
    """
    Recommend top_k similar products for a user based on a selected product
    
    Args:
        user_id: ID of the user
        df_products: DataFrame containing all product details
        df: DataFrame containing user-item interactions
        top_k: Number of recommendations to return
        
    Returns:
        DataFrame containing recommended products with their details
    """
    # Get all unique product IDs from your dataset
    all_products = df_users['product_id'].unique()

    # Get predictions for all products for this user
    predictions = []
    for pid in all_products:
        try:
            pred = svd_model.predict(uid=str(user_id), iid=str(pid))
            predictions.append((pid, pred.est))
        except:
            continue
    
    # Sort by predicted rating and get top k
    predictions.sort(key=lambda x: x[1], reverse=True)

    # Filter out the input product and get top k product IDs
    recommended_ids = [p[0] for p in predictions][:top_k]
    
    # Get the full product details from df_products
    recommendations = df_products[df_products['product_id'].isin(recommended_ids)]
    
    return recommendations
