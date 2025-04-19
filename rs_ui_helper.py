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
import json
from wordcloud import WordCloud


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
        st.write("Selected User: ", user)


def display_product_card(product):
    if product.empty:
        st.write("ℹ️ Please select a product to view details")
    else:
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
            

            # description = ''
            # if product.description_clean.empty:
            #     description = str(product.description_clean)[:100] + "..."
            # else:
            #     description = "No description available."

            # image = ""
            # if product.image.empty:
            #     image = product.image
            # else:
            #     image = DEFAULT_IMAGE_BASE64

            st.markdown(f"""
            <div class="main-card">
                <img src="{product['image'].iloc[0] if pd.notna(product['image'].iloc[0]) else DEFAULT_IMAGE_BASE64}" 
                    alt="Product Image">
                <div class="main-content">
                    <div class="main-title">{product['product_name'].iloc[0]}</div>
                    <div class="main-price">{product['price'].iloc[0]:,.0f}đ</div>
                    <div class="main-info"><b>Mã sản phẩm:</b> {product['product_id'].iloc[0]}</div>
                    <div class="main-info"><b>Mô tả:</b> {str(product['description_clean'].iloc[0])[:100] + "..." if pd.notna(product['description_clean'].iloc[0]) else "No description available"}</div>
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

                expander = st.expander("Details")
                expander.write(f"Product ID: {product.product_id}")
                if pd.notna(product.description_clean):
                    expander.write(str(product.description_clean[:100] + "..."))
                else:
                    expander.write("No description available.")
                expander.markdown("Click the arrow to close this text box.")   
                
                # st.write(product)


            

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
        st.write("\n**💡 You may also like:** ")
        recommended_products = df[df['product_id'].isin(recommendation_products['product_id'])]
        display_product_cards(recommended_products, cols=3)
    else:
        st.write("⚠️ No products found")


def display_seach_products(df, recommendation_products, keyword):
    if recommendation_products is not None:
        st.write(f"\n**🔎 Search results for '{keyword}':**")
        recommended_products = df[df['product_id'].isin(recommendation_products['product_id'])]
        display_product_cards(recommended_products, cols=3)
    else:
        st.write("⚠️ No products found")


def display_recommended_user(df, recommendation_products):
    if recommendation_products is not None:
        st.write(f"\n**👥 Users also chose:**")
        display_product_cards(recommendation_products, cols=3)
        
    else:
        st.write("⚠️ No products found")
        
def display_box_overview(df_products, df_users):
    
    total_products = df_products['product_id'].nunique()
    total_users = df_users['user_id'].nunique()
    total_ratings = df_users['rating'].count()
    avg_rating = df_users['rating'].mean()
    
    # Custom card CSS
    st.markdown("""
        <style>
        .overview-card {
            padding: 30px 20px;
            border-radius: 20px;
            background: #ffffff;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            text-align: center;
            transition: transform 0.3s ease;
        }
        .overview-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        }
        .overview-icon {
            font-size: 40px;
            color: #4a90e2;
            margin-bottom: 10px;
        }
        .overview-title {
            font-weight: 600;
            color: #6c757d;
            margin-bottom: 5px;
            font-size: 16px;
        }
        .overview-value {
            font-size: 32px;
            font-weight: 700;
            color: #212529;
        }
        </style>
    """, unsafe_allow_html=True)

    # Layout
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="overview-card">
                <div class="overview-icon">📦</div>
                <div class="overview-title">TOTAL PRODUCTS</div>
                <div class="overview-value">{total_products:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="overview-card">
                <div class="overview-icon">👥</div>
                <div class="overview-title">TOTAL USERS</div>
                <div class="overview-value">{total_users:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="overview-card">
                <div class="overview-icon">⭐</div>
                <div class="overview-title">TOTAL RATINGS</div>
                <div class="overview-value">{total_ratings:,}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="overview-card">
                <div class="overview-icon">🌟</div>
                <div class="overview-title">AVERAGE RATING</div>
                <div class="overview-value">{avg_rating:.1f}</div>
            </div>
        """, unsafe_allow_html=True)



def display_model_evaluations(data_list):
    """
    Displays a dynamic, interactive model evaluation table using st.dataframe().
    """
    df = pd.DataFrame(data_list)

    # Simulate merged cells: clear repeated "Method" values
    df["Method"] = df["Method"].mask(df["Method"].duplicated(), "")

    st.markdown("## 📊 Model Evaluations")
    st.dataframe(df, use_container_width=True)
        
    
model_data = [
    {"Method": "Collaborative filtering", "Model": "SVD", "Results": "RMSE = 0.88\ntime = 4 min",
     "Comments": "Performed well after tuning.", "Pros": "Easy to use with sparse data",
     "Cons": "Slower on large datasets"},
    {"Method": f"Collaborative filtering", "Model": "ALS", "Results": "RMSE = 1.14\ntime = 4.1 min",
     "Comments": "Scalable for large datasets", "Pros": "Works with Spark", "Cons": "Lower accuracy"},
    {"Method": "Content-based filtering", "Model": "Gensim", "Results": "Score: 0.2–0.4",
     "Comments": "Semantic similarity", "Pros": "Understands meaning", "Cons": "Needs clean input"},
    {"Method": "Content-based filtering", "Model": "Cosine similarity", "Results": "Score: 0.2–0.4",
     "Comments": "Simple to use", "Pros": "Fast and interpretable", "Cons": "Purely vector-based"},
]


