import select
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from rs_helper import *
import os
from PIL import Image
import base64
import io

def get_image_as_base64(image_path):
    img = Image.open(image_path)
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Get the directory containing the current script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_IMAGE_PATH = os.path.join(CURRENT_DIR, "data", "default-product.jpg")
DEFAULT_IMAGE_BASE64 = f"data:image/png;base64,{get_image_as_base64(DEFAULT_IMAGE_PATH)}"


def display_user_card(user):
    with st.container():
        st.write("Bạn chọn User: ", user)


def display_product_card(product):
    with st.container():
        st.markdown("""
        <style>
        .main-card {
            background-color: #1E1E1E;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            color: white;
            display: flex;
            align-items: start;
            gap: 20px;
        }
        .main-card img {
            width: 300px;
            height: 300px;
            object-fit: cover;
            border-radius: 4px;
        }
        .main-content {
            flex: 1;
        }
        .main-title {
            font-size: 24px;
            color: white;
            margin: 10px 0;
            font-weight: bold;
        }
        .main-price {
            color: #00CA4E;
            font-weight: bold;
            font-size: 20px;
            margin: 10px 0;
        }
        .main-info {
            color: #fafafa;
            margin: 8px 0;
            font-size: 16px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="main-card">
            <img src="{product['image'].iloc[0] if pd.notna(product['image'].iloc[0]) else DEFAULT_IMAGE_BASE64}" 
                 alt="Product Image">
            <div class="main-content">
                <div class="main-title">{product['product_name'].iloc[0]}</div>
                <div class="main-price">{product['price'].iloc[0]:,.0f}đ</div>
                <div class="main-info"><b>Mã sản phẩm:</b> {product['product_id'].iloc[0]}</div>
                <div class="main-info"><b>Mô tả:</b> {product['Content_wt'].iloc[0][:100]}...</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def display_product_cards(products, cols=4):
    with st.container():
        st.markdown("""
        <style>
        .simple-card {
            background-color: #1E1E1E;
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
            text-align: center;
            height: 280px;  /* Fixed height for the card */
            display: flex;
            flex-direction: column;
        }
        .card-title {
            font-size: 14px;
            color: white;
            margin: 8px 0;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            height: 42px;  /* Fixed height for 2 lines of text */
            line-height: 1.5;
        }
        .card-price {
            color: #00CA4E;
            font-weight: bold;
            margin: 5px 0;
        }
        </style>
        """, unsafe_allow_html=True)
        
    columns = st.columns(cols)
    for idx, product in enumerate(products.itertuples()):
        with columns[idx % cols]:
            with st.container():
                st.markdown(f"""
                <div class="simple-card">
                    <img src="{product.image if pd.notna(product.image) else DEFAULT_IMAGE_BASE64}" 
                         style="width: 100%; height: 150px; object-fit: cover; border-radius: 4px;">
                    <div class="card-title">{product.product_name}</div>
                    <div class="card-price">{product.price:,.0f}đ</div>
                </div>
                """, unsafe_allow_html=True)

                expander = st.expander(f"Chi tiết")
                expander.write(f"Mã SP: {product.product_id}")
                expander.write(product.Content_wt[:100] + "...")
                expander.markdown("Nhấn vào mũi tên để đóng hộp text này.")       
            

def display_product_by_users_cards(products, cols=4):
    st.markdown("""
        <style>
        div[data-testid="stHorizontalBlock"] {
            overflow-x: auto;
            white-space: nowrap;
            display: flex;
            gap: 1rem;
            padding: 1rem 0;
        }
        div[data-testid="column"] {
            flex: 0 0 200px !important;
            min-width: 200px !important;
        }
        .scroll-card {
            background-color: #1E1E1E;
            border-radius: 8px;
            padding: 10px;
            margin: 5px;
            text-align: center;
            height: 280px;
            display: flex;
            flex-direction: column;
        }
        .scroll-card img {
            width: 100%;
            height: 150px;
            object-fit: cover;
            border-radius: 4px;
        }
        .scroll-title {
            font-size: 14px;
            color: white;
            margin: 8px 0;
            overflow: hidden;
            text-overflow: ellipsis;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            height: 42px;
            line-height: 1.5;
        }
        .scroll-price {
            color: #00CA4E;
            font-weight: bold;
            margin: 5px 0;
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(len(products))
    for idx, product in enumerate(products.itertuples()):
        with cols[idx]:
            st.markdown(f"""
                <div class="scroll-card">
                    <img src="{product.image if pd.notna(product.image) else DEFAULT_IMAGE_BASE64}">
                    <div class="scroll-title">{product.product_name}</div>
                    <div class="scroll-price">{product.price:,.0f}đ</div>
                </div>
            """, unsafe_allow_html=True)

def display_recommended_products(df, recommendation_products):
    if recommendation_products is not None:
        st.write("\n**Có thể bạn cũng thích:** ")
        recommended_products = df[df['product_id'].isin(recommendation_products['product_id'])]
        display_product_cards(recommended_products, cols=3)
    else:
        st.write(f"Không tìm thấy sản phẩm")


def display_seach_products(df, recommendation_products, keyword):
    if recommendation_products is not None:
        st.write(f"\n**Kết quả tìm kiếm cho '{keyword}:'**")
        recommended_products = df[df['product_id'].isin(recommendation_products['product_id'])]
        display_product_cards(recommended_products, cols=3)
    else:
        st.write(f"Không tìm thấy sản phẩm")


def display_recommended_user(df, recommendation_products):
    if recommendation_products is not None:
        st.write(f"\n**Người dùng cũng chọn:**")
        display_product_cards(recommendation_products, cols=3)
        
    else:
        st.write(f"Không tìm thấy sản phẩm")

