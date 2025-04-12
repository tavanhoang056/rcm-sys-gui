import streamlit as st
import pandas as pd
from rs_helper import *
from rs_ui_helper import *
from streamlit_option_menu import option_menu

def get_products():
    return pd.read_csv('data/items.csv');

def get_users():
    return pd.read_csv('data/ratings.csv');

def get_random_products(df):
    return df.sample(n=10)

def get_random_users(df):
    return df.sample(n=10)

def display_products(df):
    st.write(df)

def display_users(df):
    st.write(df)

def select_product(df):
    st.write('\n\n')
    st.markdown("#### 2️⃣ Select Product")
    product_options = [('none', '📋 Select a product')] + [(row['product_id'], row['product_name']) for index, row in df.iterrows()]
    selected_product = st.selectbox(
        "🛒Select Product",
        options=product_options,
        format_func=lambda x: x[1],
        index=0  # Set default to first option (none)
    )
    return selected_product[0]

def select_user(df):
    st.write('\n\n')
    st.markdown("#### 1️⃣ Select User")
    user_options = [(0, 'guest')] + [(row['user_id'], row['user_name']) for index, row in df.iterrows()]
    selected_user = st.selectbox(
        "👤Select User",
        options=user_options,
        format_func=lambda x: '🧑 Guest' if x[1] == 'guest' else x[1],
        index=0  # Set default to first option (guest)
    )
    return selected_user[0]

def search_products():
    st.write('\n\n')
    st.markdown("#### 3️⃣ Search Products")
    return st.text_input("🔍 Enter search keywords")

def get_recommendation_products_by_user(user_id, df_products, df_users, selected_user):
    # st.write(selected_user)
    if not selected_user.empty:
        recommendations = get_collaborative_filtering_recommendations(
            user_id=user_id,
            df_products=df_products,
            df_users=df_users,
            top_k=3
        )
        return recommendations
    else:
        return None

def get_recommendation_products_by_id(id, df, selected_product):
    if not selected_product.empty:
        recommendations = get_content_based_recommendations_by_id(
            id=id,
            df=df,
            top_k=6
        )
        return recommendations
    else:
        return None

def get_recommendation_products_by_keyword(keyword, df):
    if keyword and keyword.strip():
        recommendations = get_content_based_recommendations_by_keyword(
            keyword=keyword,
            df=df,
            top_k=6
        )
        return recommendations
    else:
        return None
 
def display_project_overview():
    st.subheader("Business Objective")
    
    st.markdown("🌟 **Shopee** is an 'all-in-one' e-commerce ecosystem and a leading platform in Southeast Asia. Among its services, **``shopee.vn``** is one of the top e-commerce websites in Vietnam.")
    st.image('data/shopee.png')
    st.markdown("🔑 Challenge: Shopee hasn’t rolled out a Recommender System yet – how would you build one to revolutionize their platform?")
    st.markdown("🎯 **Goal**: Create a system that delivers personalized product suggestions to delight every user!")
    tab1, tab2, tab3, tab4 = st.tabs(['Methodology', 'Data Exploration', 'Gensim Model', 'Surprise SVD Model'])


    df_products = get_products();
    if 'random_products' not in st.session_state:
        st.session_state.random_products = get_random_products(df_products);

    with tab1:
        st.write("#### Content-based Filtering using Cosine Similarity (Gensim Model)")
        st.image('data/rs-cbf.png')
        st.write("#### Collaborative Filtering")
        st.image('data/rs-cf.png')

    with tab2:
        st.write("#### Dataset")
        display_products(st.session_state.random_products)
        st.write("#### Charts")
        st.write("##### Top Words")
        st.image('data/keyword-wordcloud.png')
        st.write("##### Top Products")
        st.image('data/rs-products.png')
        st.write("##### Top Ratings")
        st.image('data/rs-ratings.png')
        st.write("##### Top Prices")
        st.image('data/rs-prices.png')
        st.write("##### Most and Least")
        st.image('data/rs-most.png')
        st.image('data/rs-least.png')
    with tab3:
        st.write("#### Charts")
        st.image('data/rs-gensim-chart.png')
        st.write("#### Recommendation by ID")
        st.image('data/rs-gensim-id.png')
        st.write("#### Recommendation by Keyword")
        st.image('data/rs-gensim-keyword.png')
    with tab4:
        st.write("#### Recommendation for User")
        st.image('data/rs-svd.png')

def display_recommendation_app():
    st.subheader('🌟 Welcome to our product — we invite you to explore and enjoy the experience!')
    st.image('data/shopee-banner.jpg')
    df_products = get_products();
    if 'random_products' not in st.session_state:
        st.session_state.random_products = get_random_products(df_products);

    df_users = get_users()
    if 'random_users' not in st.session_state:
        st.session_state.random_users = get_random_users(df_users);
    # display_users(st.session_state.random_users)

    selected_user_id = select_user(st.session_state.random_users)
    selected_user = pd.DataFrame() if selected_user_id == 'guest' else df_users[df_users['user_id'] == selected_user_id]
    # display_user_card(selected_user)

    recommendation_products_by_user = get_recommendation_products_by_user(selected_user_id, df_products, df_users, selected_user)
    display_recommended_user(df_users, recommendation_products_by_user)

    selected_product_id = select_product(st.session_state.random_products)
    selected_product = pd.DataFrame() if selected_product_id == 'none' else df_products[df_products['product_id'] == selected_product_id]

    display_product_card(selected_product)

    recommendation_products_by_id = get_recommendation_products_by_id(selected_product_id, df_products, selected_product)
    display_recommended_products(df_products, recommendation_products_by_id)

    search_product_keyword = search_products()
    recommendation_products_by_keyword = get_recommendation_products_by_keyword(search_product_keyword, df_products)
    display_seach_products(df_products, recommendation_products_by_keyword, search_product_keyword)


def display_sidebar():
    # Sidebar menu
    with st.sidebar:
        choice = option_menu(
            menu_title=None,  # No title
            options=["Project Overview", "Recommendation App"],
            # icons=["house", "bi bi-bar-chart", "list-task", "search", "info-circle"],
            icons = ['house', 'list-task'],
            default_index=0,  # Default to "Kết Quả"
            orientation="vertical",
            styles={
                "container": {"padding": "10px", "background-color": "#0f0f0f", "border-radius": "10px"},
                "icon": {"color": "white", "font-size": "18px"},
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "color": "#fff",
                    "padding": "10px 15px",
                    "border-radius": "6px"
                },
                "nav-link-selected": {
                    "background-color": "#FF4B4B",  # This is the red highlight
                    "color": "white"
                }
            }
        )
        
    # Footer
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 16px; line-height: 1.5;'>
            Made by <b>Tran T. Kim Phung & Ta Van Hoang</b><br>
            Instructed by <b>Khuat Thuy Phuong</b> ❤️ <br>
            April 2025
        </div>
        """,
        unsafe_allow_html=True
    )

    if choice == 'Project Overview':
        display_project_overview()
    elif choice == 'Recommendation App':
        display_recommendation_app()


def main():
    st.set_page_config(
        page_title='Shopee Recommendation System',
        # layout='wide',
        initial_sidebar_state='expanded'
    )

    st.title("💡🛍️ Shopee Recommendation System")
    display_sidebar()

main()




