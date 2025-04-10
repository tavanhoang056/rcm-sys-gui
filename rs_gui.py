import select
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from rs_helper import *
 

def get_products():
    return pd.read_csv('data/items.csv');

def get_random_products(df):
    return df.head(n=10)

def display_products(df):
    st.write(df)

def display_product_card(product):
    st.write(product)
    with st.container():
        st.markdown("""
        <style>
        .product-card {
            border: 1px solid #2e2e2e;
            padding: 1.5rem;
            border-radius: 10px;
            background-color: #0e1117;
            margin: 10px 0;
            color: white;
        }
        .product-title {
            color: white;
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        .product-info {
            color: #fafafa;
            margin: 5px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                image_url = product['image'].iloc[0]
                if pd.notna(image_url) and image_url.strip() != '':
                    st.image(image_url, width=150)
                else:
                    st.image("data/default-product.jpg", width=150)  # Optional: show a default image
            
            with col2:
                st.markdown(f"<div class='product-title'>{product['product_name'].iloc[0]}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='product-info'><b>Mã sản phẩm:</b> {product['product_id'].iloc[0]}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='product-info'><b>Giá:</b> {product['price'].iloc[0]:,.0f}đ</div>", unsafe_allow_html=True)

                expander = st.expander("Mô tả")
                product_description = product['Content_wt'].iloc[0]
                truncated_description = ' '.join(product_description.split()[:100]) + '...'
                expander.write(truncated_description)
                expander.markdown("Nhấn vào mũi tên để đóng hộp text này.")
            
            st.markdown('</div>', unsafe_allow_html=True)

def select_product(df):
    product_options = [(row['product_id'], row['product_name']) for index, row in df.iterrows()]
    selected_product = st.selectbox(
        "Chọn sản phẩm",
        options=product_options,
        format_func=lambda x: x[1]
    )

    return selected_product[0]

def get_recommendation_products(df, selected_product, select_product_id):
    if not selected_product.empty:
        dictionary, corpus, tfidf, similarity_matrix = load_all_models()
        recommendations_by_id = get_content_based_recommendations(
            query=select_product_id,
            similarity_matrix=similarity_matrix,
            tfidf=tfidf,
            corpus=corpus,
            df=df,
            dictionary=dictionary,
            top_k=5,
            by_keyword=False
        )

        return recommendations_by_id
    else:
        return None
 

def display_recommended_products(df, recommendation_products, selected_product_id):
    if recommendation_products is not None:
        st.write("\nOriginal product:")
        st.write(df[df['product_id'] == selected_product_id][df.columns].iloc[0])
        st.write(df[df['product_id'] == selected_product_id]['product_name'].iloc[0])

        st.write("\nRecommended products:")
        st.write(recommendation_products)
    else:
        st.write(f"Không tìm thấy sản phẩm")

def main():
    # Using menu
    st.title("Recommendation System")

    df_products = get_products();

    df_random_products = get_random_products(df_products);
    display_products(df_random_products)

    selected_product_id = select_product(df_random_products)
    selected_product = df_products[df_products['product_id'] == selected_product_id]

    display_product_card(selected_product)

    recommendation_products_by_id = get_recommendation_products(df_products, selected_product, selected_product_id)
    
    display_recommended_products(df_products, recommendation_products_by_id, selected_product_id)

    # selected_product_keyword = st.text_input("Nhập từ khóa")
    # recommendation_products = get_recommendation_products(df_products, selected_product_keyword)


main()




